"""Action executor — runs planned actions and creates timeline events."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import incident_service as svc


_ticket_counter = 1000


async def execute_action(
    db: AsyncSession,
    incident_id: str,
    action: dict[str, Any],
) -> dict:
    """Execute a single planned action. Returns the created event dict."""
    action_type = action.get("type", "")
    params = action.get("params", {})
    rationale = action.get("rationale", "")

    handler = ACTION_HANDLERS.get(action_type, _unknown_action)
    return await handler(db, incident_id, params, rationale)


# ── Handlers ──────────────────────────────────────────────────────────

async def _create_ticket(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    global _ticket_counter
    _ticket_counter += 1
    ext_id = f"INC-{_ticket_counter}"
    data = {
        "external_id": ext_id,
        "title": params.get("title", "Untitled ticket"),
        "description": params.get("description", rationale),
        "priority": params.get("priority", "P2"),
        "assignee": params.get("assignee", "unassigned"),
        "status": "open",
    }
    return await svc.add_event(
        db, incident_id=incident_id, kind="ticket", actor="agent",
        summary=f"Created {data['priority']} ticket {ext_id}: {data['title']}",
        data=data,
    )


async def _send_email(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    data = {
        "channel": "email",
        "direction": "outbound",
        "sender": "noc-agent@company.com",
        "recipient": params.get("to") or params.get("recipient", ""),
        "subject": params.get("subject", "Incident notification"),
        "body": params.get("body") or params.get("message", rationale),
    }
    return await svc.add_event(
        db, incident_id=incident_id, kind="message", actor="agent",
        summary=f"Email sent to {data['recipient']}: {data['subject']}",
        data=data,
    )


async def _send_chat(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    data = {
        "channel": "chat",
        "direction": "outbound",
        "sender": "noc-agent",
        "recipient": params.get("channel") or params.get("recipient", ""),
        "body": params.get("message") or params.get("body", rationale),
    }
    return await svc.add_event(
        db, incident_id=incident_id, kind="message", actor="agent",
        summary=f"Chat sent to {data['recipient']}",
        data=data,
    )


async def _make_call(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    data = {
        "channel": "voice",
        "direction": "outbound",
        "sender": "noc-agent",
        "recipient": params.get("recipient_name") or params.get("phone", ""),
        "phone": params.get("phone", ""),
        "script": params.get("script", rationale),
        "status": "initiated",
    }
    return await svc.add_event(
        db, incident_id=incident_id, kind="message", actor="agent",
        summary=f"Voice call initiated to {data['recipient']}",
        data=data,
    )


async def _ask_human(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    question = params.get("question") or params.get("message", rationale)
    return await svc.add_event(
        db, incident_id=incident_id, kind="note", actor="agent",
        summary=f"Agent asks: {question}",
        data={"body": question},
    )


async def _update_severity(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    new_severity = params.get("severity", "high")
    inc = await svc.get_incident(db, incident_id)
    old_severity = inc.severity if inc else "unknown"
    await svc.update_incident(db, incident_id, severity=new_severity)
    return await svc.add_event(
        db, incident_id=incident_id, kind="status_change", actor="agent",
        summary=f"Severity changed: {old_severity} → {new_severity}",
        data={"field": "severity", "from": old_severity, "to": new_severity, "reason": rationale},
    )


async def _escalate(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    await svc.update_incident(db, incident_id, status="mitigating")
    return await svc.add_event(
        db, incident_id=incident_id, kind="status_change", actor="agent",
        summary=f"Incident escalated: {rationale}",
        data={"field": "status", "from": "investigating", "to": "mitigating", "reason": rationale},
    )


async def _resolve(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    await svc.update_incident(db, incident_id, status="resolved")
    return await svc.add_event(
        db, incident_id=incident_id, kind="status_change", actor="agent",
        summary=f"Incident resolved: {rationale}",
        data={"field": "status", "from": "investigating", "to": "resolved", "reason": rationale},
    )


async def _unknown_action(db: AsyncSession, incident_id: str, params: dict, rationale: str) -> dict:
    return await svc.add_event(
        db, incident_id=incident_id, kind="note", actor="agent",
        summary=f"Unknown action attempted: {params}",
        data={"params": params, "rationale": rationale},
    )


ACTION_HANDLERS = {
    "create_ticket": _create_ticket,
    "send_email": _send_email,
    "send_chat": _send_chat,
    "make_call": _make_call,
    "ask_human": _ask_human,
    "update_severity": _update_severity,
    "escalate": _escalate,
    "resolve": _resolve,
}
