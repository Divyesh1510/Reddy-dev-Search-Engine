import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, DATA_DIR
from app.api.routes_search import router as search_router
from app.api.routes_crawl import router as crawl_router
from app.api.routes_stats import router as stats_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

app = FastAPI(
    title="Modular Hybrid Search Engine API",
    description="Production-ready search engine with SQLite FTS5 (BM25) lexical index, ChromaDB vector semantic search, RRF ranker, and async crawler.",
    version="1.0.0"
)

# CORS Middleware reading ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(search_router)
app.include_router(crawl_router)
app.include_router(stats_router)

@app.get("/")
async def root():
    return {
        "service": "Modular Hybrid Search Engine",
        "status": "online",
        "data_dir": DATA_DIR,
        "docs_url": "/docs"
    }
