import logging
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.crawler.models import CrawlRequest, CrawlResponse, CrawledDocument
from app.crawler.crawler import AsyncCrawler
from app.indexer.index_manager import index_manager
from app.jobs import job_store, CrawlJobModel

logger = logging.getLogger("routes_crawl")
router = APIRouter(prefix="/crawl", tags=["Crawler & Ingestion"])

async def _crawl_worker(job_id: str, request: CrawlRequest):
    logger.info(f"Starting background crawl job {job_id} for URLs: {request.urls}")
    job_store.update_job_status(job_id, "running")

    pages_crawled = 0
    chunks_indexed = 0
    errors = []

    async def on_doc_crawled(doc: CrawledDocument):
        nonlocal pages_crawled, chunks_indexed
        pages_crawled += 1
        try:
            chunks = index_manager.ingest_document(doc)
            chunks_indexed += len(chunks)
            job_store.update_job_status(
                job_id,
                "running",
                pages_crawled=pages_crawled,
                chunks_indexed=chunks_indexed
            )
        except Exception as e:
            err = f"Failed indexing {doc.url}: {str(e)}"
            logger.error(err)
            errors.append(err)

    def on_crawl_error(err_msg: str):
        errors.append(err_msg)

    crawler = AsyncCrawler(
        request_delay=request.rate_limit_delay
    )

    try:
        await crawler.crawl_urls(
            seed_urls=request.urls,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            on_document_crawled=on_doc_crawled,
            on_error=on_crawl_error
        )
        job_store.update_job_status(
            job_id,
            "completed",
            pages_crawled=pages_crawled,
            chunks_indexed=chunks_indexed,
            errors=errors
        )
        logger.info(f"Crawl job {job_id} completed: {pages_crawled} pages, {chunks_indexed} chunks.")
    except Exception as e:
        logger.error(f"Crawl job {job_id} failed: {e}")
        errors.append(str(e))
        job_store.update_job_status(
            job_id,
            "failed",
            pages_crawled=pages_crawled,
            chunks_indexed=chunks_indexed,
            errors=errors
        )

@router.post("", response_model=CrawlResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks
):
    """
    Submits an asynchronous crawl job. Returns 202 Accepted with job_id for status polling.
    """
    if not request.urls:
        raise HTTPException(status_code=400, detail="Must provide at least one URL to crawl.")

    job = job_store.create_job(urls=request.urls)
    background_tasks.add_task(_crawl_worker, job.job_id, request)

    return CrawlResponse(
        job_id=job.job_id,
        status="queued",
        message="Crawl job accepted and running in background.",
        urls=request.urls
    )

@router.get("/status/{job_id}", response_model=CrawlJobModel)
async def get_crawl_status(job_id: str):
    """
    Polls status and progress of a background crawl job.
    """
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    return job

@router.get("/jobs", response_model=list[CrawlJobModel])
async def list_crawl_jobs(limit: int = 20):
    """
    Lists recent crawl jobs and their statuses.
    """
    return job_store.list_jobs(limit=limit)
