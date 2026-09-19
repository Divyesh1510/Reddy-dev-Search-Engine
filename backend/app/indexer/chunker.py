import re
from typing import List
from app.config import CHUNK_WORD_SIZE, CHUNK_OVERLAP_SIZE
from app.crawler.models import CrawledDocument, DocumentChunk

class DocumentChunker:
    def __init__(self, chunk_size: int = CHUNK_WORD_SIZE, overlap: int = CHUNK_OVERLAP_SIZE):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: CrawledDocument) -> List[DocumentChunk]:
        """
        Splits text into chunks of `chunk_size` words with `overlap` words.
        Attaches document metadata to each chunk.
        """
        words = doc.body_text.split()
        if not words:
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        step = max(1, self.chunk_size - self.overlap)
        chunk_idx = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunk_id = f"{doc.id}_{chunk_idx}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc.id,
                    chunk_index=chunk_idx,
                    url=doc.url,
                    domain=doc.domain,
                    title=doc.title,
                    text=chunk_text,
                    word_count=len(chunk_words)
                )
            )

            if end == len(words):
                break
            start += step
            chunk_idx += 1

        return chunks

default_chunker = DocumentChunker()
