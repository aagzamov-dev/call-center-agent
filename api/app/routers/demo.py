"""POST /api/demo/scenarios/{name} — seed and start demo scenarios."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services import incident_service as svc

router = APIRouter(prefix="/api", tags=["demo"])

SCENARIOS = {
    "disk_full": {
        "alert_id": "zabbix-12345",
        "host": "db-prod-01",
        "service": "postgresql",
        "severity": "critical",
        "title": "Disk usage > 95% on /var/lib/postgresql",
        "description": "Partition /var/lib/postgresql is 97% full. WAL archiving may be failing.",
        "tags": {"env": "production", "team": "dba"},
    },
    "cpu_spike": {
        "alert_id": "zabbix-22001",
        "host": "api-gw-01",
        "service": "api-gateway",
        "severity": "high",
        "title": "CPU > 90% sustained for 15 minutes on api-gw-01",
        "description": "API gateway CPU usage has been above 90% for 15 minutes. Request latency increasing.",
        "tags": {"env": "production", "team": "platform"},
    },
    "db_connections": {
        "alert_id": "zabbix-33001",
        "host": "db-prod-01",
        "service": "postgresql",
        "severity": "critical",
        "title": "PostgreSQL max_connections (200) reached on db-prod-01",
        "description": "All 200 connection slots are in use. New connections are being refused.",
        "tags": {"env": "production", "team": "dba"},
    },
    "network_blocked": {
        "alert_id": "zabbix-44001",
        "host": "api-gw-01",
        "service": "api-gateway",
        "severity": "critical",
        "title": "Connection refused on port 5432 from api-gw-01 to db-prod-01",
        "description": "API gateway cannot reach the database. All queries are failing.",
        "tags": {"env": "production", "team": "network"},
    },
    "cert_expired": {
        "alert_id": "zabbix-55001",
        "host": "api-gw-01",
        "service": "api-gateway",
        "severity": "high",
        "title": "TLS certificate expired on api-gw-01 (*.company.com)",
        "description": "SSL certificate has expired. Clients are receiving certificate errors.",
        "tags": {"env": "production", "team": "security"},
    },
}


@router.post("/demo/scenarios/{name}", status_code=201)
async def run_scenario(name: str, db: AsyncSession = Depends(get_session)):
    scenario = SCENARIOS.get(name)
    if not scenario:
        raise HTTPException(400, f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")

    # Create incident
    incident = await svc.create_incident(
        db,
        title=f"{scenario['severity'].upper()}: {scenario['title']}",
        severity=scenario["severity"],
        host=scenario["host"],
        service=scenario["service"],
    )

    # Add initial alert event
    await svc.add_event(
        db,
        incident_id=incident.id,
        kind="alert",
        actor="system",
        summary=f"Alert received: {scenario['title']}",
        data=scenario,
    )

    return {
        "incident_id": incident.id,
        "scenario": name,
        "message": f"Scenario '{name}' started. Alert injected for {scenario['host']}.",
    }


@router.get("/demo/scenarios")
async def list_scenarios():
    return {"scenarios": list(SCENARIOS.keys())}
