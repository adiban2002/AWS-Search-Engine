import os
import logging
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger(__name__)


class OpenSearchVectorStore:

    def __init__(self):
        self.host = os.getenv("OPENSEARCH_HOST")
        self.username = os.getenv("OPENSEARCH_USERNAME")
        self.password = os.getenv("OPENSEARCH_PASSWORD")
        self.index_name = os.getenv("OPENSEARCH_INDEX", "llmops-index")

        if not all([self.host, self.username, self.password]):
            raise ValueError("Missing OpenSearch credentials")

        self.client = OpenSearch(
            hosts=[{"host": self.host, "port": 443}],
            http_auth=(self.username, self.password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )

    def _create_index(self, dimension: int):

        logger.info(f"Creating index: {self.index_name} (dim={dimension})")

        body = {
            "settings": {
                "index": {"knn": True}
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": dimension
                    },
                    "metadata": {"type": "object"}
                }
            }
        }

        self.client.indices.create(index=self.index_name, body=body)

    def _ensure_index(self, embedding: List[float]):

        dim = len(embedding)

        if not self.client.indices.exists(index=self.index_name):
            self._create_index(dim)
            return

        try:
            mapping = self.client.indices.get(index=self.index_name)
            current_dim = mapping[self.index_name]["mappings"]["properties"]["embedding"]["dimension"]

            if current_dim != dim:
                logger.warning(f"Recreating index (old={current_dim}, new={dim})")
                self.client.indices.delete(index=self.index_name)
                self._create_index(dim)

        except Exception as e:
            logger.error(f"[Index Validation Error]: {e}", exc_info=True)
            raise

    def index_document(self, text: str, embedding: List[float], metadata: Dict[str, Any] = None):

        if not embedding or not isinstance(embedding, list):
            raise ValueError("Invalid embedding")

        self._ensure_index(embedding)

        doc = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        }

        return self.client.index(
            index=self.index_name,
            body=doc,
            refresh=True
        )

    def search(self, embedding: List[float], k: int = 3):

        if not embedding or not isinstance(embedding, list):
            raise ValueError("Invalid embedding")

        query = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": k
                    }
                }
            }
        }

        response = self.client.search(
            index=self.index_name,
            body=query
        )

        hits = response.get("hits", {}).get("hits", [])

        return [
            {
                "text": hit["_source"].get("text"),
                "score": hit.get("_score"),
                "metadata": hit["_source"].get("metadata", {})
            }
            for hit in hits
        ]