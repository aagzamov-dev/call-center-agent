"""Incident schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IncidentOut(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    host: Optional[str] = None
    service: Optional[str] = None
    summary: str = ""
    event_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentList(BaseModel):
    items: list[IncidentOut]
    total: int
