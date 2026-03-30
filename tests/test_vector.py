

import pytest
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore


@pytest.fixture(scope="module")
def vector_store():
    return OpenSearchVectorStore()


def test_embedding_generation():
    text = "DevOps and Cloud Computing are essential skills."

    embedding = EmbeddingGenerator.generate_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_index_and_search(vector_store):
    text = "AWS provides scalable cloud infrastructure."

    embedding = EmbeddingGenerator.generate_embedding(text)

    response = vector_store.index_document(
        text=text,
        embedding=embedding,
        metadata={"test": True}
    )

    assert response is not None

    results = vector_store.search(embedding, k=2)

    assert isinstance(results, list)
    assert len(results) > 0
    assert any("AWS" in (res.get("text") or "") for res in results)