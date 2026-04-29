import os
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential


from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    def __init__(self, vector_store=None, top_k=6, min_score=0.45, max_context_chars=3500):

        self.vector_store = vector_store or OpenSearchVectorStore()
        self.top_k = top_k
        self.min_score = min_score
        self.max_context_chars = max_context_chars
        
       
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.2,  
            max_output_tokens=1024
        )

        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an expert AI Cloud Engineer Assistant. 
Your task is to answer the user's question based ONLY on the provided context from the knowledge base.
If the answer is not contained within the context, strictly state: "I don't have enough information in my knowledge base."

Context:
{context}

Question: 
{question}

Answer:"""
        )

    def _get_relevant_docs(self, query: str) -> List[Document]:
        
        query_embedding = EmbeddingGenerator.generate_embedding(query)
        
       
        raw_results = self.vector_store.search(query_embedding, k=self.top_k)
        
        processed_docs = []
        seen_content = set()
        
        for res in raw_results:
            score = res.get("score", 0)
            text = res.get("text", "").strip()
            
            
            if score >= self.min_score and len(text) > 50:
                content_snippet = text[:100]
                if content_snippet not in seen_content:
                    seen_content.add(content_snippet)
                    processed_docs.append(Document(page_content=text, metadata={"score": score}))
        
        return processed_docs

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def run(self, query: str) -> Dict[str, Any]:

        try:
            
            docs = self._get_relevant_docs(query)

            if not docs:
                return {
                    "query": query,
                    "answer": "No relevant information found in the knowledge base.",
                    "documents": [],
                    "success": True
                }

            
            context_string = ""
            for d in docs:
                if len(context_string) + len(d.page_content) < self.max_context_chars:
                    context_string += d.page_content + "\n\n"

           
            formatted_prompt = self.prompt_template.format(context=context_string, question=query)
            response = self.llm.invoke(formatted_prompt)
            
            return {
                "query": query,
                "answer": response.content,
                "documents": [d.metadata for d in docs],
                "context_length": len(context_string),
                "success": True
            }

        except Exception as e:
            logger.error(f"[Critical RAG Pipeline Error]: {e}")
            return {
                "query": query,
                "answer": "Internal Server Error: The AI Agent is currently unavailable.",
                "error": str(e),
                "success": False
            }