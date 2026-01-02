import asyncio
import sys
import os
import numpy as np
from sqlalchemy import text, inspect

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.embeddings.google_embedding import GoogleEmbedding
from src.configs.db import AsyncSessionFactory, get_async_engine
from src.services.retrieval_service import RetrievalService
from src.dao.vector_dao import VectorDAO

async def debug_dao():
    print("Initializing...")
    get_async_engine.cache_clear()
    
    async with AsyncSessionFactory() as session:
        service = RetrievalService(session)
        dao = VectorDAO(session)
        
        query = "昉·星光 2的USB Type C 开始同时用于供电和数据传输吗？"
        print(f"Query: {query}")

        # 1. Get embedding from RetrievalService
        query_embedding = service.embedding_client.embed_query(query)
        print("Generated embedding for query.")
        
        # 2. Get distance to Chunk 16
        target_text_snippet = "请勿将此端口同时复用于充电和数据传输"
        
        chunk_sql = text("SELECT id, content, embedding FROM document_chunks_gemini WHERE content LIKE :snippet")
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
            print(f"\nDistance to Chunk 16 ('请勿...'): {dist_row[0]:.4f}")

        # 3. Get Top 5 chunks
        print("\n--- Top 5 Chunks ---")
        top_chunks = await dao.search_similar_chunks(query_embedding, limit=5)
        
        for i, (chunk, distance) in enumerate(top_chunks):
            print(f"\n{i+1}. Distance: {distance:.4f}")
            print(f"   Content: {chunk.content[:150].replace(chr(10), ' ')}...")
            if chunk.id == chunk_16_id:
                print("   *** THIS IS CHUNK 16 ***")

if __name__ == "__main__":
    asyncio.run(debug_dao())
