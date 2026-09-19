import logging
from typing import List, Dict, Any
from app.crawler.models import CrawledDocument, DocumentChunk
from app.indexer.chunker import default_chunker
from app.indexer.fts_index import fts_index
from app.indexer.vector_index import vector_index

logger = logging.getLogger("index_manager")

class IndexManager:
    def __init__(self):
        self.chunker = default_chunker
        self.fts = fts_index
        self.vector = vector_index

    def ingest_document(self, doc: CrawledDocument) -> List[DocumentChunk]:
        """
        Chunks the document and writes it simultaneously to SQLite FTS5 and ChromaDB.
        """
        chunks = self.chunker.chunk_document(doc)
        if not chunks:
            logger.warning(f"No chunks generated for document {doc.id} ({doc.url})")
            return []

        # 1. Store and index in SQLite FTS5
        self.fts.index_document(doc, chunks)

        # 2. Store and index in ChromaDB
        self.vector.add_chunks(chunks)

        logger.info(f"Successfully indexed document {doc.id} with {len(chunks)} chunks.")
        return chunks

    def get_index_stats(self) -> Dict[str, Any]:
        fts_stats = self.fts.get_stats()
        vector_count = self.vector.get_count()
        return {
            "total_documents": fts_stats["total_documents"],
            "total_fts_chunks": fts_stats["total_chunks"],
            "total_vector_chunks": vector_count,
            "status": "healthy"
        }

index_manager = IndexManager()
