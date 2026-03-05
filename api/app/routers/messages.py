"""GET/POST /api/incidents/{id}/messages — message events."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["messages"])


class MessageCreate(BaseModel):
    channel: str  # email, chat, voice
    recipient: str
    subject: str = ""
    body: str


@router.get("/incidents/{incident_id}/messages")
async def get_messages(
    incident_id: str,
    channel: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    items, total = await svc.get_timeline(db, incident_id, kind="message", limit=100)
    if channel:
        items = [i for i in items if i.get("data", {}).get("channel") == channel]
    return {"items": items}


@router.post("/incidents/{incident_id}/messages", status_code=201)
async def send_message(
    incident_id: str,
    body: MessageCreate,
    db: AsyncSession = Depends(get_session),
):
    inc = await svc.get_incident(db, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    event = await svc.add_event(
        db,
        incident_id=incident_id,
        kind="message",
        actor="human",
        summary=f"{body.channel.capitalize()} sent to {body.recipient}",
        data={
            "channel": body.channel,
            "direction": "outbound",
            "sender": "operator",
            "recipient": body.recipient,
            "subject": body.subject,
            "body": body.body,
        },
    )
    return {"event": event}
