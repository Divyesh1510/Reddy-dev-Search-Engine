import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.config import SQLITE_DB_PATH

class CrawlJobModel(BaseModel):
    job_id: str
    status: str = Field(..., description="queued | running | completed | failed")
    urls: List[str]
    pages_crawled: int = 0
    chunks_indexed: int = 0
    errors: List[str] = []
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class JobStore:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    urls TEXT NOT NULL,
                    pages_crawled INTEGER DEFAULT 0,
                    chunks_indexed INTEGER DEFAULT 0,
                    errors TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                )
            """)
            conn.commit()

    def create_job(self, urls: List[str]) -> CrawlJobModel:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        job = CrawlJobModel(
            job_id=job_id,
            status="queued",
            urls=urls,
            pages_crawled=0,
            chunks_indexed=0,
            errors=[],
            created_at=now
        )
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO crawl_jobs (job_id, status, urls, pages_crawled, chunks_indexed, errors, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (job.job_id, job.status, json.dumps(job.urls), job.pages_crawled, job.chunks_indexed, json.dumps(job.errors), job.created_at)
            )
            conn.commit()
        return job

    def get_job(self, job_id: str) -> Optional[CrawlJobModel]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM crawl_jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return CrawlJobModel(
                job_id=row["job_id"],
                status=row["status"],
                urls=json.loads(row["urls"]),
                pages_crawled=row["pages_crawled"],
                chunks_indexed=row["chunks_indexed"],
                errors=json.loads(row["errors"]) if row["errors"] else [],
                created_at=row["created_at"],
                started_at=row["started_at"],
                completed_at=row["completed_at"]
            )

    def update_job_status(self, job_id: str, status: str, **kwargs):
        updates = ["status = ?"]
        params = [status]
        now = datetime.now(timezone.utc).isoformat()

        if status == "running" and "started_at" not in kwargs:
            updates.append("started_at = ?")
            params.append(now)
        elif status in ("completed", "failed") and "completed_at" not in kwargs:
            updates.append("completed_at = ?")
            params.append(now)

        for key, val in kwargs.items():
            if key in ("pages_crawled", "chunks_indexed"):
                updates.append(f"{key} = ?")
                params.append(val)
            elif key in ("errors", "urls"):
                updates.append(f"{key} = ?")
                params.append(json.dumps(val))
            elif key in ("started_at", "completed_at"):
                updates.append(f"{key} = ?")
                params.append(val)

        params.append(job_id)
        sql = f"UPDATE crawl_jobs SET {', '.join(updates)} WHERE job_id = ?"
        with self._get_connection() as conn:
            conn.execute(sql, params)
            conn.commit()

    def list_jobs(self, limit: int = 50) -> List[CrawlJobModel]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM crawl_jobs ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                CrawlJobModel(
                    job_id=row["job_id"],
                    status=row["status"],
                    urls=json.loads(row["urls"]),
                    pages_crawled=row["pages_crawled"],
                    chunks_indexed=row["chunks_indexed"],
                    errors=json.loads(row["errors"]) if row["errors"] else [],
                    created_at=row["created_at"],
                    started_at=row["started_at"],
                    completed_at=row["completed_at"]
                )
                for row in rows
            ]

job_store = JobStore()
