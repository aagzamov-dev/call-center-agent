"""Demo alerts tool — returns related alerts for a host/service."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

SCENARIOS: dict[str, list[dict]] = {
    "db-prod-01": [
        {"alert_id": "zabbix-12345", "severity": "critical", "title": "Disk usage > 95% on /var/lib/postgresql",
         "host": "db-prod-01", "service": "postgresql", "ts": "2026-03-04T10:55:00Z"},
        {"alert_id": "zabbix-12346", "severity": "warning", "title": "WAL archiving lag > 30min",
         "host": "db-prod-01", "service": "postgresql", "ts": "2026-03-04T10:50:00Z"},
        {"alert_id": "zabbix-12347", "severity": "high", "title": "Replication lag > 60s on db-prod-02",
         "host": "db-prod-02", "service": "postgresql", "ts": "2026-03-04T10:58:00Z"},
    ],
    "api-gw-01": [
        {"alert_id": "zabbix-22001", "severity": "high", "title": "CPU > 90% sustained for 15min",
         "host": "api-gw-01", "service": "api-gateway", "ts": "2026-03-04T10:45:00Z"},
        {"alert_id": "zabbix-22002", "severity": "warning", "title": "HTTP 5xx rate > 5%",
         "host": "api-gw-01", "service": "api-gateway", "ts": "2026-03-04T10:47:00Z"},
    ],
}


class AlertsTool(BaseTool):
    name = "check_alerts"
    description = "Retrieve related alerts for a host in a given time window."

    async def execute(self, params: dict) -> ToolResult:
        host = params.get("host", "")
        alerts = SCENARIOS.get(host, [])
        return ToolResult(success=True, data={"alerts": alerts, "count": len(alerts)})
