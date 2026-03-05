"""POST /api/incidents/{id}/agent/step — run one LangGraph agent step."""

import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["agent"])


class AgentStepRequest(BaseModel):
    hint: str | None = None


@router.post("/incidents/{incident_id}/agent/step")
async def run_agent_step(
    incident_id: str,
    body: AgentStepRequest | None = None,
    db: AsyncSession = Depends(get_session),
):
    inc = await svc.get_incident(db, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    # Count existing agent_plan events to get step number
    timeline, _ = await svc.get_timeline(db, incident_id, kind="agent_plan", limit=100)
    step_number = len(timeline) + 1

    # Build incident dict for the graph
    incident_dict = {
        "id": inc.id,
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "host": inc.host,
        "service": inc.service,
        "summary": inc.summary or "",
    }

    hint = body.hint if body else ""
    t0 = time.time()

    # Run LangGraph agent
    from app.agent.graph import run_agent_step as _run
    final_state = await _run(incident_dict, step_number, hint=hint or "")

    duration_ms = int((time.time() - t0) * 1000)
    plan = final_state.get("plan", {})
    events = final_state.get("events_created", [])

    # Count actions by status
    executed = sum(1 for e in events if e.get("kind") == "action_exec" and e.get("data", {}).get("status") != "needs_approval")
    pending = sum(1 for e in events if e.get("kind") == "action_exec" and e.get("data", {}).get("status") == "needs_approval")

    return {
        "run_id": f"run_{incident_id}_{step_number}",
        "step": step_number,
        "plan": plan,
        "actions_executed": executed,
        "actions_requiring_approval": pending,
        "tokens_used": 0,  # TODO: extract from LLM response metadata
        "duration_ms": duration_ms,
        "events": events,
    }
