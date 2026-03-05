"""LangGraph node implementations for the investigation agent."""

from __future__ import annotations

import json
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agent.prompts import build_system_prompt, PLAN_PROMPT
from app.agent.state import AgentState
from app.agent import policy
from app.agent import executor as action_executor
from app.core.config import settings
from app.schemas.agent import AgentPlan
from app.tools.registry import TOOL_MAP, INVESTIGATION_TOOLS


# ── LLMs ───────────────────────────────────────────────────────────────

def _get_llm():
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )


def _get_llm_with_tools():
    return _get_llm().bind_tools(INVESTIGATION_TOOLS)


def _get_structured_llm():
    return _get_llm().with_structured_output(AgentPlan)


# ── Node 1: gather_context ─────────────────────────────────────────────

async def gather_context(state: AgentState) -> dict:
    """Assemble context from DB and context tools (no LLM call)."""
    from app.db.engine import async_session
    from app.services import incident_service as svc

    incident = state["incident"]
    inc_id = incident.get("id", "")

    async with async_session() as db:
        timeline = await svc.get_recent_events(db, inc_id, limit=15)

    # Call context tools directly
    topology_result = await TOOL_MAP["get_topology"].execute(
        {"service": incident.get("service", "")}
    )
    kb_result = await TOOL_MAP["search_wiki"].execute(
        {"query": incident.get("title", "")}
    )
    contacts_result = await TOOL_MAP["get_contacts"].execute(
        {"service": incident.get("service", "")}
    )

    topology = topology_result.data
    kb_snippets = kb_result.data.get("results", [])
    contacts = contacts_result.data

    hint = state.get("hint", "")
    system_content = build_system_prompt(
        incident, timeline, topology, kb_snippets, contacts, hint=hint
    )

    return {
        "timeline": timeline,
        "topology": topology,
        "kb_snippets": kb_snippets,
        "contacts": contacts,
        "messages": [
            SystemMessage(content=system_content),
            HumanMessage(content=(
                "Analyze this incident. Use the available tools to gather evidence "
                "about the root cause. When you have enough evidence, stop calling tools."
            )),
        ],
    }


# ── Node 2: investigate ────────────────────────────────────────────────

async def investigate(state: AgentState) -> dict:
    """LLM call with investigation tools bound."""
    llm = _get_llm_with_tools()
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


# ── Node 3: execute_tools ──────────────────────────────────────────────

async def execute_tools(state: AgentState) -> dict:
    """Execute tool calls from the LLM response."""
    last_msg = state["messages"][-1]
    results = []
    evidence = list(state.get("evidence", []))

    for tc in last_msg.tool_calls:
        tool_name = tc["name"]
        tool_args = tc["args"]
        tool = TOOL_MAP.get(tool_name)

        if tool:
            result = await tool.execute(tool_args)
            result_str = json.dumps(result.data, default=str)
            results.append(ToolMessage(content=result_str, tool_call_id=tc["id"]))
            evidence.append({
                "tool": tool_name,
                "params": tool_args,
                "finding": result_str[:500],
            })
        else:
            results.append(ToolMessage(
                content=json.dumps({"error": f"Unknown tool: {tool_name}"}),
                tool_call_id=tc["id"],
            ))

    return {"messages": results, "evidence": evidence}


# ── Node 4: produce_plan ───────────────────────────────────────────────

async def produce_plan(state: AgentState) -> dict:
    """Produce final structured plan via with_structured_output."""
    llm = _get_structured_llm()
    msgs = list(state["messages"]) + [HumanMessage(content=PLAN_PROMPT)]
    plan: AgentPlan = await llm.ainvoke(msgs)
    return {"plan": plan.model_dump()}


# ── Node 5: execute_actions ────────────────────────────────────────────

async def execute_actions(state: AgentState) -> dict:
    """Policy-validate and execute planned actions."""
    from app.db.engine import async_session

    plan = state.get("plan", {})
    if not plan:
        return {"events_created": []}

    events = []
    async with async_session() as db:
        incident_id = state["incident"]["id"]

        # Save the agent plan as a timeline event
        plan_event = await _save_plan_event(db, incident_id, state)
        events.append(plan_event)

        # Execute each action
        for action in plan.get("actions", []):
            verdict = policy.validate_action(action)
            if verdict == "execute":
                evt = await action_executor.execute_action(db, incident_id, action)
                events.append(evt)
            elif verdict == "needs_approval":
                from app.services import incident_service as svc
                evt = await svc.add_event(
                    db, incident_id=incident_id, kind="action_exec", actor="agent",
                    summary=f"Action needs approval: {action.get('type', '')}",
                    data={**action, "status": "needs_approval"},
                )
                events.append(evt)
            else:
                from app.services import incident_service as svc
                evt = await svc.add_event(
                    db, incident_id=incident_id, kind="action_exec", actor="agent",
                    summary=f"Action rejected: {action.get('type', '')}",
                    data={**action, "status": "rejected"},
                )
                events.append(evt)

        # Update incident summary and severity
        from app.services import incident_service as svc
        await svc.update_incident(
            db, incident_id,
            summary=plan.get("summary", ""),
            severity=plan.get("severity", "medium"),
            status="investigating",
        )

    return {"events_created": events}


async def _save_plan_event(db, incident_id: str, state: AgentState) -> dict:
    """Save the agent's plan as a timeline event."""
    from app.services import incident_service as svc
    plan = state.get("plan", {})
    step = state.get("step_number", 1)
    return await svc.add_event(
        db, incident_id=incident_id, kind="agent_plan", actor="agent",
        summary=f"Agent Step #{step}: {plan.get('summary', '')[:100]}",
        data=plan,
    )


# ── Routing ────────────────────────────────────────────────────────────

def should_continue_investigating(state: AgentState) -> str:
    """After LLM responds, check if it wants more tools or is done."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "plan"
