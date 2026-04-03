import pytest
from data.s3_loader import S3DocumentLoader


@pytest.fixture(scope="module")
def loader():
    return S3DocumentLoader()


def test_s3_connection(loader):
    files = loader.list_files(prefix="documents/")

    assert isinstance(files, list)
    assert len(files) > 0


def test_load_documents(loader):

    docs = loader.load_documents(prefix="documents/")

    assert isinstance(docs, list)
    assert len(docs) > 0

    for doc in docs:
        assert "text" in doc
        assert "metadata" in doc
        assert "source" in doc["metadata"]

        assert isinstance(doc["text"], str)
        assert len(doc["text"]) > 0


def test_file_content(loader):
    
    docs = loader.load_documents(prefix="documents/")

    texts = [doc["text"] for doc in docs]

    assert any("AWS" in text or "Cloud" in text for text in texts)