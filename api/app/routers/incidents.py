"""GET /api/incidents — list and detail."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["incidents"])


@router.get("/incidents")
async def list_incidents(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session),
):
    items, total = await svc.list_incidents(db, status=status, limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_session)):
    inc = await svc.get_incident(db, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    event_count = await svc.count_events(db, incident_id)
    d = {
        "id": inc.id,
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "host": inc.host,
        "service": inc.service,
        "summary": inc.summary or "",
        "event_count": event_count,
        "created_at": inc.created_at.isoformat() if inc.created_at else "",
        "updated_at": inc.updated_at.isoformat() if inc.updated_at else "",
    }
    return d
