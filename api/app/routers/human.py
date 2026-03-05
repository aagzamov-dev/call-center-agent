"""POST /api/incidents/{id}/human-reply — inject human answer."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["human"])


class HumanReplyRequest(BaseModel):
    sender: str
    body: str


@router.post("/incidents/{incident_id}/human-reply", status_code=201)
async def send_human_reply(
    incident_id: str,
    body: HumanReplyRequest,
    db: AsyncSession = Depends(get_session),
):
    inc = await svc.get_incident(db, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    event = await svc.add_event(
        db,
        incident_id=incident_id,
        kind="human_reply",
        actor=f"human",
        summary=f"Human reply from {body.sender}: {body.body[:100]}",
        data={"sender": body.sender, "body": body.body},
    )
    return {"event": event}
