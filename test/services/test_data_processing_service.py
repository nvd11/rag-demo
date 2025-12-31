import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.services.data_processing_service import DataProcessingService
from src.configs.db import get_async_engine
from src.models.document_model import Base
from src.dao.topic_dao import TopicDAO
from langchain_core.documents import Document

@pytest.fixture
async def db_session():
    get_async_engine.cache_clear()
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_process_file_with_topic(db_session):
    # 1. Mock Dependencies
    with patch("src.services.data_processing_service.DataLoadService") as MockLoader, \
         patch("src.services.data_processing_service.ChunkingService") as MockChunker, \
         patch("src.services.data_processing_service.EmbeddingService") as MockEmbedder:
        
        # Setup Mocks
        mock_loader = MockLoader.return_value
        mock_loader.load.return_value = [Document(page_content="Test content", metadata={"page_number": 1})]
        
        mock_chunker = MockChunker.return_value
        mock_chunker.chunk_document.return_value = ["Chunk 1", "Chunk 2"]
        
        mock_embedder = MockEmbedder.return_value
        mock_embedder.generate_embeddings.return_value = [[0.1]*768, [0.2]*768]
        
        # 2. Init Service
        service = DataProcessingService(db_session)
        # Verify mocks are injected (DataProcessingService creates new instances in init, so patch works on class)
        
        # 3. Process File
        file_path = "test_docs/manual.pdf"
        topic_name = "New Topic"
        creator_id = 999
        
        doc_id = await service.process_file(file_path, topic_name, creator_id)
        
        # 4. Verify Database State
        assert doc_id is not None
        
        topic_dao = TopicDAO(db_session)
        topic = await topic_dao.get_topic_by_name(topic_name)
        assert topic is not None
        assert topic.name == topic_name
        assert topic.creator_user_id == creator_id
        
        doc_ids = await topic_dao.get_document_ids_by_topic(topic_name)
        assert doc_id in doc_ids
        
        print("Data processing with topic creation passed!")
