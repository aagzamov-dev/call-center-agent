"""Base tool interface and result model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    data: dict[str, Any] = {}
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> ToolResult:
        ...
