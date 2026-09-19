import pytest
import os
import shutil
import tempfile
from app.crawler.models import CrawledDocument
from app.indexer.chunker import DocumentChunker
from app.indexer.fts_index import FTSIndex

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=10, overlap=2)
    words = [f"word{i}" for i in range(25)]
    doc = CrawledDocument(
        id="test_doc_1",
        url="https://example.com/chunk-test",
        domain="example.com",
        title="Chunk Test",
        body_text=" ".join(words)
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 3
    assert chunks[0].doc_id == "test_doc_1"
    assert chunks[0].chunk_index == 0
    assert chunks[0].title == "Chunk Test"
    assert chunks[0].word_count == 10

def test_fts5_indexing_and_bm25():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_fts.db")

    try:
        fts = FTSIndex(db_path=db_path)
        chunker = DocumentChunker(chunk_size=50, overlap=10)

        doc1 = CrawledDocument(
            id="doc1",
            url="https://fastapi.tiangolo.com",
            domain="fastapi.tiangolo.com",
            title="FastAPI Web Framework",
            body_text="FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints."
        )

        doc2 = CrawledDocument(
            id="doc2",
            url="https://sqlite.org",
            domain="sqlite.org",
            title="SQLite Database Engine",
            body_text="SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured SQL database engine."
        )

        fts.index_document(doc1, chunker.chunk_document(doc1))
        fts.index_document(doc2, chunker.chunk_document(doc2))

        # Search for 'FastAPI'
        results = fts.search_bm25("FastAPI")
        assert len(results) > 0
        assert results[0]["title"] == "FastAPI Web Framework"
        assert "<mark>FastAPI</mark>" in results[0]["snippet"]

        # Search for 'SQLite database'
        results_sql = fts.search_bm25("SQLite database")
        assert len(results_sql) > 0
        assert results_sql[0]["title"] == "SQLite Database Engine"

        # Check stats
        stats = fts.get_stats()
        assert stats["total_documents"] == 2
        assert stats["total_chunks"] == 2

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
