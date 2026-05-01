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
    def search(query_data: dict):
        try:
            if not isinstance(query_data, dict):
                return {"status": "error", "message": "Invalid data format. Expected JSON object."}
            
            query = query_data.get("query")
            
            if not query or not str(query).strip():
                return {"status": "error", "message": "Query cannot be empty"}

            global agent
            if agent is None:
                try:
                    agent = SearchAgent()
                except Exception as init_error:
                    logger.error(f"Retry initialization failed: {init_error}")
                    return {
                        "status": "error", 
                        "message": "Search Agent not initialized. Check API Keys and Environment Variables."
                    }

            logger.info(f"LLMOps Service processing query: {query}")
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