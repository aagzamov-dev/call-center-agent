"""SQLAlchemy ORM models — only 2 tables: incidents + events."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, String, Text
from sqlalchemy.orm import DeclarativeBase


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="medium")
    status = Column(String, nullable=False, default="new")
    host = Column(String, nullable=True)
    service = Column(String, nullable=True)
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_incidents_status", "status"),
        Index("idx_incidents_severity", "severity"),
        Index("idx_incidents_host", "host"),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    incident_id = Column(String, nullable=False, index=False)
    kind = Column(String, nullable=False)
    actor = Column(String, nullable=False, default="system")
    summary = Column(String, nullable=False)
    data = Column(Text, nullable=False, default="{}")
    ts = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("idx_events_incident_ts", "incident_id", "ts"),
        Index("idx_events_incident_kind", "incident_id", "kind"),
    )
