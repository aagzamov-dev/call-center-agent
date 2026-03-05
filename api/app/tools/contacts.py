"""Demo contacts tool — on-call / owner directory."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

CONTACTS: dict[str, dict] = {
    "dba-team": {
        "team": "dba-team",
        "oncall": {"name": "John DBA", "email": "john.dba@company.com", "phone": "+1-555-0101", "role": "Senior DBA"},
        "members": [
            {"name": "John DBA", "email": "john.dba@company.com", "role": "Senior DBA"},
            {"name": "Maria DB", "email": "maria.db@company.com", "role": "DBA"},
        ],
    },
    "platform-team": {
        "team": "platform-team",
        "oncall": {"name": "Alice Platform", "email": "alice.platform@company.com", "phone": "+1-555-0102", "role": "Platform Lead"},
        "members": [
            {"name": "Alice Platform", "email": "alice.platform@company.com", "role": "Platform Lead"},
            {"name": "Charlie Ops", "email": "charlie.ops@company.com", "role": "SRE"},
        ],
    },
    "backend-team": {
        "team": "backend-team",
        "oncall": {"name": "Bob Backend", "email": "bob.backend@company.com", "phone": "+1-555-0103", "role": "Backend Lead"},
        "members": [
            {"name": "Bob Backend", "email": "bob.backend@company.com", "role": "Backend Lead"},
            {"name": "Diana Dev", "email": "diana.dev@company.com", "role": "Senior Developer"},
        ],
    },
    "network-team": {
        "team": "network-team",
        "oncall": {"name": "Eve Network", "email": "eve.network@company.com", "phone": "+1-555-0104", "role": "Network Engineer"},
        "members": [
            {"name": "Eve Network", "email": "eve.network@company.com", "role": "Network Engineer"},
        ],
    },
    "security-team": {
        "team": "security-team",
        "oncall": {"name": "Frank Security", "email": "frank.security@company.com", "phone": "+1-555-0105", "role": "Security Lead"},
        "members": [
            {"name": "Frank Security", "email": "frank.security@company.com", "role": "Security Lead"},
        ],
    },
}

SERVICE_TO_TEAM: dict[str, str] = {
    "postgresql": "dba-team",
    "api-gateway": "platform-team",
    "payment-service": "backend-team",
    "redis": "platform-team",
    "user-service": "backend-team",
}


class ContactsTool(BaseTool):
    name = "get_contacts"
    description = "Look up team contacts, on-call person, and contact info by team name or service name."

    async def execute(self, params: dict) -> ToolResult:
        team = params.get("team", "")
        service = params.get("service", "")
        if service and not team:
            team = SERVICE_TO_TEAM.get(service, "")
        contacts = CONTACTS.get(team)
        if not contacts:
            return ToolResult(success=True, data={"team": team or service, "oncall": None, "members": []})
        return ToolResult(success=True, data=contacts)
