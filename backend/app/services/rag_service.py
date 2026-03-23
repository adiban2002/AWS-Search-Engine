import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")  


class RAGService:

    @staticmethod
    def retrieve_context(query: str):
        return [
            "AWS (Amazon Web Services) is a cloud platform offering scalable services.",
            "It provides services like EC2 for compute, S3 for storage, and Lambda for serverless."
        ]

    @staticmethod
    def generate_answer(query: str, context: list):
        try:
            context_text = "\n".join(context)

            prompt = f"""
You are a helpful AI assistant.

Use the context below to answer the question.

Context:
{context_text}

Question:
{query}

Answer clearly and concisely.
"""

            response = model.generate_content(prompt)

            return response.text if response.text else "No response generated"

        except Exception as e:
            print(f"[RAG Error]: {e}")
            return "Error generating response"