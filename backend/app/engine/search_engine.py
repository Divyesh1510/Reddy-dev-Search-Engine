import time
import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.indexer.fts_index import fts_index
from app.indexer.vector_index import vector_index
from app.engine.query_parser import query_parser
from app.engine.hybrid_ranker import hybrid_ranker
from app.crawler.models import SearchResponse, SearchResultItem

class SearchEngine:
    def __init__(self):
        self.fts = fts_index
        self.vector = vector_index
        self.parser = query_parser
        self.ranker = hybrid_ranker

    def _highlight_snippet(self, text: str, query_tokens: List[str]) -> str:
        if "<mark>" in text:
            return text
        highlighted = text
        for token in query_tokens:
            if len(token) > 2:
                pattern = re.compile(rf"\b({re.escape(token)})\b", re.IGNORECASE)
                highlighted = pattern.sub(r"<mark>\1</mark>", highlighted)
        return highlighted

    def search(
        self,
        query: str,
        mode: str = "hybrid",
        domain: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> SearchResponse:
        start_time = time.perf_counter()

        parsed = self.parser.parse(query)
        effective_domain = domain or parsed.get("domain_filter")

        lexical_query = parsed["lexical_query"]
        semantic_query = parsed["semantic_query"]
        tokens = parsed["tokens"]

        candidate_limit = max(50, page * page_size * 2)
        candidates: List[Dict[str, Any]] = []

        if mode == "lexical":
            candidates = self.fts.search_bm25(lexical_query, limit=candidate_limit, domain=effective_domain)
            for item in candidates:
                # Invert BM25 score for display
                raw = item.get("bm25_score", 0.0)
                item["score"] = round(abs(raw), 4)
                item["snippet"] = self._highlight_snippet(item["snippet"], tokens)
        elif mode == "semantic":
            candidates = self.vector.search_vector(semantic_query, limit=candidate_limit, domain=effective_domain)
            for item in candidates:
                item["score"] = round(item.get("similarity", 0.0), 4)
                item["snippet"] = self._highlight_snippet(item["snippet"], tokens)
        else:
            # Hybrid search
            lexical_results = self.fts.search_bm25(lexical_query, limit=candidate_limit, domain=effective_domain)
            semantic_results = self.vector.search_vector(semantic_query, limit=candidate_limit, domain=effective_domain)

            candidates = self.ranker.fuse_ranks(lexical_results, semantic_results, top_k=candidate_limit)
            for item in candidates:
                item["snippet"] = self._highlight_snippet(item["snippet"], tokens)

        # Deduplicate to distinct URLs (keeping best-scoring chunk per URL)
        seen_urls = set()
        deduped_candidates: List[Dict[str, Any]] = []
        for c in candidates:
            url = c.get("url")
            if url not in seen_urls:
                seen_urls.add(url)
                deduped_candidates.append(c)

        # Pagination
        total_results = len(deduped_candidates)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = deduped_candidates[start_idx:end_idx]

        results = [
            SearchResultItem(
                id=item.get("doc_id", item.get("chunk_id", "")),
                chunk_id=item.get("chunk_id", ""),
                title=item.get("title", "Untitled"),
                url=item.get("url", ""),
                domain=item.get("domain", ""),
                snippet=item.get("snippet", ""),
                score=item.get("score", 0.0),
                lexical_rank=item.get("lexical_rank"),
                semantic_rank=item.get("semantic_rank"),
                timestamp=item.get("created_at", datetime.now(timezone.utc).isoformat())
            )
            for item in page_items
        ]

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return SearchResponse(
            query=query,
            total_results=total_results,
            page=page,
            page_size=page_size,
            latency_ms=latency_ms,
            results=results
        )

search_engine = SearchEngine()
