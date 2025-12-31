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
async def test_search_similar_chunks(db_session):
    dao = VectorDAO(db_session)
    
    # 1. Create Doc
    doc = await dao.create_document(file_path="search_test.pdf", title="Search Test")
    
    # 2. Add Chunks with distinct embeddings
    # Target Query: [1.0, 0.0, ..., 0.0]
    
    # Chunk 1: Very similar to query ([0.9, 0.1, ...])
    emb1 = [0.0] * 768
    emb1[0] = 0.9
    emb1[1] = 0.1
    
    # Chunk 2: Dissimilar ([0.1, 0.9, ...])
    emb2 = [0.0] * 768
    emb2[0] = 0.1
    emb2[1] = 0.9
    
    chunks_data = [
        {"content": "Target Content", "embedding": emb1, "chunk_index": 0},
        {"content": "Noise Content", "embedding": emb2, "chunk_index": 1}
    ]
    await dao.add_chunks(doc.id, chunks_data)
    
    # 3. Search
    query_emb = [0.0] * 768
    query_emb[0] = 1.0 # Should match Chunk 1 best
    
    # 3.1 Test Limit 1 (Best Match)
    results = await dao.search_similar_chunks(query_emb, limit=1)
    
    assert len(results) == 1
    # Result is now a tuple: (chunk, distance)
    chunk, distance = results[0]
    
    # Note: Cosine Distance: Lower is better.
    # [1.0, 0...] vs [0.9, 0.1...] is closer than [1.0, 0...] vs [0.1, 0.9...]
    assert chunk.content == "Target Content"
    assert isinstance(distance, float)
    
    # 3.2 Test Limit 2 (All matches)
    results_all = await dao.search_similar_chunks(query_emb, limit=2)
    assert len(results_all) == 2
    
    chunk0, dist0 = results_all[0]
    chunk1, dist1 = results_all[1]
    
    assert chunk0.content == "Target Content" # Order matters
    assert chunk1.content == "Noise Content"
    assert dist0 < dist1 # Target should be closer

    print("Search test passed!")

@pytest.mark.asyncio
async def test_search_with_document_filter(db_session):
    dao = VectorDAO(db_session)
    
    # 1. Create 2 Documents
    doc1 = await dao.create_document(file_path="doc1.pdf", title="Doc 1")
    doc2 = await dao.create_document(file_path="doc2.pdf", title="Doc 2")
    
    # 2. Add identical chunks to both documents
    # Both chunks are perfect matches for the query [1.0, 0...]
    emb = [0.0] * 768
    emb[0] = 1.0 
    
    await dao.add_chunks(doc1.id, [{"content": "Content from Doc 1", "embedding": emb, "chunk_index": 0}])
    await dao.add_chunks(doc2.id, [{"content": "Content from Doc 2", "embedding": emb, "chunk_index": 0}])
    
    # 3. Search with Filter (Only Doc 2)
    query_emb = [0.0] * 768
    query_emb[0] = 1.0
    
    results = await dao.search_similar_chunks(query_emb, limit=5, document_ids=[doc2.id])
    
    # 4. Verify
    assert len(results) == 1
    chunk, _ = results[0]
    assert chunk.content == "Content from Doc 2"
    assert chunk.document_id == doc2.id
    
    print("Filter test passed!")
