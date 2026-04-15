import logging
import re
from typing import List, Dict, Any

from data.s3_loader import S3DocumentLoader
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IngestionPipeline:

    def __init__(self, chunk_size=700, chunk_overlap=80, prefix="documents/"):
        self.loader = S3DocumentLoader()
        self.vector_store = OpenSearchVectorStore()

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.prefix = prefix

    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    
    def _chunk_text(self, text: str) -> List[str]:
        sentences = self._split_sentences(text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += " " + sentence
            else:
                if current.strip():
                    chunks.append(current.strip())

               
                overlap = current[-self.chunk_overlap:] if current else ""
                current = overlap + " " + sentence

        if current.strip():
            chunks.append(current.strip())

      
        unique_chunks = []
        seen = set()

        for chunk in chunks:
            key = chunk[:200]  
            if key not in seen:
                seen.add(key)
                unique_chunks.append(chunk)

        return unique_chunks

    def _process_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []

        for doc in docs:
            text = doc["text"]
            metadata = doc["metadata"]

            chunks = self._chunk_text(text)

            for i, chunk in enumerate(chunks):
                processed.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_id": i
                    }
                })

        logger.info(f"Chunks created: {len(processed)}")
        return processed

    def _index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        success = 0

        for chunk in chunks:
            try:
                embedding = EmbeddingGenerator.generate_embedding(chunk["text"])

                self.vector_store.index_document(
                    text=chunk["text"],
                    embedding=embedding,
                    metadata=chunk["metadata"]
                )

                success += 1

            except Exception as e:
                logger.error(f"[Index Error]: {e}")

        return success

    def run(self):
        logger.info("Starting ingestion...")

        docs = self.loader.load_documents(prefix=self.prefix)

        if not docs:
            raise ValueError("No documents found")

        chunks = self._process_documents(docs)

        indexed = self._index_chunks(chunks)

        return {
            "status": "success",
            "documents": len(docs),
            "chunks": len(chunks),
            "indexed": indexed
        }