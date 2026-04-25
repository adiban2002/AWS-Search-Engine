import os
import logging
import boto3
from typing import List, Dict, Any
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class S3DocumentLoader:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "ap-south-1")

        if not self.bucket_name:
            raise ValueError("Missing S3_BUCKET_NAME in .env")

        self.client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        logger.info(f"S3 client initialized for: {self.bucket_name}")

    def list_files(self, prefix: str = "documents/") -> List[str]:
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".txt")]
        except Exception as e:
            logger.error(f"S3 List Error: {e}")
            return []

    def read_file(self, key: str) -> str:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read().decode("utf-8")
        except Exception as e:
            logger.error(f"S3 Read Error for {key}: {e}")
            return ""

    def load_documents(self, prefix: str = "documents/") -> List[Dict[str, Any]]:
        files = self.list_files(prefix)
        documents = []
        for key in files:
            text = self.read_file(key)
            if text.strip():
                documents.append({"text": text, "metadata": {"source": key}})
        logger.info(f"Loaded {len(documents)} documents from S3")
        return documents