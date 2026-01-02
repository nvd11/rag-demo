from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.vector_dao import VectorDAO
from src.dao.topic_dao import TopicDAO
from src.embeddings.embedding_factory import EmbeddingFactory
from src.configs.config import yaml_configs
from loguru import logger
from typing import Optional

class RetrievalService:
    def __init__(self, session: AsyncSession, provider: Optional[str] = None, model: Optional[str] = None):
        self.vector_dao = VectorDAO(session)
        self.topic_dao = TopicDAO(session)
        
        embedding_config = yaml_configs.get("embedding", {})
        
        # Priority: Constructor Args -> Config File -> Defaults
        self.provider = provider or embedding_config.get("provider", "google")
        self.model = model or embedding_config.get("model", "models/text-embedding-004")
        
        embedding_provider = EmbeddingFactory.get_embedding_provider(self.provider, self.model)
        self.embedding_client = embedding_provider.get_client()
        logger.info(f"Retrieval Service initialized with embedding model: {self.provider}/{self.model}")
        
        # Load Similarity Threshold from config, default to 0.5
        self.similarity_threshold = 0.5
        if yaml_configs and "retrieval" in yaml_configs:
            self.similarity_threshold = yaml_configs["retrieval"].get("similarity_threshold", 0.5)
        logger.info(f"Retrieval Service initialized with similarity threshold: {self.similarity_threshold}")

    async def search_knowledge_base(self, query: str, limit: int = 5, topic: Optional[str] = None) -> str:
        """
        Embeds the query and searches the knowledge base.
        Can be optionally filtered by topic.
        Returns a formatted string context.
        """
        try:
            if not self.embedding_client:
                 raise ValueError("Embedding client is not initialized.")
            
            logger.info(f"Generating embedding for query: {query}")
            # 1. Generate Embedding
            # embed_query returns List[float]
            query_embedding = self.embedding_client.embed_query(query)
            
            # 2. Prepare Filter (Document IDs by Topic)
            document_ids = None
            if topic:
                logger.info(f"Filtering search by topic: {topic}")
                document_ids = await self.topic_dao.get_document_ids_by_topic(topic)
                if not document_ids:
                    logger.warning(f"No documents found for topic '{topic}'.")
                    return f"No documents found for topic '{topic}'."
            else:
                logger.info("No topic provided. Performing global search across all documents.")

            # 3. Search DB
            logger.info("Searching database...")
            # chunks_with_score is a list of (DocumentChunkGemini, distance)
            chunks_with_score = await self.vector_dao.search_similar_chunks(
                query_embedding, 
                limit=limit,
                document_ids=document_ids
            )
            
            if not chunks_with_score:
                logger.warning("No chunks found in DB.")
                return "No relevant information found in the knowledge base."
            
            # 3. Process Chunks (Pass all chunks to Agent, but mark relevance)
            processed_chunks = []
            valid_count = 0
            for chunk, distance in chunks_with_score:
                # We determine validity based on threshold, but we don't filter them out entirely.
                # This allows the Agent to see "near misses" or decide for itself, 
                # while still providing a hint about relevance.
                is_valid = distance <= self.similarity_threshold
                
                # Tag chunks that are far away
                status_tag = "" if is_valid else f" [LOW RELEVANCE > {self.similarity_threshold}]"
                
                processed_chunks.append((chunk, distance, status_tag))
                if is_valid:
                    valid_count += 1
                else:
                    logger.debug(f"Marked chunk as LOW RELEVANCE (distance {distance:.4f} > {self.similarity_threshold})")

            # 4. Format Output
            context_parts = []
            for i, (chunk, distance, status_tag) in enumerate(processed_chunks):
                # Include page number if available
                page_info = f"Page: {chunk.page_number}" if chunk.page_number else ""
                
                # Include other metadata
                meta_dict = chunk.meta_data or {}
                # Exclude page_number from general metadata display if it's already shown
                meta_str = ", ".join([f"{k}={v}" for k, v in meta_dict.items() if k != 'page_number'])
                
                meta_display = []
                if page_info: meta_display.append(page_info)
                if meta_str: meta_display.append(meta_str)
                
                meta_full_str = f" ({', '.join(meta_display)})" if meta_display else ""
                
                # Construct Header: [Source 1] (Page: 5, source=...) (Score: 0.1234) [LOW RELEVANCE > 0.5]
                header = f"[Source {i+1}]{meta_full_str} (Score: {distance:.4f}){status_tag}"
                context_parts.append(f"{header}:\n{chunk.content}")
            
            formatted_context = "\n\n".join(context_parts)
            logger.info(f"Retrieved {len(processed_chunks)} chunks (Valid by threshold: {valid_count}).")
            return formatted_context
            
        except Exception as e:
            logger.error(f"Error in retrieval service: {e}")
            return f"Error retrieving information: {str(e)}"
