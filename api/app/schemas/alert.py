"""Alert injection schemas."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from app.schemas.event import EventOut


class AlertIn(BaseModel):
    alert_id: str
    host: str
    service: str
    severity: str = "medium"
    title: str
    description: str = ""
    tags: dict[str, Any] = {}


class AlertResponse(BaseModel):
    incident_id: str
    is_new: bool
    event: EventOut
