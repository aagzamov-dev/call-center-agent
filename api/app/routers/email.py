"""POST /api/email/send — standalone email sending."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["email"])


class EmailSendRequest(BaseModel):
    incident_id: str
    to: str
    cc: str = ""
    subject: str
    body: str
    is_html: bool = False


@router.post("/email/send", status_code=201)
async def send_email(body: EmailSendRequest, db: AsyncSession = Depends(get_session)):
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
        summary=f"Email sent to {body.to}: {body.subject}",
        data={
            "message_id": msg_id,
            "channel": "email",
            "direction": "outbound",
            "sender": "operator@company.com",
            "recipient": body.to,
            "cc": body.cc,
            "subject": body.subject,
            "body": body.body,
            "is_html": body.is_html,
        },
    )
    return {"message_id": msg_id, "status": "sent", "event": event}
