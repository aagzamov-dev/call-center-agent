"""Tickets CRUD — admin-facing."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import ticket_service as svc

router = APIRouter(prefix="/api", tags=["tickets"])


@router.get("/tickets")
async def list_tickets(
    team: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_session),
):
    return {"tickets": await svc.list_tickets(db, team=team, status=status, limit=limit)}


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_session)):
    t = await svc.get_ticket(db, ticket_id)
    if not t:
        raise HTTPException(404, "Ticket not found")
    return t


class TicketUpdate(BaseModel):
    status: str | None = None
    assigned_to: str | None = None
    priority: str | None = None
    team: str | None = None


@router.patch("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, body: TicketUpdate, db: AsyncSession = Depends(get_session)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    t = await svc.update_ticket(db, ticket_id, **updates)
    if not t:
        raise HTTPException(404, "Ticket not found")
    return t
