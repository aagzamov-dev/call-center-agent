"""Demo network/security tool — STUB: returns static FortiGate-like status."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

SCENARIOS: dict[str, dict] = {
    "fw-prod-01": {
        "device": "fw-prod-01",
        "type": "FortiGate 600E",
        "status": "online",
        "cpu_usage": 35,
        "memory_usage": 62,
        "sessions": 45230,
        "recent_rules": [
            {"id": 142, "action": "deny", "src": "10.0.2.0/24", "dst": "10.0.1.10",
             "port": 5432, "created": "2026-03-04T10:30:00Z", "comment": "Emergency block DB access"},
        ],
        "interfaces": [
            {"name": "port1", "status": "up", "speed": "10Gbps", "ip": "10.0.0.1/24"},
            {"name": "port2", "status": "up", "speed": "10Gbps", "ip": "10.0.1.1/24"},
            {"name": "port3", "status": "up", "speed": "1Gbps", "ip": "10.0.2.1/24"},
        ],
    },
    "sw-prod-01": {
        "device": "sw-prod-01",
        "type": "FortiSwitch 248E",
        "status": "online",
        "ports_up": 24,
        "ports_total": 48,
        "vlan_count": 8,
    },
}


class NetworkTool(BaseTool):
    name = "check_network"
    description = "Check network/security device status (FortiGate firewall rules, port status, interfaces)."

    async def execute(self, params: dict) -> ToolResult:
        device = params.get("device", "fw-prod-01")
        data = SCENARIOS.get(device, SCENARIOS.get("fw-prod-01", {}))
        check = params.get("check", "status")
        return ToolResult(success=True, data=data)
