"""Policy layer — validates agent actions before execution."""

from __future__ import annotations

ALWAYS_ALLOWED = {
    "run_command", "search_logs", "check_metrics", "check_network",
    "search_wiki", "get_topology", "get_contacts", "ask_human",
    "check_config", "search_video",
}

AUTO_EXECUTE = {
    "create_ticket", "send_email", "send_chat", "update_severity",
}

NEEDS_APPROVAL = {
    "make_call", "escalate", "resolve",
}


def validate_action(action: dict) -> str:
    """Returns 'execute', 'needs_approval', or 'rejected'."""
    action_type = action.get("type", "")
    if action_type in ALWAYS_ALLOWED:
        return "execute"
    if action_type in AUTO_EXECUTE:
        return "execute"
    if action_type in NEEDS_APPROVAL:
        return "needs_approval"
    return "rejected"
