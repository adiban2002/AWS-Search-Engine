import os
import logging
from typing import List, Dict, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class S3DocumentLoader:
    """
    Production-grade S3 Loader
    """

    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "ap-south-1")

        if not self.bucket_name:
            raise ValueError("Missing S3_BUCKET_NAME")

        self.client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        logger.info(f"S3 client initialized for bucket: {self.bucket_name}")


    def list_files(self, prefix: str = "") -> List[str]:
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            contents = response.get("Contents", [])

            files = [
                obj["Key"]
                for obj in contents
                if obj["Key"].endswith(".txt")
            ]

            logger.info(f"Found {len(files)} files in S3")

            return files

        except (BotoCoreError, ClientError) as e:
            logger.error(f"[S3 List Error]: {e}", exc_info=True)
            raise


    def read_file(self, key: str) -> str:
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )

            content = response["Body"].read().decode("utf-8")

            if not content.strip():
                logger.warning(f"Empty file: {key}")

            return content

        except (BotoCoreError, ClientError) as e:
            logger.error(f"[S3 Read Error]: {e}", exc_info=True)
            raise


    def load_documents(self, prefix: str = "") -> List[Dict[str, Any]]:
        try:
            files = self.list_files(prefix)

            if not files:
                logger.warning("No files found in S3")
                return []

            documents = []

            for key in files:
                try:
                    text = self.read_file(key)

                    if not text.strip():
                        continue

                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": key
                        }
                    })

                except Exception as e:
                    logger.error(f"[S3 Load Error - Skipping File]: {key} → {e}")

            logger.info(f"Loaded {len(documents)} documents")

            return documents

        except Exception as e:
            logger.error(f"[S3 Load Pipeline Error]: {e}", exc_info=True)
            raise