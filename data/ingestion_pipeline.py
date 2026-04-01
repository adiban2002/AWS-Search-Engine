import os
import logging
from typing import List

from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionPipeline:

    def __init__(self, data_dir: str = "data/documents", chunk_size: int = 500):
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.vector_store = OpenSearchVectorStore()


    def _load_documents(self) -> List[str]:
        documents = []

        for filename in os.listdir(self.data_dir):
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(self.data_dir, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

                if content.strip():
                    documents.append(content)

        logger.info(f"Loaded {len(documents)} documents")
        return documents


    def _chunk_text(self, text: str) -> List[str]:
        chunks = []

        start = 0
        while start < len(text):
            chunk = text[start:start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size

        return chunks

    def run(self):
        documents = self._load_documents()

        total_chunks = 0

        for doc in documents:
            chunks = self._chunk_text(doc)

            for chunk in chunks:
                try:
                    embedding = EmbeddingGenerator.generate_embedding(chunk)

                    self.vector_store.index_document(
                        text=chunk,
                        embedding=embedding,
                        metadata={"source": "ingested"}
                    )

                    total_chunks += 1

                except Exception as e:
                    logger.error(f"[Chunk Error]: {e}", exc_info=True)

        logger.info(f"Total chunks indexed: {total_chunks}")


if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    pipeline.run()