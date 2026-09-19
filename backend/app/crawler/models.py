from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CrawledDocument(BaseModel):
    id: str
    url: str
    domain: str
    title: str
    meta_description: str = ""
    canonical_url: Optional[str] = None
    body_text: str
    headers: List[str] = Field(default_factory=list)
    raw_html_length: int = 0
    crawled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    chunk_index: int
    url: str
    domain: str
    title: str
    text: str
    word_count: int
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CrawlRequest(BaseModel):
    urls: List[str]
    max_depth: int = Field(default=1, ge=0, le=3)
    max_pages: int = Field(default=25, ge=1, le=100)
    rate_limit_delay: float = Field(default=0.5, ge=0.1, le=5.0)

class CrawlResponse(BaseModel):
    job_id: str
    status: str
    message: str
    urls: List[str]

class SearchResultItem(BaseModel):
    id: str
    chunk_id: str
    title: str
    url: str
    domain: str
    snippet: str
    score: float
    lexical_rank: Optional[int] = None
    semantic_rank: Optional[int] = None
    timestamp: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    page_size: int
    latency_ms: float
    results: List[SearchResultItem]
