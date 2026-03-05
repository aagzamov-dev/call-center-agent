"""Knowledge Base router — semantic search + admin CRUD for documents."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import rag_service

router = APIRouter(prefix="/api", tags=["kb"])


# ── Search ─────────────────────────────────────────────────────────────

@router.get("/kb/search")
async def search_kb(q: str = Query(...), top_k: int = Query(5, ge=1, le=20)):
    results = rag_service.search(q, top_k=top_k)
    return {"results": results, "total": len(results)}


# ── Admin CRUD ─────────────────────────────────────────────────────────

class SectionModel(BaseModel):
    heading: str
    content: str


class DocumentCreate(BaseModel):
    title: str
    category: str = ""
    tags: list[str] = []
    sections: list[SectionModel]


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    sections: list[SectionModel] | None = None


@router.get("/kb/documents")
async def list_documents():
    return {"documents": rag_service.list_documents()}


@router.get("/kb/documents/{doc_id}")
async def get_document(doc_id: str):
    doc = rag_service.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.post("/kb/documents", status_code=201)
async def create_document(body: DocumentCreate):
    doc = rag_service.add_document(body.model_dump())
    return {"document": doc, "message": "Document added and index rebuilt"}


@router.put("/kb/documents/{doc_id}")
async def update_document(doc_id: str, body: DocumentUpdate):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if "sections" in updates:
        updates["sections"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in updates["sections"]]
    doc = rag_service.update_document(doc_id, updates)
    if not doc:
        raise HTTPException(404, "Document not found")
    return {"document": doc, "message": "Document updated and index rebuilt"}


@router.delete("/kb/documents/{doc_id}")
async def delete_document(doc_id: str):
    if not rag_service.delete_document(doc_id):
        raise HTTPException(404, "Document not found")
    return {"message": "Document deleted and index rebuilt"}


@router.post("/kb/reindex")
async def reindex():
    count = rag_service.rebuild_index()
    return {"message": f"Index rebuilt with {count} chunks"}
