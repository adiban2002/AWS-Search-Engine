from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService


class SearchService:

    @staticmethod
    def search(query: str):
        try:
            embedding = EmbeddingService.get_embedding(query)

            if embedding is None:
                return {"error": "Embedding failed"}

            context = RAGService.retrieve_context(query)

            answer = RAGService.generate_answer(query, context)

            return {
                "query": query,
                "answer": answer,
                "context_used": context
            }

        except Exception as e:
            print(f"[Search Error]: {e}")
            return {"error": "Search failed"}