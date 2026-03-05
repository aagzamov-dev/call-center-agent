"""GET /api/kb/search — wiki/runbook search."""

from fastapi import APIRouter, Query

from app.tools.registry import TOOL_MAP

router = APIRouter(prefix="/api", tags=["kb"])


@router.get("/kb/search")
async def search_kb(q: str = Query(...)):
    tool = TOOL_MAP["search_wiki"]
    result = await tool.execute({"query": q})
    return result.data
