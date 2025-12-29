import pytest
from unittest.mock import MagicMock, patch
from src.services.embedding_service import EmbeddingService

@pytest.fixture
def mock_google_embeddings():
    # We now need to patch where it is USED or IMPORTED in the new structure
    # The EmbeddingService calls EmbeddingFactory, which creates GoogleEmbedding.
    # GoogleEmbedding imports GoogleGenerativeAIEmbeddings from langchain_google_genai
    
    with patch("src.embeddings.google_embedding.GoogleGenerativeAIEmbeddings") as mock:
        yield mock

@patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"})
def test_init_success(mock_google_embeddings):
    service = EmbeddingService()
    assert service.provider == "google"
    assert service.model == "models/text-embedding-004"
    # Factory calls GoogleEmbedding, which calls get_client, which instantiates GoogleGenerativeAIEmbeddings
    mock_google_embeddings.assert_called_once()

@patch.dict("os.environ", {}, clear=True)
def test_init_no_api_key():
    # Ensure GOOGLE_API_KEY is not set
    with pytest.raises(ValueError, match="GOOGLE_API_KEY is required"):
        EmbeddingService()

@patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"})
def test_generate_embeddings_success(mock_google_embeddings):
    # Setup mock return value
    mock_instance = mock_google_embeddings.return_value
    expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_instance.embed_documents.return_value = expected_embeddings

    service = EmbeddingService()
    chunks = ["hello", "world"]
    result = service.generate_embeddings(chunks)

    assert result == expected_embeddings
    mock_instance.embed_documents.assert_called_once_with(chunks)

@patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"})
def test_generate_embeddings_empty(mock_google_embeddings):
    service = EmbeddingService()
    result = service.generate_embeddings([])
    assert result == []
    mock_google_embeddings.return_value.embed_documents.assert_not_called()

@patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"})
def test_generate_embeddings_error(mock_google_embeddings):
    mock_instance = mock_google_embeddings.return_value
    mock_instance.embed_documents.side_effect = Exception("API Error")

    service = EmbeddingService()
    with pytest.raises(Exception, match="API Error"):
        service.generate_embeddings(["test"])
