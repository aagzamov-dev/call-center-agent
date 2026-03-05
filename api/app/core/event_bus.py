"""In-memory pub/sub event bus for WebSocket fan-out."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine

Callback = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class EventBus:
    """Simple in-memory pub/sub. Services emit events, WS hub subscribes."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callback]] = defaultdict(list)
        self._global_listeners: list[Callback] = []

    def subscribe(self, incident_id: str, callback: Callback) -> None:
        self._listeners[incident_id].append(callback)

    def unsubscribe(self, incident_id: str, callback: Callback) -> None:
        listeners = self._listeners.get(incident_id, [])
        if callback in listeners:
            listeners.remove(callback)

    def subscribe_global(self, callback: Callback) -> None:
        """Subscribe to ALL events (used for incident list updates)."""
        self._global_listeners.append(callback)

    def unsubscribe_global(self, callback: Callback) -> None:
        if callback in self._global_listeners:
            self._global_listeners.remove(callback)

    async def emit(self, event: dict[str, Any]) -> None:
        incident_id = event.get("incident_id", "")
        listeners = list(self._listeners.get(incident_id, []))
        listeners += list(self._global_listeners)
        await asyncio.gather(
            *(cb(event) for cb in listeners),
            return_exceptions=True,
        )


# Global singleton
event_bus = EventBus()
