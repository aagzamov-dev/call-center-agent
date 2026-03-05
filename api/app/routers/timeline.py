"""GET /api/incidents/{id}/timeline — event list."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["timeline"])


@router.get("/incidents/{incident_id}/timeline")
async def get_timeline(
    incident_id: str,
    kind: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session),
):
    items, total = await svc.get_timeline(db, incident_id, kind=kind, limit=limit, offset=offset)
    return {"items": items, "total": total}
