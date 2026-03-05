"""POST /api/chat — main user-facing chat endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import ticket_service as svc

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    channel: str = "chat"


@router.post("/chat")
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_session)):
    from app.agent.graph import run_support_agent

    # Run the agent
    result = await run_support_agent(body.message, channel=body.channel)

    reply = result["reply"]
    ticket_action = result["ticket_action"]
    agent_steps = result["agent_steps"]
    ticket = None

    # Create ticket if agent decided to
    if ticket_action.get("action") == "create":
        ticket = await svc.create_ticket(
            db,
            title=ticket_action.get("title", body.message[:80]),
            team=ticket_action.get("team", "help_desk"),
            priority=ticket_action.get("priority", "P3"),
            summary=ticket_action.get("summary", ""),
        )
        ticket_id = ticket["id"]

        # Save user message
        await svc.add_message(db, ticket_id=ticket_id, role="user", content=body.message, channel=body.channel)
        # Save agent reply
        await svc.add_message(db, ticket_id=ticket_id, role="agent", content=reply, channel=body.channel)
        # Save agent steps (for admin reasoning view)
        for step in agent_steps:
            await svc.add_agent_step(
                db, ticket_id=ticket_id,
                step_type=step.get("step_type", ""),
                tool_name=step.get("tool_name", ""),
                input_data=step.get("input"),
                output_data=step.get("output"),
            )

    return {
        "reply": reply,
        "ticket": ticket,
        "kb_results_count": len(result.get("kb_results", [])),
    }
