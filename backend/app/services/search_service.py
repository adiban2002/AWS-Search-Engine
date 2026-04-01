from backend.app.services.rag_service import RAGService


class SearchService:

    @staticmethod
    def search(query: str):
        try:
            if not query or not query.strip():
                return {"error": "Query cannot be empty"}

            result = RAGService.generate_answer(query)

            return result

        except Exception as e:
            print(f"[Search Error]: {e}")
            return {"error": "Search failed"}