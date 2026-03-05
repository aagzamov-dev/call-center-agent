"""Agent state definition for LangGraph."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Core context (set by gather_context)
    incident: dict
    timeline: list[dict]
    topology: dict
    kb_snippets: list[dict]
    contacts: dict

    # LLM conversation history (investigation phase)
    messages: Annotated[list[BaseMessage], add_messages]

    # Collected evidence from tool calls
    evidence: list[dict]

    # Final structured plan (set by produce_plan)
    plan: dict | None

    # Events created during execution
    events_created: list[dict]

    # Step tracking
    step_number: int
    hint: str
