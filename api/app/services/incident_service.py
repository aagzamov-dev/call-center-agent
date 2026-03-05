"""Incident service — CRUD + events + timeline. Central write path."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import event_bus
from app.db.models import Event, Incident


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

async def create_incident(
    db: AsyncSession,
    *,
    title: str,
    severity: str = "medium",
    host: str | None = None,
    service: str | None = None,
) -> Incident:
    inc = Incident(
        id=_uid("inc_"),
        title=title,
        severity=severity,
        status="new",
        host=host,
        service=service,
        summary="",
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(inc)
    await db.commit()
    await db.refresh(inc)
    return inc


async def get_incident(db: AsyncSession, incident_id: str) -> Incident | None:
    return await db.get(Incident, incident_id)


async def list_incidents(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    q = select(Incident).order_by(Incident.created_at.desc())
    count_q = select(func.count(Incident.id))
    if status:
        q = q.where(Incident.status == status)
        count_q = count_q.where(Incident.status == status)
    q = q.limit(limit).offset(offset)

    rows = (await db.execute(q)).scalars().all()
    total = (await db.execute(count_q)).scalar() or 0

    items = []
    for inc in rows:
        ec = (await db.execute(
            select(func.count(Event.id)).where(Event.incident_id == inc.id)
        )).scalar() or 0
        d = _inc_to_dict(inc)
        d["event_count"] = ec
        items.append(d)
    return items, total


async def update_incident(
    db: AsyncSession,
    incident_id: str,
    **kwargs: Any,
) -> Incident | None:
    kwargs["updated_at"] = _now()
    await db.execute(
        update(Incident).where(Incident.id == incident_id).values(**kwargs)
    )
    await db.commit()
    return await get_incident(db, incident_id)


async def find_open_incident_for_host(
    db: AsyncSession, host: str
) -> Incident | None:
    q = (
        select(Incident)
        .where(Incident.host == host)
        .where(Incident.status.notin_(["resolved", "closed"]))
        .order_by(Incident.created_at.desc())
        .limit(1)
    )
    return (await db.execute(q)).scalar_one_or_none()


# ---------------------------------------------------------------------------
# Events (canonical)
# ---------------------------------------------------------------------------

async def add_event(
    db: AsyncSession,
    *,
    incident_id: str,
    kind: str,
    actor: str = "system",
    summary: str,
    data: dict[str, Any] | None = None,
) -> dict:
    evt = Event(
        id=_uid("evt_"),
        incident_id=incident_id,
        kind=kind,
        actor=actor,
        summary=summary,
        data=json.dumps(data or {}, default=str),
        ts=_now(),
    )
    db.add(evt)
    await db.commit()
    await db.refresh(evt)
    evt_dict = _evt_to_dict(evt)
    await event_bus.emit(evt_dict)
    return evt_dict


async def get_timeline(
    db: AsyncSession,
    incident_id: str,
    *,
    kind: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    q = (
        select(Event)
        .where(Event.incident_id == incident_id)
        .order_by(Event.ts.asc())
    )
    count_q = select(func.count(Event.id)).where(Event.incident_id == incident_id)
    if kind:
        kinds = [k.strip() for k in kind.split(",")]
        q = q.where(Event.kind.in_(kinds))
        count_q = count_q.where(Event.kind.in_(kinds))
    total = (await db.execute(count_q)).scalar() or 0
    rows = (await db.execute(q.limit(limit).offset(offset))).scalars().all()
    return [_evt_to_dict(e) for e in rows], total


async def get_recent_events(
    db: AsyncSession, incident_id: str, limit: int = 15
) -> list[dict]:
    q = (
        select(Event)
        .where(Event.incident_id == incident_id)
        .order_by(Event.ts.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).scalars().all()
    return [_evt_to_dict(e) for e in reversed(rows)]


async def count_events(db: AsyncSession, incident_id: str) -> int:
    q = select(func.count(Event.id)).where(Event.incident_id == incident_id)
    return (await db.execute(q)).scalar() or 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inc_to_dict(inc: Incident) -> dict:
    return {
        "id": inc.id,
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "host": inc.host,
        "service": inc.service,
        "summary": inc.summary or "",
        "created_at": inc.created_at.isoformat() if inc.created_at else "",
        "updated_at": inc.updated_at.isoformat() if inc.updated_at else "",
    }


def _evt_to_dict(evt: Event) -> dict:
    data = evt.data
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            data = {}
    return {
        "id": evt.id,
        "incident_id": evt.incident_id,
        "kind": evt.kind,
        "actor": evt.actor,
        "summary": evt.summary,
        "data": data,
        "ts": evt.ts.isoformat() if evt.ts else "",
    }
