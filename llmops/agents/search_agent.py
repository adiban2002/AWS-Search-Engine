import os
import logging
import time
from dotenv import load_dotenv

from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from llmops.rag.retrieval_pipeline import RetrievalPipeline

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",   
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
            max_retries=1  
        )

        self.rag_pipeline = RetrievalPipeline()

        self.tools = [
            Tool(
                name="Cloud_Knowledge_Base",
                func=self.rag_pipeline.run,
                description="Use this to answer AWS, EKS, DevOps queries"
            )
        ]

        self.agent = self.llm.bind_tools(self.tools)

    def ask(self, query: str) -> str:
        try:
            logger.info(f"Agent Processing: {query}")

            
            response = self.agent.invoke(query)

            
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_call = response.tool_calls[0]
                result = self.rag_pipeline.run(tool_call["args"])

                
                final = self.llm.invoke(
                    f"""Answer using this context:
                    {result}

                    Question: {query}
                    """
                )
                return final.content

            return response.content

        except Exception as e:
            
            if "RESOURCE_EXHAUSTED" in str(e):
                logger.warning("Quota exceeded. Using fallback response.")

                context = self.rag_pipeline.run(query)
                return f"(Fallback RAG Answer)\n\n{context}"

            return f"Error: {str(e)}"


if __name__ == "__main__":
    agent = SearchAgent()
    print(agent.ask("How to setup EKS?"))