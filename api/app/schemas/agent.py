"""Agent step schemas — structured LLM output."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

from app.schemas.event import EventOut


class PlannedAction(BaseModel):
    type: Literal[
        "run_command",
        "search_logs",
        "check_metrics",
        "check_network",
        "search_wiki",
        "get_topology",
        "get_contacts",
        "create_ticket",
        "send_email",
        "send_chat",
        "make_call",
        "ask_human",
        "update_severity",
        "escalate",
        "resolve",
    ]
    params: dict[str, Any] = {}
    rationale: str = ""


class AgentPlan(BaseModel):
    """Strict schema passed to LLM via with_structured_output()."""

    summary: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    hypotheses: list[str] = []
    evidence: list[dict[str, Any]] = []
    next_questions: list[str] = []
    actions: list[PlannedAction] = []


class AgentStepRequest(BaseModel):
    hint: Optional[str] = None


class AgentStepResponse(BaseModel):
    run_id: str
    step: int
    plan: AgentPlan
    actions_executed: int
    actions_requiring_approval: int
    tokens_used: int
    duration_ms: int
    events: list[EventOut]
