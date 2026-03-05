"""GET /api/topology/{service} — service topology."""

from fastapi import APIRouter

from app.tools.registry import TOOL_MAP

router = APIRouter(prefix="/api", tags=["topology"])


@router.get("/topology/{service_name}")
async def get_topology(service_name: str):
    tool = TOOL_MAP["get_topology"]
    result = await tool.execute({"service": service_name})
    return result.data
