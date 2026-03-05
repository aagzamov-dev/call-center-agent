"""GET/POST /api/incidents/{id}/tickets — ticket events."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["tickets"])


class TicketCreate(BaseModel):
    title: str
    priority: str = "P2"
    assignee: str = "unassigned"
    description: str = ""


@router.get("/incidents/{incident_id}/tickets")
async def get_tickets(incident_id: str, db: AsyncSession = Depends(get_session)):
    items, total = await svc.get_timeline(db, incident_id, kind="ticket", limit=100)
    return {"items": items}


@router.post("/incidents/{incident_id}/tickets", status_code=201)
async def create_ticket(
    incident_id: str,
    body: TicketCreate,
    db: AsyncSession = Depends(get_session),
):
    inc = await svc.get_incident(db, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    import random
    ext_id = f"INC-{random.randint(1000, 9999)}"
    event = await svc.add_event(
        db,
        incident_id=incident_id,
        kind="ticket",
        actor="human",
        summary=f"Ticket created: {ext_id} — {body.title}",
        data={
            "external_id": ext_id,
            "title": body.title,
            "description": body.description,
            "priority": body.priority,
            "assignee": body.assignee,
            "status": "open",
        },
    )
    return {"event": event}
