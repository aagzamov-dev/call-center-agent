"""LangGraph StateGraph definition — the compiled agent graph."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    execute_actions,
    execute_tools,
    gather_context,
    investigate,
    produce_plan,
    should_continue_investigating,
)
from app.agent.state import AgentState

# ── Build graph ────────────────────────────────────────────────────────

_graph = StateGraph(AgentState)

_graph.add_node("gather", gather_context)
_graph.add_node("investigate", investigate)
_graph.add_node("tools", execute_tools)
_graph.add_node("plan", produce_plan)
_graph.add_node("execute", execute_actions)

_graph.set_entry_point("gather")
_graph.add_edge("gather", "investigate")
_graph.add_conditional_edges(
    "investigate",
    should_continue_investigating,
    {"tools": "tools", "plan": "plan"},
)
_graph.add_edge("tools", "investigate")
_graph.add_edge("plan", "execute")
_graph.add_edge("execute", END)

agent_graph = _graph.compile()


# ── Public API ─────────────────────────────────────────────────────────

async def run_agent_step(incident: dict, step_number: int, hint: str = "") -> dict:
    """Run one full agent step. Returns the final state."""
    initial_state: AgentState = {
        "incident": incident,
        "timeline": [],
        "topology": {},
        "kb_snippets": [],
        "contacts": {},
        "messages": [],
        "evidence": [],
        "plan": None,
        "events_created": [],
        "step_number": step_number,
        "hint": hint,
    }
    final_state = await agent_graph.ainvoke(initial_state)
    return final_state
