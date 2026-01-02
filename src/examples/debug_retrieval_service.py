import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.retrieval_service import RetrievalService
from src.configs.db import AsyncSessionFactory, get_async_engine

async def debug_retrieval():
    # Ensure fresh engine
    get_async_engine.cache_clear()
    
    async with AsyncSessionFactory() as session:
        service = RetrievalService(session)
        
        query = "昉·星光 2的USB Type C 开始同时用于供电和数据传输吗？"
        print(f"--- Query: {query} ---")
        
        # We need to manually set the topic as the Agent would
        result_text = await service.search_knowledge_base(query, topic="开发板")
        
        print("\n--- Retrieval Service Output ---\n")
        print(result_text)

if __name__ == "__main__":
    asyncio.run(debug_retrieval())
