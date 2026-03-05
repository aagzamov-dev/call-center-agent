"""Demo config analysis tool — STUB: returns canned config diffs."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

SCENARIOS: dict[tuple[str, str], dict] = {
    ("db-prod-01", "postgresql"): {
        "host": "db-prod-01",
        "service": "postgresql",
        "config_file": "/etc/postgresql/14/main/postgresql.conf",
        "current_values": {
            "max_connections": "200",
            "shared_buffers": "8GB",
            "wal_level": "replica",
            "archive_mode": "on",
            "archive_command": "test ! -f /archive/%f && cp %p /archive/%f",
        },
        "diff_from_baseline": [
            "- max_connections = 100",
            "+ max_connections = 200",
            "  # Changed 2026-02-15 by dba-team (ticket INC-890)",
        ],
    },
    ("api-gw-01", "nginx"): {
        "host": "api-gw-01",
        "service": "nginx",
        "config_file": "/etc/nginx/nginx.conf",
        "current_values": {
            "worker_processes": "auto",
            "worker_connections": "4096",
            "ssl_certificate": "/etc/ssl/certs/company.crt",
            "ssl_certificate_key": "/etc/ssl/private/company.key",
        },
        "diff_from_baseline": [],
    },
}


class ConfigAnalysisTool(BaseTool):
    name = "check_config"
    description = "Retrieve configuration snapshots and diffs from baseline for a host/service."

    async def execute(self, params: dict) -> ToolResult:
        host = params.get("host", "")
        service = params.get("service", "")
        data = SCENARIOS.get((host, service))
        if not data:
            data = {"host": host, "service": service, "config_file": "unknown", "current_values": {}, "diff_from_baseline": []}
        return ToolResult(success=True, data=data)
