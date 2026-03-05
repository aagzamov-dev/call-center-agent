"""Demo command execution tool — allowlisted read-only commands."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult

ALLOWED_COMMANDS = {"df", "top", "free", "ps", "service", "pg_stat_activity", "netstat", "ss"}

COMMAND_OUTPUTS: dict[tuple[str, str], dict] = {
    ("db-prod-01", "df -h"): {
        "exit_code": 0,
        "stdout": (
            "Filesystem      Size  Used Avail Use% Mounted on\n"
            "/dev/sda1        50G   12G   38G  24% /\n"
            "/dev/sdb1       100G   97G  3.0G  97% /var/lib/postgresql\n"
            "tmpfs            16G  512M   16G   4% /dev/shm"
        ),
        "stderr": "",
    },
    ("db-prod-01", "pg_stat_activity"): {
        "exit_code": 0,
        "stdout": (
            "pid  | state  | query_start          | client_addr  | application_name | query\n"
            "-----+--------+----------------------+--------------+------------------+------\n"
            "1234 | active | 2026-03-04 10:30:00  | 10.0.2.15    | payment-service  | SELECT * FROM transactions WHERE...\n"
            "1235 | idle   | 2026-03-04 09:15:00  | 10.0.2.15    | payment-service  | \n"
            "1236 | idle   | 2026-03-04 08:00:00  | 10.0.2.15    | payment-service  | \n"
            "... (180 idle connections from payment-service)\n"
            "2001 | active | 2026-03-04 10:55:00  | 10.0.2.20    | user-service     | INSERT INTO audit_log...\n"
            "2002 | active | 2026-03-04 10:58:00  | 10.0.2.25    | api-gateway      | SELECT 1"
        ),
        "stderr": "",
    },
    ("db-prod-01", "free -h"): {
        "exit_code": 0,
        "stdout": "              total        used        free      shared  buff/cache   available\nMem:           31Gi       22Gi       1.2Gi       512Mi       7.8Gi       8.0Gi\nSwap:         8.0Gi       2.1Gi       5.9Gi",
        "stderr": "",
    },
    ("api-gw-01", "top"): {
        "exit_code": 0,
        "stdout": (
            "top - 11:00:05 up 45 days, load average: 12.34, 10.21, 8.55\n"
            "Tasks: 256 total,   4 running, 252 sleeping\n"
            "%Cpu(s): 91.2 us,  3.1 sy,  0.0 ni,  4.5 id,  0.0 wa\n"
            "MiB Mem :  16384.0 total,    512.0 free,  14336.0 used,   1536.0 buff\n\n"
            "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND\n"
            " 3412 node      20   0 4194304 2.1g  32768 R  87.3 13.1  42:15.67 node /app/server.js\n"
            " 3500 node      20   0 1048576 512m  16384 S   3.2  3.1   5:23.11 node /app/worker.js"
        ),
        "stderr": "",
    },
    ("api-gw-01", "df -h"): {
        "exit_code": 0,
        "stdout": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       50G   18G   32G  36% /\ntmpfs           8.0G  256M  7.8G   4% /dev/shm",
        "stderr": "",
    },
}


class CommandTool(BaseTool):
    name = "run_command"
    description = "Execute a read-only diagnostic command on a host. Allowed: df, top, free, ps, service status, pg_stat_activity, netstat, ss."

    async def execute(self, params: dict) -> ToolResult:
        host = params.get("host", "")
        command = params.get("command", "").strip()

        base_cmd = command.split()[0] if command else ""
        if base_cmd not in ALLOWED_COMMANDS:
            return ToolResult(success=False, error=f"Command '{base_cmd}' not in allowlist: {ALLOWED_COMMANDS}")

        output = COMMAND_OUTPUTS.get((host, command))
        if not output:
            output = {"exit_code": 0, "stdout": f"[mock] {command} on {host}: OK", "stderr": ""}

        return ToolResult(success=True, data={
            "host": host, "command": command, "duration_ms": 120, **output
        })
