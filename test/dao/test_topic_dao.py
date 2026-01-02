import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.dao.topic_dao import TopicDAO
from src.dao.vector_dao import VectorDAO
from src.configs.db import get_async_engine
from src.models.document_model import Base

@pytest.fixture
async def db_session():
    # Clear cache to ensure a fresh engine for testing environment if needed
    get_async_engine.cache_clear()
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_topic_lifecycle(db_session):
    topic_dao = TopicDAO(db_session)
    vector_dao = VectorDAO(db_session)
    
    # 1. Create Topic
    topic_name = "Test Topic"
    topic = await topic_dao.create_topic(name=topic_name, description="A test topic", creator_user_id=123)
    
    assert topic.id is not None
    assert topic.name == topic_name
    assert topic.creator_user_id == 123
    
    # 2. Get Topic by Name
    fetched_topic = await topic_dao.get_topic_by_name(topic_name)
    assert fetched_topic is not None
    assert fetched_topic.id == topic.id
    
    # 3. Create Documents and Associate
    doc1 = await vector_dao.create_document(file_path="doc1.pdf", title="Doc 1")
    doc2 = await vector_dao.create_document(file_path="doc2.pdf", title="Doc 2")
    
    await topic_dao.add_document_to_topic(topic.id, doc1.id)
    await topic_dao.add_document_to_topic(topic.id, doc2.id)
    
    # 4. Get Document IDs by Topic
    doc_ids = await topic_dao.get_document_ids_by_topic(topic_name)
    
    assert len(doc_ids) == 2
    assert doc1.id in doc_ids
    assert doc2.id in doc_ids
    
    print("Topic lifecycle test passed!")
