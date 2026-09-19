import pytest
from app.engine.hybrid_ranker import HybridRanker
from app.engine.query_parser import QueryParser

def test_query_parser():
    qp = QueryParser()
    res = qp.parse("site:python.org modern search engine tutorial")
    assert res["domain_filter"] == "python.org"
    assert "modern" in res["lexical_query"]
    assert "search" in res["lexical_query"]

def test_hybrid_ranker_rrf():
    ranker = HybridRanker(rrf_k=60, weight_lexical=0.5, weight_semantic=0.5)

    lexical_items = [
        {"chunk_id": "c1", "title": "Result 1", "snippet": "Text 1", "url": "http://a.com"},
        {"chunk_id": "c2", "title": "Result 2", "snippet": "Text 2", "url": "http://b.com"},
    ]
    semantic_items = [
        {"chunk_id": "c2", "title": "Result 2", "snippet": "Text 2", "url": "http://b.com"},
        {"chunk_id": "c3", "title": "Result 3", "snippet": "Text 3", "url": "http://c.com"},
    ]

    fused = ranker.fuse_ranks(lexical_items, semantic_items)
    assert len(fused) == 3
    # c2 appeared in both lexical (#2) and semantic (#1), so it should rank highest!
    assert fused[0]["chunk_id"] == "c2"
    assert fused[0]["lexical_rank"] == 2
    assert fused[0]["semantic_rank"] == 1
