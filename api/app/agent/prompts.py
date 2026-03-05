"""System prompt template for the incident investigation agent."""

SYSTEM_PROMPT = """You are an expert Incident Response AI Agent for a NOC (Network Operations Center).

## Your Role
You investigate infrastructure incidents by gathering evidence using diagnostic tools, then produce a structured action plan.

## Current Incident
Title: {incident_title}
Severity: {incident_severity}
Status: {incident_status}
Host: {incident_host}
Service: {incident_service}

## Recent Timeline
{timeline_summary}

## Service Topology
{topology_summary}

## Relevant Knowledge Base
{kb_summary}

## On-Call Contacts
{contacts_summary}

## Instructions
1. INVESTIGATE: Use the available tools to gather evidence about the root cause.
   - Check metrics for trends (CPU, RAM, disk, latency)
   - Search logs for errors and warnings
   - Run diagnostic commands (df, top, pg_stat_activity, etc.)
   - Check related alerts for the host
   - Check network/firewall status if relevant
   - Review config changes if relevant

2. When you have enough evidence, STOP calling tools. The system will then ask you for your final plan.

3. Be thorough but efficient — typically 2-4 tool calls are sufficient.

4. Focus on the MOST LIKELY root cause based on the alert and evidence.

{hint_section}"""


def build_system_prompt(
    incident: dict,
    timeline: list[dict],
    topology: dict,
    kb_snippets: list[dict],
    contacts: dict,
    hint: str = "",
) -> str:
    timeline_summary = "\n".join(
        f"- [{e.get('ts', '')}] {e.get('kind', '')}: {e.get('summary', '')}"
        for e in (timeline or [])[-10:]
    ) or "No events yet."

    topo_items = []
    if topology:
        topo_items.append(f"Service: {topology.get('service', 'unknown')}")
        topo_items.append(f"Hosts: {', '.join(topology.get('hosts', []))}")
        topo_items.append(f"Depends on: {', '.join(topology.get('depends_on', []))}")
        topo_items.append(f"Depended by: {', '.join(topology.get('depended_by', []))}")
        topo_items.append(f"Owner: {topology.get('owner', 'unknown')}")
    topology_summary = "\n".join(topo_items) or "No topology data."

    kb_items = []
    for kb in (kb_snippets or [])[:3]:
        kb_items.append(f"### {kb.get('title', '')}\n{kb.get('snippet', '')}")
    kb_summary = "\n\n".join(kb_items) or "No relevant runbooks found."

    contacts_info = []
    if contacts:
        oncall = contacts.get("oncall", {})
        if oncall:
            contacts_info.append(f"On-call: {oncall.get('name', '')} ({oncall.get('email', '')}, {oncall.get('phone', '')})")
        for m in contacts.get("members", [])[:3]:
            contacts_info.append(f"- {m.get('name', '')} ({m.get('role', '')}): {m.get('email', '')}")
    contacts_summary = "\n".join(contacts_info) or "No contact info available."

    hint_section = f"## Additional Context from Human\n{hint}" if hint else ""

    return SYSTEM_PROMPT.format(
        incident_title=incident.get("title", ""),
        incident_severity=incident.get("severity", ""),
        incident_status=incident.get("status", ""),
        incident_host=incident.get("host", ""),
        incident_service=incident.get("service", ""),
        timeline_summary=timeline_summary,
        topology_summary=topology_summary,
        kb_summary=kb_summary,
        contacts_summary=contacts_summary,
        hint_section=hint_section,
    )


PLAN_PROMPT = """Based on your investigation, produce your final structured action plan.

Include:
- A 1-3 sentence summary of the situation
- Severity assessment
- Ranked hypotheses for root cause
- Evidence you gathered (tool + finding)
- Questions for the human operator
- Actions to take (create tickets, send notifications, run commands, etc.)

Be specific and actionable."""
