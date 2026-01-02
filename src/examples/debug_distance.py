import asyncio
import sys
import os
import numpy as np
from sqlalchemy import text, inspect

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.embeddings.google_embedding import GoogleEmbedding
from src.configs.db import AsyncSessionFactory, get_async_engine

def cosine_distance(v1, v2):
    """
    Calculate cosine distance between two vectors.
    Distance = 1 - Cosine Similarity
    """
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    similarity = dot_product / (norm_v1 * norm_v2)
    return 1 - similarity

async def debug_distance():
    print("Initializing embedding service...")
    embedder = GoogleEmbedding("models/text-embedding-004").get_client()
    
    # Original, full user query
    # query = "昉·星光 2的USB Type C 开始同时用于供电和数据传输吗？"
    
    # LLM rephrased query (from agent logs)
    query = "USB Type C供电和数据传输"

    # We found this chunk in previous steps (Chunk 16)
    target_text_snippet = "请勿将此端口同时复用于充电和数据传输"
    
    print(f"Query: {query}")
    print(f"Target Snippet: {target_text_snippet}")
    
    # 1. Generate Embeddings locally
    print("Generating embeddings...")
    emb_query = embedder.embed_query(query)
    
    # 2. Check Database Distance
    # We need to find the actual chunk in DB and compare it with our query embedding
    print("\nChecking Database...")
    get_async_engine.cache_clear()
    
    async with AsyncSessionFactory() as session:
        # Find Chunk 16 (by content snippet)
        chunk_sql = text("SELECT id, content, embedding FROM document_chunks_gemini WHERE content LIKE :snippet")
        result = await session.execute(chunk_sql, {"snippet": f"%{target_text_snippet}%"})
        chunk_row = result.first()
        
        if chunk_row:
            db_content = chunk_row[1]
            db_embedding = chunk_row[2] # pgvector returns list/array
            
            # Let database calculate it
            # We pass the query embedding to DB
            dist_sql = text("""
                SELECT embedding <=> :query_emb as distance
                FROM document_chunks_gemini 
                WHERE id = :chunk_id
            """)
            
            try:
                dist_res = await session.execute(dist_sql, {"query_emb": str(emb_query), "chunk_id": chunk_row[0]})
                dist_row = dist_res.first()
                if dist_row:
                    print(f"[PGVector Calculation] DB Distance: {dist_row[0]:.4f}")
            except Exception as e:
                print(f"PGVector calc failed (might be syntax): {e}")

            print("-" * 30)
            print("Full Chunk Content:")
            print(db_content)
            
        else:
            print("Target chunk not found in DB.")

if __name__ == "__main__":
    asyncio.run(debug_distance())
