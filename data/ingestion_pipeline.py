import logging
from typing import List, Dict, Any

from data.s3_loader import S3DocumentLoader
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IngestionPipeline:


    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        prefix: str = "documents/"
    ):
        self.loader = S3DocumentLoader()
        self.vector_store = OpenSearchVectorStore()

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.prefix = prefix


    def _chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks


    def _process_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_chunks = []

        for doc in docs:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            chunks = self._chunk_text(text)

            for idx, chunk in enumerate(chunks):
                processed_chunks.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_id": idx
                    }
                })

        logger.info(f"Total chunks created: {len(processed_chunks)}")

        return processed_chunks


    def _index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        success_count = 0

        for chunk in chunks:
            try:
                embedding = EmbeddingGenerator.generate_embedding(chunk["text"])

                self.vector_store.index_document(
                    text=chunk["text"],
                    embedding=embedding,
                    metadata=chunk["metadata"]
                )

                success_count += 1

            except Exception as e:
                logger.error(f"[Chunk Index Error]: {e}", exc_info=True)

        return success_count


    def run(self) -> Dict[str, Any]:
        try:
            logger.info("Starting ingestion pipeline...")

            
            documents = self.loader.load_documents(prefix=self.prefix)

            if not documents:
                raise ValueError("No documents found in S3")

            logger.info(f"Loaded {len(documents)} documents")

           
            chunks = self._process_documents(documents)

            if not chunks:
                raise ValueError("No chunks created")

            
            indexed_count = self._index_chunks(chunks)

            logger.info(f"Successfully indexed {indexed_count} chunks")

            return {
                "status": "success",
                "documents": len(documents),
                "chunks": len(chunks),
                "indexed": indexed_count
            }

        except Exception as e:
            logger.error(f"[Ingestion Pipeline Error]: {e}", exc_info=True)
            raise