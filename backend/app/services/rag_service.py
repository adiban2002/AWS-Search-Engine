from llmops.rag.retrieval_pipeline import RetrievalPipeline


pipeline = RetrievalPipeline()


class RAGService:

    @staticmethod
    def generate_answer(query: str):
        return pipeline.run(query)