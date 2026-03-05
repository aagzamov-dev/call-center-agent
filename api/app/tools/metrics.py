"""Demo metrics tool — returns mock time-series data."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

SCENARIOS: dict[tuple[str, str], list[dict]] = {
    ("db-prod-01", "disk"): [
        {"ts": "2026-03-04T05:00:00Z", "value": 60},
        {"ts": "2026-03-04T07:00:00Z", "value": 72},
        {"ts": "2026-03-04T09:00:00Z", "value": 88},
        {"ts": "2026-03-04T10:00:00Z", "value": 93},
        {"ts": "2026-03-04T10:30:00Z", "value": 95},
        {"ts": "2026-03-04T11:00:00Z", "value": 97},
    ],
    ("db-prod-01", "cpu"): [
        {"ts": "2026-03-04T05:00:00Z", "value": 15},
        {"ts": "2026-03-04T08:00:00Z", "value": 22},
        {"ts": "2026-03-04T11:00:00Z", "value": 35},
    ],
    ("db-prod-01", "ram"): [
        {"ts": "2026-03-04T05:00:00Z", "value": 68},
        {"ts": "2026-03-04T11:00:00Z", "value": 74},
    ],
    ("api-gw-01", "cpu"): [
        {"ts": "2026-03-04T10:00:00Z", "value": 20},
        {"ts": "2026-03-04T10:30:00Z", "value": 55},
        {"ts": "2026-03-04T10:45:00Z", "value": 94},
        {"ts": "2026-03-04T11:00:00Z", "value": 91},
    ],
    ("api-gw-01", "latency"): [
        {"ts": "2026-03-04T10:00:00Z", "value": 45},
        {"ts": "2026-03-04T10:45:00Z", "value": 1200},
        {"ts": "2026-03-04T11:00:00Z", "value": 980},
    ],
}


class MetricsTool(BaseTool):
    name = "check_metrics"
    description = "Retrieve performance metric time-series (cpu, ram, disk, latency) for a host."

    async def execute(self, params: dict) -> ToolResult:
        host = params.get("host", "")
        metric = params.get("metric", "cpu")
        points = SCENARIOS.get((host, metric), [])
        if not points:
            points = [{"ts": "2026-03-04T11:00:00Z", "value": 42}]
        return ToolResult(success=True, data={
            "host": host, "metric": metric,
            "datapoints": points, "unit": "%" if metric != "latency" else "ms"
        })
