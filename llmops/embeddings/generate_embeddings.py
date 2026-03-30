

import os
import logging
from typing import List
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Missing Gemini API Key")

client = genai.Client(api_key=API_KEY)


class EmbeddingGenerator:
    MODEL = "gemini-embedding-001"

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def generate_embedding(text: str) -> List[float]:

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = client.models.embed_content(
                model=EmbeddingGenerator.MODEL,
                contents=text
            )

            if not response.embeddings:
                raise ValueError("No embeddings returned")

            embedding = response.embeddings[0].values

            if not embedding or not isinstance(embedding, list):
                raise ValueError("Invalid embedding received")

            return embedding

        except Exception as e:
            logger.error(f"[Embedding Error]: {e}", exc_info=True)
            raise