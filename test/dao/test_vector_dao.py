import pytest
import uuid
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from src.dao.vector_dao import VectorDAO
from src.configs.db import get_async_engine
from src.models.document_model import Base

@pytest.fixture
async def db_session():
    """
    Creates a new database session for testing.
    Rolls back the session after the test to ensure clean state.
    """
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Create tables (if not exist)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        yield session
        await session.rollback() # Rollback changes after test

@pytest.mark.asyncio
async def test_create_document_and_chunks(db_session):
    dao = VectorDAO(db_session)
    
    # 1. Test create document
    file_path = "test_docs/manual.pdf"
    title = "Test Manual"
    user_id = 999
    
    doc = await dao.create_document(file_path=file_path, title=title, creator_user_id=user_id)
    
    assert doc.id is not None
    assert doc.file_path == file_path
    assert doc.title == title
    assert doc.creator_user_id == user_id
    
    print(f"Created doc: {doc.id}")

    # 2. Test add chunks
    chunks_data = [
        {
            "content": "This is chunk 1 content.",
            "embedding": [0.1] * 768, # Mock embedding
            "chunk_index": 0,
            "page_number": 1,
            "metadata": {"source": "intro"}
        },
        {
            "content": "This is chunk 2 content.",
            "embedding": [0.2] * 768, 
            "chunk_index": 1,
            "page_number": 1
        }
    ]
    
    chunks = await dao.add_chunks(doc.id, chunks_data)
    
    assert len(chunks) == 2
    assert chunks[0].document_id == doc.id 
    assert chunks[0].content == "This is chunk 1 content."
    assert chunks[0].chunk_index == 0 
    
    print(f"Added {len(chunks)} chunks.")
    
    # 3. Verify retrieval
    retrieved_doc = await dao.get_document_by_id(doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.file_path == file_path
