import os
import logging
from typing import List, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class S3DocumentLoader:

    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "ap-south-1")

        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME is required in environment variables")

        try:
            self.client = boto3.client("s3", region_name=self.region)
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"[S3 Init Error]: {e}", exc_info=True)
            raise

    def list_files(self, prefix: str = "") -> List[str]:
        try:
            paginator = self.client.get_paginator("list_objects_v2")

            file_keys = []

            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    key = obj["Key"]

                    # Ignore folders
                    if not key.endswith("/") and key.endswith(".txt"):
                        file_keys.append(key)

            logger.info(f"Found {len(file_keys)} files in S3")

            return file_keys

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

    def load_documents(self, prefix: str = "") -> List[Dict]:
        try:
            file_keys = self.list_files(prefix)

            if not file_keys:
                logger.warning("No files found in S3")

            documents = []

            for key in file_keys:
                text = self.read_file(key)

                documents.append({
                    "text": text,
                    "metadata": {
                        "source": key
                    }
                })

            logger.info(f"Loaded {len(documents)} documents from S3")

            return documents

        except Exception as e:
            logger.error(f"[S3 Load Error]: {e}", exc_info=True)
            raise