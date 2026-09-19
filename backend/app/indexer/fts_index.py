import sqlite3
import re
from typing import List, Dict, Any, Optional
from app.config import SQLITE_DB_PATH
from app.crawler.models import DocumentChunk, CrawledDocument

class FTSIndex:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            # Table to store master documents
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    url TEXT UNIQUE,
                    domain TEXT,
                    title TEXT,
                    meta_description TEXT,
                    canonical_url TEXT,
                    body_text TEXT,
                    created_at TEXT
                )
            """)

            # SQLite FTS5 virtual table for lexical BM25 indexing
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
                    chunk_id UNINDEXED,
                    doc_id UNINDEXED,
                    url UNINDEXED,
                    domain UNINDEXED,
                    title,
                    text,
                    tokenize='porter unicode61'
                )
            """)
            conn.commit()

    def index_document(self, doc: CrawledDocument, chunks: List[DocumentChunk]):
        with self._get_connection() as conn:
            # Upsert master document
            conn.execute("""
                INSERT INTO documents (id, url, domain, title, meta_description, canonical_url, body_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    url=excluded.url,
                    domain=excluded.domain,
                    title=excluded.title,
                    meta_description=excluded.meta_description,
                    canonical_url=excluded.canonical_url,
                    body_text=excluded.body_text,
                    created_at=excluded.created_at
            """, (
                doc.id, doc.url, doc.domain, doc.title,
                doc.meta_description, doc.canonical_url, doc.body_text, doc.crawled_at
            ))

            # Remove previous chunks for this doc in FTS
            conn.execute("DELETE FROM fts_chunks WHERE doc_id = ?", (doc.id,))

            # Insert new chunks into FTS5
            for chunk in chunks:
                conn.execute("""
                    INSERT INTO fts_chunks (chunk_id, doc_id, url, domain, title, text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.doc_id, chunk.url, chunk.domain, chunk.title, chunk.text
                ))
            conn.commit()

    def search_bm25(self, query: str, limit: int = 50, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        clean_query = self._sanitize_fts_query(query)
        if not clean_query:
            return []

        sql = """
            SELECT 
                chunk_id,
                doc_id,
                url,
                domain,
                title,
                snippet(fts_chunks, 5, '<mark>', '</mark>', '...', 25) as snippet_text,
                bm25(fts_chunks, 2.0, 1.0) as bm25_score
            FROM fts_chunks
            WHERE fts_chunks MATCH ?
        """
        params = [clean_query]

        if domain:
            sql += " AND domain = ?"
            params.append(domain)

        # SQLite FTS5 bm25 assigns lower numbers for better matches (e.g. -2.5 is better than -0.5)
        sql += " ORDER BY bm25_score ASC LIMIT ?"
        params.append(limit)

        results = []
        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            for row in cursor.fetchall():
                results.append({
                    "chunk_id": row["chunk_id"],
                    "doc_id": row["doc_id"],
                    "url": row["url"],
                    "domain": row["domain"],
                    "title": row["title"],
                    "snippet": row["snippet_text"] if row["snippet_text"] else row["title"],
                    "bm25_score": row["bm25_score"]
                })
        return results

    def _sanitize_fts_query(self, query: str) -> str:
        # Keep alphanumeric and spaces, wrap terms in quotes or handle NEAR/AND
        terms = re.findall(r"\w+", query)
        if not terms:
            return ""
        # Match any or all tokens with prefix support
        return " OR ".join(f'"{t}"*' for t in terms)

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunk_count = conn.execute("SELECT COUNT(*) FROM fts_chunks").fetchone()[0]
            return {
                "total_documents": doc_count,
                "total_chunks": chunk_count
            }

fts_index = FTSIndex()
