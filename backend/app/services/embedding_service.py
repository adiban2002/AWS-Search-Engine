class EmbeddingService:

    @staticmethod
    def get_embedding(text: str):
        if not text:
            return None
        return [0.0] * 10