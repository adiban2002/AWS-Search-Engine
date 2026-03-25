import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME: str = "AI Powered Cloud Search Engine"
    VERSION: str = "1.0.0"


    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")


    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "")
    OPENSEARCH_PORT: int = int(os.getenv("OPENSEARCH_PORT", 443))


settings = Settings()