import os
import logging
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger(__name__)

class OpenSearchVectorStore:
    def __init__(self):
        raw_host = os.getenv("OPENSEARCH_HOST")
        if raw_host:
            self.host = raw_host.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
        else:
            self.host = None
            
        self.username = os.getenv("OPENSEARCH_USERNAME", "admin")
        self.password = os.getenv("OPENSEARCH_PASSWORD")
        self.index_name = os.getenv("OPENSEARCH_INDEX", "llmops-index")

        if not all([self.host, self.username, self.password]):
            logger.error("Missing OpenSearch credentials in environment variables!")
            raise ValueError("Missing OpenSearch credentials in .env or Kubernetes Secrets")

        try:
            self.client = OpenSearch(
                hosts=[{'host': self.host, 'port': 443}],
                http_auth=(self.username, self.password),
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=60, 
                max_retries=5,
                retry_on_timeout=True
            )
            logger.info(f"OpenSearch client initialized for IPv4 host: {self.host}")
        except Exception as e:
            logger.error(f"Failed to create OpenSearch client: {e}")
            raise

        self.index_validated = False

    def _create_index(self, dimension: int):
        logger.info(f"Creating k-NN index: {self.index_name} (dim={dimension})")
        body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": "100"
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": "l2",
                            "engine": "nmslib"
                        }
                    },
                    "metadata": {"type": "object"}
                }
            }
        }
        try:
            self.client.indices.create(index=self.index_name, body=body)
            logger.info(f"Index {self.index_name} created successfully.")
        except Exception as e:
            logger.error(f"Error creating index: {e}")

    def _ensure_index(self, embedding: List[float]):
        if self.index_validated:
            return

        dim = len(embedding)
        try:
            if not self.client.indices.exists(index=self.index_name):
                self._create_index(dim)
            else:
                mapping = self.client.indices.get(index=self.index_name)
                try:
                    current_dim = mapping[self.index_name]["mappings"]["properties"]["embedding"]["dimension"]
                    if current_dim != dim:
                        logger.warning(f"Dimension mismatch! Recreating index {self.index_name}.")
                        self.client.indices.delete(index=self.index_name)
                        self._create_index(dim)
                except KeyError:
                    logger.error("Could not verify index dimensions.")
            
            self.index_validated = True
        except Exception as e:
            logger.error(f"Index validation failed: {e}")

    def index_document(self, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        self._ensure_index(embedding)
        doc = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        try:
            return self.client.index(index=self.index_name, body=doc, refresh=True)
        except Exception as e:
            logger.error(f"Failed to index document: {e}")

    def search(self, embedding: List[float], k: int = 3):
        """ভেক্টর সার্চ"""
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
        try:
            response = self.client.search(index=self.index_name, body=query)
            hits = response.get("hits", {}).get("hits", [])
            return [
                {
                    "text": hit["_source"].get("text"),
                    "score": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {})
                }
                for hit in hits
            ]
        except Exception as e:
            logger.error(f"Search error in OpenSearch: {e}")
            return []