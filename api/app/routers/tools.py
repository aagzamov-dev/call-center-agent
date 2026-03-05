"""POST /api/tools/exec — read-only command execution."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.tools.registry import TOOL_MAP

router = APIRouter(prefix="/api", tags=["tools"])


class ToolExecRequest(BaseModel):
    host: str
    command: str


@router.post("/tools/exec")
async def execute_tool(body: ToolExecRequest):
    tool = TOOL_MAP["run_command"]
    result = await tool.execute({"host": body.host, "command": body.command})
    if not result.success:
        from fastapi import HTTPException
        raise HTTPException(400, result.error)
    return result.data
