from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.vector_dao import VectorDAO
from src.embeddings.google_embedding import GoogleEmbedding
from src.configs.config import yaml_configs
from loguru import logger

class RetrievalService:
    def __init__(self, session: AsyncSession):
        self.vector_dao = VectorDAO(session)
        # Initialize embedding model
        # Using the same model config as data ingestion: models/embedding-001
        self.embedding_client = GoogleEmbedding("models/embedding-001").get_client()
        
        # Load Similarity Threshold from config, default to 0.5
        self.similarity_threshold = 0.5
        if yaml_configs and "retrieval" in yaml_configs:
            self.similarity_threshold = yaml_configs["retrieval"].get("similarity_threshold", 0.5)
        logger.info(f"Retrieval Service initialized with similarity threshold: {self.similarity_threshold}")

    async def search_knowledge_base(self, query: str, limit: int = 5) -> str:
        """
        Embeds the query and searches the knowledge base (e.g. VisionFive 2 Datasheet).
        Returns a formatted string context.
        """
        try:
            if not self.embedding_client:
                 raise ValueError("Embedding client is not initialized.")
            
            logger.info(f"Generating embedding for query: {query}")
            # 1. Generate Embedding
            # embed_query returns List[float]
            query_embedding = self.embedding_client.embed_query(query)
            
            # 2. Search DB
            logger.info("Searching database...")
            # chunks_with_score is a list of (DocumentChunkGemini, distance)
            chunks_with_score = await self.vector_dao.search_similar_chunks(query_embedding, limit=limit)
            
            if not chunks_with_score:
                logger.warning("No chunks found in DB.")
                return "No relevant information found in the knowledge base."
            
            # 3. Filter by Threshold
            valid_chunks = []
            for chunk, distance in chunks_with_score:
                if distance <= self.similarity_threshold:
                    valid_chunks.append((chunk, distance))
                else:
                    logger.debug(f"Filtered out chunk (distance {distance:.4f} > {self.similarity_threshold})")

            if not valid_chunks:
                logger.warning("All chunks filtered out by threshold.")
                return "No relevant information found in the knowledge base."

            # 4. Format Output
            context_parts = []
            # enumerate(sequence, start=0) returns a tuple containing a count (from start) and the values obtained from iterating over sequence
            for i, (chunk, distance) in enumerate(valid_chunks):
                # Include page number if available
                page_info = f" (Page {chunk.page_number})" if chunk.page_number else ""
                context_parts.append(f"[Source {i+1}]{page_info} (Score: {distance:.4f}):\n{chunk.content}")
            
            formatted_context = "\n\n".join(context_parts)
            logger.info(f"Retrieved {len(valid_chunks)} chunks after filtering.")
            return formatted_context
            
        except Exception as e:
            logger.error(f"Error in retrieval service: {e}")
            return f"Error retrieving information: {str(e)}"
