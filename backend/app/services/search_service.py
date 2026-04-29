import logging
from llmops.agents.search_agent import SearchAgent


logger = logging.getLogger(__name__)


try:
    agent = SearchAgent()
    logger.info("SearchAgent initialized successfully in SearchService.")
except Exception as e:
    logger.error(f"Failed to initialize SearchAgent: {e}")
    agent = None

class SearchService:
    @staticmethod
    def search(query: str):
        try:
            
            if not query or not query.strip():
                return {"status": "error", "message": "Query cannot be empty"}

            if agent is None:
                return {"status": "error", "message": "Search Agent not initialized"}

            
            logger.info(f"Service processing query: {query}")
            result = agent.ask(query)

            
            return {
                "status": "success",
                "query": query,
                "answer": result
            }

        except Exception as e:
            logger.error(f"Search failure in SearchService: {e}")
            return {
                "status": "error",
                "message": "Search failed internally",
                "details": str(e)
            }