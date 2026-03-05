"""Tool registry — maps tool names to instances and provides LangChain tool wrappers."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import StructuredTool

from app.tools.base import BaseTool
from app.tools.alerts import AlertsTool
from app.tools.metrics import MetricsTool
from app.tools.logs import LogsTool
from app.tools.command import CommandTool
from app.tools.topology import TopologyTool
from app.tools.contacts import ContactsTool
from app.tools.wiki import WikiTool
from app.tools.network import NetworkTool
from app.tools.config_analysis import ConfigAnalysisTool
from app.tools.video import VideoTool

# ── Instances ──────────────────────────────────────────────────────────
_TOOLS: list[BaseTool] = [
    AlertsTool(),
    MetricsTool(),
    LogsTool(),
    CommandTool(),
    TopologyTool(),
    ContactsTool(),
    WikiTool(),
    NetworkTool(),
    ConfigAnalysisTool(),
    VideoTool(),
]

TOOL_MAP: dict[str, BaseTool] = {t.name: t for t in _TOOLS}


# ── LangChain wrappers for LangGraph investigation node ───────────────
def _make_langchain_tool(tool: BaseTool) -> StructuredTool:
    """Wrap a BaseTool as a LangChain StructuredTool so LLM can call it."""
    import asyncio

    async def _fn(**kwargs: Any) -> str:
        result = await tool.execute(kwargs)
        return json.dumps(result.data, default=str)

    return StructuredTool.from_function(
        coroutine=_fn,
        name=tool.name,
        description=tool.description,
    )


# Investigation tools (read-only, safe for agent to call freely)
INVESTIGATION_TOOL_NAMES = [
    "check_alerts", "check_metrics", "search_logs", "run_command",
    "check_network", "check_config",
]

INVESTIGATION_TOOLS: list[StructuredTool] = [
    _make_langchain_tool(TOOL_MAP[name])
    for name in INVESTIGATION_TOOL_NAMES
    if name in TOOL_MAP
]

# Context tools (used in gather_context, not by LLM directly)
CONTEXT_TOOL_NAMES = ["get_topology", "get_contacts", "search_wiki", "search_video"]
