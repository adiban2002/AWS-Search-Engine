import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "AI-Powered-Search-Engine"
    VERSION = "1.0.0"
    
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    
    OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
    OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "admin")
    OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")
    
    
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    @classmethod
    def validate_config(cls):
        
        required = ["GEMINI_API_KEY", "OPENSEARCH_HOST", "OPENSEARCH_PASSWORD"]
        for var in required:
            if not getattr(cls, var):
                raise ValueError(f"Missing required environment variable: {var}")
        print("Configuration validated successfully!")