"""POST /api/voice/transcribe — upload audio, get text back, optionally feed to agent."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc
from app.services.audio_service import transcribe_audio

router = APIRouter(prefix="/api", tags=["voice"])


@router.post("/voice/transcribe", status_code=201)
async def voice_transcribe(
    audio: UploadFile = File(...),
    incident_id: str | None = Query(None, description="If set, transcript is added as human_reply to this incident"),
    sender: str = Query("caller", description="Who is speaking"),
    language: str | None = Query(None, description="ISO language code (e.g. en, ru, uz)"),
    db: AsyncSession = Depends(get_session),
):
    """
    Upload a voice recording → transcribed to text via whisper-1.
    If incident_id is provided, the transcript is automatically injected
    as a human_reply event so the agent can read it.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "Empty audio file")

    ext = audio.filename.rsplit(".", 1)[-1] if audio.filename and "." in audio.filename else "webm"
    filename = f"voice_{uuid.uuid4().hex[:8]}.{ext}"

    result = await transcribe_audio(audio_bytes, filename=filename, language=language)
    transcript_text = result["text"]

    event = None
    if incident_id:
        inc = await svc.get_incident(db, incident_id)
        if not inc:
            raise HTTPException(404, "Incident not found")

        event = await svc.add_event(
            db,
            incident_id=incident_id,
            kind="human_reply",
            actor="human",
            summary=f"Voice message from {sender}: {transcript_text[:100]}",
            data={
                "sender": sender,
                "body": transcript_text,
                "channel": "voice",
                "audio_url": result["audio_url"],
            },
        )

    return {
        "transcript": transcript_text,
        "audio_url": result["audio_url"],
        "model": result["model"],
        "event": event,
    }
