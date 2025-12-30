import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.services.retrieval_service import RetrievalService
from src.configs.db import get_async_engine
from src.models.document_model import Base, DocumentChunkGemini
from src.dao.vector_dao import VectorDAO

@pytest.fixture
async def db_session():
    """
    Creates a new database session for testing.
    Rolls back the session after the test to ensure clean state.
    """
    # Force creation of a new engine for the current event loop
    get_async_engine.cache_clear()
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Create tables (if not exist)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        yield session
        await session.rollback() # Rollback changes after test

@pytest.mark.asyncio
async def test_search_knowledge_base_flow(db_session):
    """
    Test the full flow of searching the knowledge base.
    We will mock the GoogleEmbedding client to avoid making real API calls,
    but use the real VectorDAO and Database.
    """
    
    # 1. Setup Data in DB
    dao = VectorDAO(db_session)
    doc = await dao.create_document(file_path="service_test.pdf", title="Service Test")
    
    # Fake embedding for "test query"
    fake_query_embedding = [0.1] * 768
    
    chunks_data = [
        {
            "content": "VisionFive 2 has a StarFive JH7110 SoC.",
            "embedding": fake_query_embedding, # Perfect match for our fake query
            "chunk_index": 0,
            "page_number": 5
        },
        {
            "content": "Irrelevant info about weather.",
            "embedding": [0.9] * 768, # Dissimilar
            "chunk_index": 1,
            "page_number": 10
        }
    ]
    await dao.add_chunks(doc.id, chunks_data)
    
    # 2. Mock GoogleEmbedding
    # Why patch the class instead of `service.embedding_client`?
    # Because `self.embedding_client` is initialized inside `RetrievalService.__init__`:
    # 
    #     self.embedding_client = GoogleEmbedding("...").get_client()
    # 
    # If we don't patch the `GoogleEmbedding` class BEFORE instantiating `RetrievalService`,
    # the real constructor will execute, attempting to connect to Google's API. 
    # This would cause a crash if no API key is present or network is down (Side Effect).
    # Therefore, we must intercept the class creation to prevent the real initialization logic.
    with patch("src.services.retrieval_service.GoogleEmbedding") as MockGoogleEmbedding:
        # Setup the mock client
        mock_client = MagicMock()
        mock_client.embed_query.return_value = fake_query_embedding
        
        # Configure the Mock class to return our mock client
        mock_instance = MockGoogleEmbedding.return_value
        mock_instance.get_client.return_value = mock_client
        
        # 3. Initialize Service
        service = RetrievalService(db_session)
        
        # 4. Execute Search
        query = "What SoC does it use?"
        result = await service.search_knowledge_base(query, limit=1)
        
        # 5. Verify
        print(f"Result:\n{result}")
        
        # Verify call to embed_query
        mock_client.embed_query.assert_called_once_with(query)
        
        # Verify result content
        assert "VisionFive 2 has a StarFive JH7110 SoC" in result
        assert "[Source 1]" in result
        # Note: Score (0.0000) is included in result because mock embedding is identical
        assert "(Page 5)" in result
        assert "Irrelevant info" not in result

@pytest.mark.asyncio
async def test_search_knowledge_base_no_results(db_session):
    """Test handling when no results are found (filtered by threshold)."""
    
    with patch("src.services.retrieval_service.GoogleEmbedding") as MockGoogleEmbedding:
        mock_client = MagicMock()
        # Return a query embedding that is (hopefully) very different from existing DB content
        # An all-zeros vector or very small values often yields large cosine distance to normalized text vectors.
        # However, to be safe, we rely on the threshold logic. 
        # Assuming existing DB vectors are somewhat normal, a [0.1] vector might still be 'close' if normalized differently.
        # But since we use Cosine Distance, if vectors are normalized, dot product = cosine similarity.
        # Distance = 1 - Similarity (approx).
        # We'll use a mock vector.
        mock_client.embed_query.return_value = [0.1] * 768
        
        mock_instance = MockGoogleEmbedding.return_value
        mock_instance.get_client.return_value = mock_client
        
        service = RetrievalService(db_session)
        
        # Execute Search
        # Since we added a threshold of 0.5 in config (default),
        # and we assume the distance between [0.1]*768 and real data is > 0.5.
        # (Real text embeddings are complex; [0.1]*768 is a specific direction).
        # If this fails, it means [0.1]*768 is surprisingly close to VisionFive text.
        result = await service.search_knowledge_base("Any query")
        
        # Assert
        assert "No relevant information found" in result
