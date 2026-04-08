import logging
from typing import List, Dict, Any, Optional
from google import genai
import os

from tenacity import retry, stop_after_attempt, wait_exponential

from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Missing Gemini API Key")

client = genai.Client(api_key=API_KEY)


class RetrievalPipeline:
    """
    Production-grade RAG pipeline
    """

    def __init__(
        self,
        vector_store: Optional[OpenSearchVectorStore] = None,
        top_k: int = 5,
        min_score: float = 0.4,
        max_context_chars: int = 3000,
        model_name: str = "gemini-2.5-flash"
    ):
        self.vector_store = vector_store or OpenSearchVectorStore()
        self.top_k = top_k
        self.min_score = min_score
        self.max_context_chars = max_context_chars
        self.model_name = model_name

    # -----------------------------
    # 🔹 EMBEDDING
    # -----------------------------
    def _embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        return EmbeddingGenerator.generate_embedding(query)

    # -----------------------------
    # 🔹 RETRIEVAL (FILTER + SORT)
    # -----------------------------
    def _retrieve(self, embedding: List[float]) -> List[Dict[str, Any]]:
        results = self.vector_store.search(embedding, k=self.top_k)

        if not results:
            logger.warning("No documents retrieved")

        # 🔥 Filter low-quality results
        filtered = [
            r for r in results
            if (r.get("score") or 0) >= self.min_score
        ]

        # 🔥 Sort best first
        filtered.sort(key=lambda x: x.get("score", 0), reverse=True)

        return filtered

    # -----------------------------
    # 🔹 CONTEXT BUILDING
    # -----------------------------
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        total_length = 0

        for doc in docs:
            text = doc.get("text", "").strip()

            if not text:
                continue

            if total_length + len(text) > self.max_context_chars:
                break

            context_parts.append(text)
            total_length += len(text)

        context = "\n\n".join(context_parts)

        if not context:
            logger.warning("Empty context generated")

        return context

    # -----------------------------
    # 🔥 LLM CALL WITH RETRY
    # -----------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def _generate_answer(self, query: str, context: str) -> str:

        prompt = f"""
You are a highly intelligent AI assistant.

Rules:
- Answer ONLY from the provided context
- If the answer is not present, say: "I don't have enough information"
- Keep answer clear, structured, and concise

---------------------
Context:
{context}
---------------------

Question:
{query}

Answer:
"""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Empty response from LLM")

            return response.text.strip()

        except Exception as e:
            logger.error(f"[LLM Error]: {e}", exc_info=True)
            raise

    # -----------------------------
    # 🔹 MAIN PIPELINE
    # -----------------------------
    def run(self, query: str) -> Dict[str, Any]:
        try:
            embedding = self._embed_query(query)

            documents = self._retrieve(embedding)

            if not documents:
                return {
                    "query": query,
                    "answer": "No relevant information found",
                    "documents": []
                }

            context = self._build_context(documents)

            answer = self._generate_answer(query, context)

            return {
                "query": query,
                "answer": answer,
                "documents": documents,
                "context_used": context
            }

        except Exception as e:
            logger.error(f"[RAG Pipeline Error]: {e}", exc_info=True)

            return {
                "query": query,
                "answer": "Temporary issue with AI model. Please try again.",
                "documents": []
            }