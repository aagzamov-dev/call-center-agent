"""Demo wiki/runbooks knowledge base tool."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

RUNBOOKS: list[dict] = [
    {
        "title": "Runbook: PostgreSQL disk full recovery",
        "snippet": "1. Check WAL archiving status: SELECT * FROM pg_stat_archiver;\n2. Run pg_archivecleanup to remove old WAL files\n3. Check for long-running transactions: SELECT * FROM pg_stat_activity WHERE state != 'idle';\n4. If WAL dir is full, manually archive and clean\n5. Verify replication is healthy after cleanup",
        "tags": ["postgresql", "disk", "wal", "archive", "full"],
    },
    {
        "title": "Runbook: PostgreSQL connection pool exhaustion",
        "snippet": "1. Check pg_stat_activity for idle connections\n2. Identify client applications with too many connections\n3. Restart the leaking application\n4. Consider adding PgBouncer for connection pooling\n5. Review max_connections setting",
        "tags": ["postgresql", "connections", "pool", "pgbouncer"],
    },
    {
        "title": "Runbook: High CPU troubleshooting",
        "snippet": "1. Run 'top' to identify the process using most CPU\n2. Check for runaway queries: SELECT * FROM pg_stat_activity ORDER BY query_start;\n3. Review recent deployments for regressions\n4. Check for cron jobs or batch processes\n5. Scale horizontally if legitimate traffic spike",
        "tags": ["cpu", "performance", "top", "process"],
    },
    {
        "title": "Runbook: Certificate renewal process",
        "snippet": "1. Check cert expiry: openssl x509 -enddate -noout -in /etc/ssl/certs/server.crt\n2. For Let's Encrypt: certbot renew --dry-run\n3. For internal CA: submit CSR to security-team, await signed cert\n4. Deploy new cert: cp new.crt /etc/nginx/ssl/ && nginx -s reload\n5. Verify: openssl s_client -connect hostname:443",
        "tags": ["certificate", "ssl", "tls", "expired", "renewal", "letsencrypt"],
    },
    {
        "title": "Runbook: Network firewall change rollback",
        "snippet": "1. Log into FortiGate: https://fw-mgmt.company.com\n2. Navigate to Policy & Objects > Firewall Policy\n3. Identify recently added/modified rules (check audit log)\n4. Disable or revert the offending rule\n5. Test connectivity: telnet <host> <port>\n6. Document change in change management ticket",
        "tags": ["firewall", "network", "fortigate", "port", "blocked", "connection refused"],
    },
    {
        "title": "Runbook: Service restart procedure",
        "snippet": "1. Notify affected teams via #incidents channel\n2. Check current status: systemctl status <service>\n3. Graceful restart: systemctl restart <service>\n4. Verify health: curl http://localhost:<port>/health\n5. Monitor logs for 5 minutes: journalctl -u <service> -f",
        "tags": ["restart", "service", "systemctl"],
    },
]


class WikiTool(BaseTool):
    name = "search_wiki"
    description = "Search the internal wiki/runbooks knowledge base for troubleshooting procedures."

    async def execute(self, params: dict) -> ToolResult:
        query = params.get("query", "").lower()
        results = []
        for rb in RUNBOOKS:
            score = 0
            words = query.split()
            for w in words:
                if any(w in tag for tag in rb["tags"]):
                    score += 0.3
                if w in rb["title"].lower():
                    score += 0.2
                if w in rb["snippet"].lower():
                    score += 0.1
            if score > 0:
                results.append({**rb, "relevance": round(min(score, 1.0), 2)})
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return ToolResult(success=True, data={"results": results[:3], "total": len(results)})
