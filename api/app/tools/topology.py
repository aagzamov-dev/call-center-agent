"""Demo topology tool — service dependency graph."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

TOPOLOGY: dict[str, dict] = {
    "postgresql": {
        "service": "postgresql",
        "hosts": ["db-prod-01", "db-prod-02"],
        "depends_on": ["storage-san-01"],
        "depended_by": ["api-gateway", "payment-service", "user-service", "order-service"],
        "owner": "dba-team",
        "oncall": "john.dba@company.com",
        "criticality": "tier-1",
    },
    "api-gateway": {
        "service": "api-gateway",
        "hosts": ["api-gw-01", "api-gw-02"],
        "depends_on": ["postgresql", "redis", "payment-service"],
        "depended_by": ["frontend", "mobile-app"],
        "owner": "platform-team",
        "oncall": "alice.platform@company.com",
        "criticality": "tier-1",
    },
    "payment-service": {
        "service": "payment-service",
        "hosts": ["pay-01", "pay-02"],
        "depends_on": ["postgresql", "redis", "stripe-api"],
        "depended_by": ["api-gateway", "order-service"],
        "owner": "backend-team",
        "oncall": "bob.backend@company.com",
        "criticality": "tier-1",
    },
    "redis": {
        "service": "redis",
        "hosts": ["cache-01"],
        "depends_on": [],
        "depended_by": ["api-gateway", "payment-service", "user-service"],
        "owner": "platform-team",
        "oncall": "alice.platform@company.com",
        "criticality": "tier-2",
    },
    "user-service": {
        "service": "user-service",
        "hosts": ["user-01"],
        "depends_on": ["postgresql", "redis"],
        "depended_by": ["api-gateway"],
        "owner": "backend-team",
        "oncall": "bob.backend@company.com",
        "criticality": "tier-2",
    },
}


class TopologyTool(BaseTool):
    name = "get_topology"
    description = "Get service dependency topology: what it depends on, what depends on it, owner, on-call."

    async def execute(self, params: dict) -> ToolResult:
        service = params.get("service", "")
        topo = TOPOLOGY.get(service)
        if not topo:
            return ToolResult(success=True, data={"service": service, "hosts": [], "depends_on": [], "depended_by": [], "owner": "unknown", "oncall": "unknown", "criticality": "unknown"})
        return ToolResult(success=True, data=topo)
