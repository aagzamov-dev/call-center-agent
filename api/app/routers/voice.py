"""POST /api/voice/transcribe — voice input via STT."""

import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.audio_service import transcribe_audio

router = APIRouter(prefix="/api", tags=["voice"])


@router.post("/voice/transcribe")
async def voice_transcribe(
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio file")

    ext = audio.filename.rsplit(".", 1)[-1] if audio.filename and "." in audio.filename else "webm"
    filename = f"voice_{uuid.uuid4().hex[:8]}.{ext}"

    result = await transcribe_audio(audio_bytes, filename=filename)
    transcript = result["text"]

    # Now run it through the chat agent
    from app.agent.graph import run_support_agent
    from app.services import ticket_service as svc

    agent_result = await run_support_agent(transcript, channel="voice")
    reply = agent_result["reply"]
    ticket_action = agent_result["ticket_action"]
    ticket = None

    if ticket_action.get("action") == "create":
        ticket = await svc.create_ticket(
            db,
            title=ticket_action.get("title", transcript[:80]),
            team=ticket_action.get("team", "help_desk"),
            priority=ticket_action.get("priority", "P3"),
            summary=ticket_action.get("summary", ""),
        )
        await svc.add_message(db, ticket_id=ticket["id"], role="user", content=transcript, channel="voice",
                              metadata={"audio_url": result["audio_url"]})
        await svc.add_message(db, ticket_id=ticket["id"], role="agent", content=reply, channel="voice")
        for step in agent_result.get("agent_steps", []):
            await svc.add_agent_step(db, ticket_id=ticket["id"], step_type=step.get("step_type", ""),
                                     tool_name=step.get("tool_name", ""), input_data=step.get("input"),
                                     output_data=step.get("output"))

    return {"transcript": transcript, "reply": reply, "ticket": ticket, "audio_url": result["audio_url"]}
