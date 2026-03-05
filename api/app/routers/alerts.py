"""POST /api/alerts — inject alert, create or correlate to incident."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.schemas.alert import AlertIn, AlertResponse
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["alerts"])


@router.post("/alerts", response_model=AlertResponse, status_code=201)
async def inject_alert(body: AlertIn, db: AsyncSession = Depends(get_session)):
    # Simple correlation: check for open incident on same host
    existing = await svc.find_open_incident_for_host(db, body.host)

    if existing:
        incident = existing
        is_new = False
    else:
        incident = await svc.create_incident(
            db,
            title=f"{body.severity.upper()}: {body.title}",
            severity=body.severity,
            host=body.host,
            service=body.service,
        )
        is_new = True

    event = await svc.add_event(
        db,
        incident_id=incident.id,
        kind="alert",
        actor="system",
        summary=f"Alert received: {body.title}",
        data=body.model_dump(),
    )

    return AlertResponse(incident_id=incident.id, is_new=is_new, event=event)
