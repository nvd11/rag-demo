import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.configs.db import get_async_engine
from src.agents.knowledge_base_agent import KnowledgeBaseAgent

@pytest.fixture
async def db_session():
    # Use existing data, do not rollback (or rollback doesn't matter for read-only)
    get_async_engine.cache_clear()
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_agent_chinese_query(db_session):
    # 1. Create Agent
    # We use a system prompt that forces the topic '开发板' because that's what we imported
    system_prompt = (
        "You are a helpful assistant. "
        "ALWAYS use the 'search_knowledge_base' tool with topic='开发板'. "
        "Answer in Chinese."
    )
    agent = KnowledgeBaseAgent(db_session, system_prompt=system_prompt)
    
    # 2. Query
    query = "昉·星光 2的USB Type C 开始同时用于供电和数据传输吗？"
    print(f"\n--- Query: {query} ---")
    
    result = await agent.ask(query)
    
    print(f"Answer: {result['answer']}")
    print(f"Sources Found: {len(result['sources'])}")
    for s in result['sources']:
        print(f" - {s}")

if __name__ == "__main__":
    import asyncio
    # Manual run for debugging
    async def main():
        engine = get_async_engine()
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        async with session_maker() as session:
            await test_agent_chinese_query(session)
    asyncio.run(main())
