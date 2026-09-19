import os
from fastapi import APIRouter
from app.indexer.index_manager import index_manager
from app.jobs import job_store
from app.config import DATA_DIR, SQLITE_DB_PATH, CHROMA_PERSIST_DIR

router = APIRouter(tags=["Statistics & Health"])

def get_directory_size(path: str) -> int:
    total = 0
    if os.path.exists(path):
        if os.path.isfile(path):
            return os.path.getsize(path)
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if not os.path.islink(fp):
                    total += os.path.getsize(fp)
    return total

@router.get("/stats")
async def get_stats():
    """
    Returns total indexed documents, chunks, storage footprint, and active crawl jobs.
    """
    index_stats = index_manager.get_index_stats()
    sqlite_size = get_directory_size(SQLITE_DB_PATH)
    chroma_size = get_directory_size(CHROMA_PERSIST_DIR)
    total_storage_bytes = sqlite_size + chroma_size

    recent_jobs = job_store.list_jobs(limit=5)
    active_jobs = [j for j in recent_jobs if j.status in ("queued", "running")]

    return {
        "index": index_stats,
        "storage": {
            "data_dir": DATA_DIR,
            "sqlite_bytes": sqlite_size,
            "chroma_bytes": chroma_size,
            "total_bytes": total_storage_bytes,
            "total_mb": round(total_storage_bytes / (1024 * 1024), 2)
        },
        "crawler": {
            "active_jobs_count": len(active_jobs),
            "recent_jobs": recent_jobs
        }
    }
