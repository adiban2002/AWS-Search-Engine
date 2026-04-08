import logging
import re
from typing import List, Dict, Any

from data.s3_loader import S3DocumentLoader
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IngestionPipeline:
    """
    Production-grade ingestion:
    S3 → Semantic Chunking → Embedding → OpenSearch
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        prefix: str = "documents/"
    ):
        self.loader = S3DocumentLoader()
        self.vector_store = OpenSearchVectorStore()

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.prefix = prefix

    # -----------------------------
    # 🔥 SMART SENTENCE CHUNKING
    # -----------------------------
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _chunk_text(self, text: str) -> List[str]:
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())

                # overlap handling
                overlap_text = current_chunk[-self.chunk_overlap:]
                current_chunk = overlap_text + " " + sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    # -----------------------------
    def _process_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []

        for doc in docs:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            chunks = self._chunk_text(text)

            for i, chunk in enumerate(chunks):
                processed.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_id": i
                    }
                })

        logger.info(f"Total chunks created: {len(processed)}")
        return processed

    # -----------------------------
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
                logger.error(f"[Index Error]: {e}", exc_info=True)

        return success

    # -----------------------------
    def run(self) -> Dict[str, Any]:
        logger.info("Starting ingestion pipeline...")

        docs = self.loader.load_documents(prefix=self.prefix)

        if not docs:
            raise ValueError("No documents found in S3")

        logger.info(f"Loaded {len(docs)} documents")

        chunks = self._process_documents(docs)

        indexed = self._index_chunks(chunks)

        return {
            "status": "success",
            "documents": len(docs),
            "chunks": len(chunks),
            "indexed": indexed
        }