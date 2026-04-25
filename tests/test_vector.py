import pytest
import time
import logging
from llmops.embeddings.generate_embeddings import EmbeddingGenerator
from llmops.vector_db.vector_store import OpenSearchVectorStore


logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def vector_store():

    store = OpenSearchVectorStore()

    try:
        if store.client.indices.exists(index=store.index_name):
            logger.info(f"Cleaning up existing index: {store.index_name}")
            store.client.indices.delete(index=store.index_name)
            time.sleep(2)
    except Exception as e:
        logger.warning(f"Initial cleanup failed or index not found: {e}")

    return store


def test_embedding_generation():

    text = "DevOps and Cloud Computing are essential skills."
    
    try:
        embedding = EmbeddingGenerator.generate_embedding(text)

        assert isinstance(embedding, list), "Embedding must be a list"
        assert len(embedding) > 0, "Embedding list cannot be empty"
        assert all(isinstance(x, (float, int)) for x in embedding), "All values must be numeric"
        print(f"\n Embedding Generated! Dimension: {len(embedding)}")
    except Exception as e:
        pytest.fail(f"Embedding Generation Failed: {e}")


def test_index_and_search(vector_store):

    text = "AWS provides scalable cloud infrastructure."
    
    embedding = EmbeddingGenerator.generate_embedding(text)
    
   
    response = vector_store.index_document(
        text=text,
        embedding=embedding,
        metadata={"test_id": "123", "category": "cloud"}
    )

    assert response is not None
    assert "_id" in response
    assert response["result"] in ["created", "updated"]
    
   
    time.sleep(1.5)

    
    results = vector_store.search(embedding, k=2)

    assert isinstance(results, list)
    assert len(results) > 0, "No search results returned from OpenSearch"

    top_result = results[0]

    assert "text" in top_result
    assert "score" in top_result
    assert isinstance(top_result["text"], str)
    assert top_result["score"] is not None

   
    found_text = any("AWS" in (res.get("text") or "") for res in results)
    assert found_text, "The expected text 'AWS' was not found in search results"
    
    print(f"\n Vector Search Success! Top Score: {top_result['score']}")


def test_search_with_non_existent_query(vector_store):
    fake_embedding = [0.01] * 768 
    
    try:
        results = vector_store.search(fake_embedding, k=1)
        assert isinstance(results, list)
        print("\n Empty search handling passed.")
    except Exception as e:
        pytest.fail(f"Search failed on non-existent query: {e}")