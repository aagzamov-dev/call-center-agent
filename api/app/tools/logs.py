"""Demo log search tool — returns mock log lines."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

SCENARIOS: dict[str, list[dict]] = {
    "db-prod-01": [
        {"ts": "2026-03-04T10:30:12Z", "level": "ERROR", "service": "postgresql",
         "message": "pg_archiver: failed to archive WAL file 0000000100000002000000A8"},
        {"ts": "2026-03-04T10:35:45Z", "level": "ERROR", "service": "postgresql",
         "message": "pg_archiver: failed to archive WAL file 0000000100000002000000A9"},
        {"ts": "2026-03-04T10:42:00Z", "level": "WARNING", "service": "postgresql",
         "message": "checkpoint starting: time"},
        {"ts": "2026-03-04T10:55:00Z", "level": "CRITICAL", "service": "system",
         "message": "Filesystem /var/lib/postgresql reached 97% usage"},
        {"ts": "2026-03-04T10:56:00Z", "level": "ERROR", "service": "postgresql",
         "message": "could not write to file pg_wal/xlogtemp.31337: No space left on device"},
        {"ts": "2026-03-04T10:58:00Z", "level": "FATAL", "service": "postgresql",
         "message": "FATAL: too many connections for role 'payment_svc'"},
    ],
    "api-gw-01": [
        {"ts": "2026-03-04T10:44:00Z", "level": "WARNING", "service": "api-gateway",
         "message": "Connection pool exhausted for upstream postgresql"},
        {"ts": "2026-03-04T10:45:30Z", "level": "ERROR", "service": "api-gateway",
         "message": "Request timeout after 30s: POST /api/payments/process"},
        {"ts": "2026-03-04T10:46:00Z", "level": "ERROR", "service": "api-gateway",
         "message": "HTTP 503 returned to client: service unavailable"},
        {"ts": "2026-03-04T10:50:00Z", "level": "ERROR", "service": "api-gateway",
         "message": "SSL_ERROR_EXPIRED_CERT_ALERT from client 10.0.1.50"},
        {"ts": "2026-03-04T10:51:00Z", "level": "ERROR", "service": "api-gateway",
         "message": "could not connect to server: Connection refused (port 5432)"},
    ],
}


class LogsTool(BaseTool):
    name = "search_logs"
    description = "Search logs by host, service, and keyword query within a time window."

    async def execute(self, params: dict) -> ToolResult:
        host = params.get("host", "")
        query = params.get("query", "").lower()
        lines = SCENARIOS.get(host, [])
        if query:
            lines = [l for l in lines if query in l["message"].lower()]
        return ToolResult(success=True, data={"host": host, "lines": lines, "count": len(lines)})
