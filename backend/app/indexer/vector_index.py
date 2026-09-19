import os
import gc
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_BATCH_SIZE
)
from app.crawler.models import DocumentChunk

logger = logging.getLogger("vector_index")

# Restrict torch thread usage to reduce memory and CPU thrashing
try:
    import torch
    torch.set_num_threads(1)
except ImportError:
    pass

class VectorIndex:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VectorIndex, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        persist_dir: str = CHROMA_PERSIST_DIR,
        model_name: str = EMBEDDING_MODEL_NAME,
        batch_size: int = EMBEDDING_BATCH_SIZE
    ):
        if self._initialized:
            return

        self.persist_dir = persist_dir
        self.model_name = model_name
        self.batch_size = batch_size
        self._model: Optional[SentenceTransformer] = None

        logger.info(f"Initializing ChromaDB Client at {self.persist_dir}")
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False, is_persistent=True)
        )
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        self._initialized = True

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name} (CPU lightweight mode)")
            self._model = SentenceTransformer(self.model_name, device="cpu")
            self._model.eval()
        return self._model

    def add_chunks(self, chunks: List[DocumentChunk]):
        if not chunks:
            return

        # Process in constrained batches to keep peak RAM under 512MB
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            texts = [f"{c.title}: {c.text}" for c in batch]
            ids = [c.chunk_id for c in batch]
            metadatas = [
                {
                    "doc_id": c.doc_id,
                    "url": c.url,
                    "domain": c.domain,
                    "title": c.title,
                    "chunk_index": c.chunk_index
                }
                for c in batch
            ]

            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                normalize_embeddings=True
            ).tolist()

            self.collection.upsert(
                ids=ids,
                documents=[c.text for c in batch],
                embeddings=embeddings,
                metadatas=metadatas
            )

            # Proactive GC to keep RAM minimal
            gc.collect()

    def search_vector(self, query: str, limit: int = 50, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        query_embedding = self.model.encode(
            [query],
            show_progress_bar=False,
            normalize_embeddings=True
        ).tolist()

        where_clause = {"domain": domain} if domain else None

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=limit,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0] if results["documents"] else [""] * len(ids)
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)
            dists = results["distances"][0] if results["distances"] else [0.0] * len(ids)

            for cid, doc_text, meta, dist in zip(ids, docs, metas, dists):
                # Cosine distance: 0 is identical, 2 is opposite. Similarity = 1 - dist/2
                similarity = max(0.0, 1.0 - (dist / 2.0))
                # Generate a short snippet from doc_text
                snippet = doc_text[:200] + ("..." if len(doc_text) > 200 else "")
                formatted.append({
                    "chunk_id": cid,
                    "doc_id": meta.get("doc_id", ""),
                    "url": meta.get("url", ""),
                    "domain": meta.get("domain", ""),
                    "title": meta.get("title", ""),
                    "snippet": snippet,
                    "similarity": similarity,
                    "distance": dist
                })
        return formatted

    def get_count(self) -> int:
        return self.collection.count()

vector_index = VectorIndex()
