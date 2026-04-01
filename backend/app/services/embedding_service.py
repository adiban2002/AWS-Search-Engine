from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.rag_service import RAGService


class SearchService:

    @staticmethod
    def search(query: str):
        try:
            if not query:
                return {"error": "Query cannot be empty"}

            embedding = EmbeddingService.get_embedding(query)


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