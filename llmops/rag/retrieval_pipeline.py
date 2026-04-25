import os
import logging
from typing import List, Dict, Any
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential


from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

class RetrievalPipeline:
    def __init__(self, vector_store=None, top_k=6, min_score=0.45, max_context_chars=2200):
        self.vector_store = vector_store or OpenSearchVectorStore()
        self.top_k = top_k
        self.min_score = min_score
        self.max_context_chars = max_context_chars
        self.model = "gemini-2.0-flash" 

    def _embed_query(self, query: str):
        return EmbeddingGenerator.generate_embedding(query)

    def _retrieve(self, embedding):
        results = self.vector_store.search(embedding, k=self.top_k)
        
       
        results = [r for r in results if (r.get("score") or 0) >= self.min_score]
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

       
        seen = set()
        clean = []
        for r in results:
            text = r["text"].strip()
            if len(text) < 50: continue
            key = text[:150]
            if key not in seen:
                seen.add(key)
                clean.append(r)
        return clean

    def _build_context(self, docs):
        context_parts = []
        total = 0
        for doc in docs:
            text = doc["text"]
            if total + len(text) > self.max_context_chars: break
            context_parts.append(text)
            total += len(text)
        return "\n\n".join(context_parts)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def _generate(self, query, context):
        prompt = f"""
You are an expert AI assistant.
Answer ONLY from the context provided. If not found, say: "I don't have enough information."

Context:
{context}

Question:
{query}

Answer:
"""
        response = client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()

    def run(self, query: str):
        try:
            emb = self._embed_query(query)
            docs = self._retrieve(emb)

            if not docs:
                return {
                    "query": query,
                    "answer": "No relevant information found in the knowledge base.",
                    "documents": []
                }

            context = self._build_context(docs)
            answer = self._generate(query, context)

            return {
                "query": query,
                "answer": answer,
                "documents": docs,
                "context_used": context
            }
        except Exception as e:
            logger.error(f"[RAG Error]: {e}")
            return {
                "query": query,
                "answer": "I'm having trouble connecting to the brain. Please try again later.",
                "documents": []
            }