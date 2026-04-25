import logging
import re
from typing import List, Dict, Any
from data.s3_loader import S3DocumentLoader
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, chunk_size=700, chunk_overlap=80, prefix="documents/"):
        self.loader = S3DocumentLoader()
        self.vector_store = OpenSearchVectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.prefix = prefix

    def _chunk_text(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        chunks, current = [], ""
        for s in sentences:
            if not s.strip(): continue
            if len(current) + len(s) <= self.chunk_size:
                current += " " + s
            else:
                if current: chunks.append(current.strip())
                current = current[-self.chunk_overlap:] + " " + s if self.chunk_overlap else s
        
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def run(self):
        logger.info(f"Starting Ingestion Pipeline from prefix: {self.prefix}")
        try:
            docs = self.loader.load_documents(prefix=self.prefix)
            if not docs:
                logger.warning("No documents found in S3 to process.")
                return {"status": "error", "message": "No docs found in S3"}

            total_indexed = 0
            total_files = len(docs)
            
            for idx, doc in enumerate(docs, 1):
                source_name = doc["metadata"].get("source", "Unknown")
                logger.info(f"Processing file {idx}/{total_files}: {source_name}")
                
                chunks = self._chunk_text(doc["text"])
                file_success_count = 0
                
                for i, chunk in enumerate(chunks):
                    try:
                       
                        emb = EmbeddingGenerator.generate_embedding(chunk)
                        
                        
                        self.vector_store.index_document(
                            text=chunk, 
                            embedding=emb, 
                            metadata={**doc["metadata"], "chunk_id": i}
                        )
                        file_success_count += 1
                        total_indexed += 1
                    except Exception as e:
                        logger.error(f" Failed to index chunk {i} of {source_name}: {str(e)}")

                logger.info(f" Finished {source_name}: {file_success_count}/{len(chunks)} chunks indexed.")

            logger.info(f" Pipeline Complete. Total chunks indexed: {total_indexed}")
            return {
                "status": "success", 
                "files_processed": total_files,
                "total_indexed_chunks": total_indexed
            }

        except Exception as e:
            logger.exception(" Critical Pipeline Crash!")
            return {"status": "error", "message": str(e)}