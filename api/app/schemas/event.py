"""Canonical event schema — used in DB, REST, WebSocket, and UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    kind: str
    actor: str = "system"
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    id: str
    incident_id: str
    kind: str
    actor: str
    summary: str
    data: dict[str, Any]
    ts: datetime

    model_config = {"from_attributes": True}


class EventList(BaseModel):
    items: list[EventOut]
    total: int
