import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.configs.db import AsyncSessionFactory, get_async_engine

async def find_chunk():
    # Key phrase from user query
    search_text = "%电涌现象发生%" 
    
    # Ensure fresh engine
    get_async_engine.cache_clear()
    
    async with AsyncSessionFactory() as session:
        print(f"Searching for chunks containing: {search_text}")
        result = await session.execute(
            text("SELECT id, chunk_index, content FROM document_chunks_gemini WHERE content LIKE :query"),
            {"query": search_text}
        )
        rows = result.all()
        
        if rows:
            print(f"Found {len(rows)} matching chunks:")
            for row in rows:
                print("-" * 50)
                print(f"Chunk ID: {row[0]}")
                print(f"Index: {row[1]}")
                print(f"Content Preview:\n{row[2]}")
                print("-" * 50)
        else:
            print("No matching chunks found in database.")

if __name__ == "__main__":
    asyncio.run(find_chunk())
