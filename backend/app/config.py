import os
from pathlib import Path
from typing import List

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

# Ensure storage directories exist
os.makedirs(DATA_DIR, exist_ok=True)
SQLITE_DB_PATH = os.path.join(DATA_DIR, "search.db")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "chroma")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# CORS Configuration
_allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
if _allowed_origins_raw == "*":
    ALLOWED_ORIGINS: List[str] = ["*"]
else:
    ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in _allowed_origins_raw.split(",") if origin.strip()]

# Embedding Model Configuration (Lightweight CPU)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "16"))
MAX_EMBEDDING_WORKERS = 1

# Crawler Configuration
CRAWLER_USER_AGENT = os.getenv("CRAWLER_USER_AGENT", "Mozilla/5.0 (compatible; ModularSearchEngineBot/1.0; +https://example.com/bot)")
DEFAULT_CRAWL_DELAY = float(os.getenv("DEFAULT_CRAWL_DELAY", "0.5"))
DEFAULT_REQUEST_TIMEOUT = float(os.getenv("DEFAULT_REQUEST_TIMEOUT", "10.0"))
MAX_CRAWL_RETRIES = int(os.getenv("MAX_CRAWL_RETRIES", "3"))

# Indexing & Chunking Configuration
CHUNK_WORD_SIZE = int(os.getenv("CHUNK_WORD_SIZE", "500"))
CHUNK_OVERLAP_SIZE = int(os.getenv("CHUNK_OVERLAP_SIZE", "50"))

# Search & Ranking Configuration
RRF_K = int(os.getenv("RRF_K", "60"))
WEIGHT_LEXICAL = float(os.getenv("WEIGHT_LEXICAL", "0.5"))
WEIGHT_SEMANTIC = float(os.getenv("WEIGHT_SEMANTIC", "0.5"))
