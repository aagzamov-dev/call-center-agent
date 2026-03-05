"""Wiki/KB tool — uses RAG vector search for semantic retrieval."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult


class WikiTool(BaseTool):
    name = "search_wiki"
    description = "Search the internal wiki/runbooks knowledge base using semantic search. Returns the most relevant sections."

    async def execute(self, params: dict) -> ToolResult:
        from app.services.rag_service import search
        query = params.get("query", "")
        top_k = params.get("top_k", 5)
        results = search(query, top_k=top_k)
        return ToolResult(success=True, data={"results": results, "total": len(results)})
