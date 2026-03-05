"""WebSocket message schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WsClientMessage(BaseModel):
    type: str  # sub, unsub, ping
    incident_id: str = ""


class WsServerMessage(BaseModel):
    type: str  # connected, ok, event, error, pong
    ref: str = ""
    event: dict[str, Any] | None = None
    incident_id: str = ""
    msg: str = ""
    ts: str = ""
