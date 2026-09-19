from typing import Optional
from fastapi import APIRouter, Query
from app.engine.search_engine import search_engine
from app.crawler.models import SearchResponse

router = APIRouter(tags=["Search"])

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    mode: str = Query("hybrid", regex="^(hybrid|lexical|semantic)$", description="Retrieval mode"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Results per page")
):
    """
    Executes hybrid RRF, lexical BM25, or semantic vector search.
    """
    return search_engine.search(
        query=q,
        mode=mode,
        domain=domain,
        page=page,
        page_size=page_size
    )

@router.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=1, description="Query prefix for autocomplete")
):
    """
    Returns query auto-suggestions based on indexed titles and terms.
    """
    candidates = search_engine.fts.search_bm25(q, limit=5)
    suggestions = list({c["title"] for c in candidates if c.get("title")})
    return {"query": q, "suggestions": suggestions[:5]}
