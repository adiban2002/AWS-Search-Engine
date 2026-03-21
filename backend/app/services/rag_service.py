from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RAGService:

    @staticmethod
    def retrieve_context(query: str):
        """
        TEMP: Replace this later with OpenSearch retrieval
        """
        # Placeholder context (later: vector DB search)
        return [
            "Cloud computing allows scalable resources over the internet.",
            "AWS provides services like EC2, S3, and Lambda."
        ]

    @staticmethod
    def generate_answer(query: str, context: list):
        try:
            context_text = "\n".join(context)

            prompt = f"""
            You are an intelligent AI assistant.

            Context:
            {context_text}

            Question:
            {query}

            Answer clearly using the context.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"[RAG Error]: {e}")
            return "Error generating response"