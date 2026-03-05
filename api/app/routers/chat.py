"""POST /api/chat/send — standalone chat sending."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["chat"])


class ChatSendRequest(BaseModel):
    incident_id: str
    channel: str  # e.g. "#dba-alerts"
    message: str


@router.post("/chat/send", status_code=201)
async def send_chat(body: ChatSendRequest, db: AsyncSession = Depends(get_session)):
    inc = await svc.get_incident(db, body.incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    import uuid
    msg_id = f"msg_{uuid.uuid4().hex[:8]}"

    event = await svc.add_event(
        db,
        incident_id=body.incident_id,
        kind="message",
        actor="human",
        summary=f"Chat sent to {body.channel}",
        data={
            "message_id": msg_id,
            "channel": "chat",
            "direction": "outbound",
            "sender": "operator",
            "recipient": body.channel,
            "body": body.message,
        },
    )
    return {"message_id": msg_id, "status": "sent", "event": event}
