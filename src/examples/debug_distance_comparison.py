import asyncio
import sys
import os
from sqlalchemy import text, inspect

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.embeddings.google_embedding import GoogleEmbedding
from src.configs.db import AsyncSessionFactory, get_async_engine

async def debug_distance_comparison():
    print("Initializing...")
    embedder = GoogleEmbedding("models/text-embedding-004").get_client()
    
    query = "昉·星光 2的USB Type C 开始同时用于供电和数据传输吗？"
    
    print(f"Query: {query}")

    print("\nGenerating embedding for query...")
    emb_query = embedder.embed_query(query)
    
    print("\n--- Running with NO cache clear ---")
    await calculate_and_show_distances(emb_query, clear_cache=False)
    
    print("\n--- Running WITH cache clear ---")
    await calculate_and_show_distances(emb_query, clear_cache=True)

async def calculate_and_show_distances(query_embedding, clear_cache: bool):
    if clear_cache:
        print("Cache cleared.")
        get_async_engine.cache_clear()
    else:
        print("Cache NOT cleared.")
    
    async with AsyncSessionFactory() as session:
        target_text_snippet = "请勿将此端口同时复用于充电和数据传输"
        
        chunk_sql = text("SELECT id, content FROM document_chunks_gemini WHERE content LIKE :snippet")
        result = await session.execute(chunk_sql, {"snippet": f"%{target_text_snippet}%"})
        chunk_row = result.first()

        if not chunk_row:
            print("Could not find target chunk in DB!")
            return
            
        chunk_16_id = chunk_row[0]
        
        dist_sql = text("SELECT embedding <=> :query_emb as distance FROM document_chunks_gemini WHERE id = :chunk_id")
        dist_res = await session.execute(dist_sql, {"query_emb": str(query_embedding), "chunk_id": chunk_16_id})
        dist_row = dist_res.first()
        if dist_row:
            print(f"Distance to Chunk 16 ('请勿...'): {dist_row[0]:.4f}")

if __name__ == "__main__":
    asyncio.run(debug_distance_comparison())
