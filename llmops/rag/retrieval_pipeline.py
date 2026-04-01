import logging
from typing import List, Dict, Any, Optional
from google import genai
import os

from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Missing Gemini API Key")

genai_client = genai.Client(api_key=API_KEY)


class RetrievalPipeline:

    def __init__(
        self,
        vector_store: Optional[OpenSearchVectorStore] = None,
        top_k: int = 5,
        max_context_chars: int = 4000,
        model_name: str = "gemini-2.5-flash"
    ):
        self.vector_store = vector_store or OpenSearchVectorStore()
        self.top_k = top_k
        self.max_context_chars = max_context_chars
        self.model_name = model_name

    def _embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        return EmbeddingGenerator.generate_embedding(query)

    def _retrieve(self, embedding: List[float]) -> List[Dict[str, Any]]:
        results = self.vector_store.search(embedding, k=self.top_k)

        if not results:
            logger.warning("No documents retrieved")

        return results

    def _build_context(self, docs: List[Dict[str, Any]]) -> str:

        if not docs:
            return ""

        docs = sorted(docs, key=lambda x: x.get("score", 0), reverse=True)

        context_parts = []
        total_length = 0

        for doc in docs:
            text = (doc.get("text") or "").strip()

            if not text:
                continue

            if total_length + len(text) > self.max_context_chars:
                break

            context_parts.append(text)
            total_length += len(text)

        context = "\n\n".join(context_parts)

        if not context:
            logger.warning("Context is empty after processing")

        return context

    def _generate_answer(self, query: str, context: str) -> str:

        prompt = f"""
You are an intelligent AI assistant.

Instructions:
- Use ONLY the provided context
- If answer is not present, say: "I don't have enough information"
- Keep answer clear, concise, and structured

Context:
{context}

Question:
{query}

Answer:
"""

        try:
            response = genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return (response.text or "").strip()

        except Exception as e:
            logger.error(f"[LLM Error]: {e}", exc_info=True)
            raise

    def run(self, query: str) -> Dict[str, Any]:

        try:
            embedding = self._embed_query(query)

            documents = self._retrieve(embedding)

            if not documents:
                return {
                    "query": query,
                    "answer": "I couldn't find relevant information in the database.",
                    "documents": [],
                    "context_used": ""
                }

            context = self._build_context(documents)

            if not context:
                return {
                    "query": query,
                    "answer": "I couldn't build enough context to answer the question.",
                    "documents": documents,
                    "context_used": ""
                }

            answer = self._generate_answer(query, context)

            return {
                "query": query,
                "answer": answer,
                "documents": documents,
                "context_used": context
            }

        except Exception as e:
            logger.error(f"[RAG Pipeline Error]: {e}", exc_info=True)
            raise