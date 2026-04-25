import pytest
import os
from data.s3_loader import S3DocumentLoader

@pytest.fixture(scope="module")
def loader():
    return S3DocumentLoader()

def test_s3_connection(loader):
    files = loader.list_files(prefix="documents/")
    
    assert isinstance(files, list), "S3 list_files should return a list"
    assert len(files) > 0, f"No files found in S3 bucket {loader.bucket_name} under 'documents/'"
    print(f"\n Found {len(files)} files in S3")

def test_load_documents(loader):
    docs = loader.load_documents(prefix="documents/")

    assert len(docs) > 0, "No documents were loaded from S3"
    
    for doc in docs:
        assert "text" in doc
        assert "metadata" in doc
        assert "source" in doc["metadata"]
        assert doc["metadata"]["source"].startswith("documents/")
        
        
        assert isinstance(doc["text"], str)
        assert len(doc["text"].strip()) > 0

def test_file_content_relevance(loader):
    
    docs = loader.load_documents(prefix="documents/")
    texts = [doc["text"].lower() for doc in docs]

    
    keywords = ["aws", "cloud", "security", "azure", "devops", "networking", "gcp", "ai"]
    
    
    found = any(any(kw in text for kw in keywords) for text in texts)
    
    assert found, f"None of the target keywords found in S3 documents"

def test_aws_credentials_check():
    
    assert os.getenv("S3_BUCKET_NAME") is not None, "S3_BUCKET_NAME is missing"
    assert os.getenv("AWS_ACCESS_KEY_ID") is not None, "AWS_ACCESS_KEY_ID is missing"
    assert os.getenv("AWS_SECRET_ACCESS_KEY") is not None, "AWS_SECRET_ACCESS_KEY is missing"