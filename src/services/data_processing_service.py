from sqlalchemy.ext.asyncio import AsyncSession
from src.services.data_load_service import DataLoadService
from src.services.chunking_service import ChunkingService
from src.services.embedding_service import EmbeddingService
from src.dao.vector_dao import VectorDAO
from src.dao.topic_dao import TopicDAO
from loguru import logger
import os

class DataProcessingService:
    def __init__(self, session: AsyncSession):
        self.vector_dao = VectorDAO(session)
        self.topic_dao = TopicDAO(session)
        self.data_load_service = DataLoadService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

    async def process_file(self, file_path: str, topic_name: str, creator_user_id: int):
        """
        Loads, chunks, embeds, and saves a document.
        Associates the document with the specified topic.
        """
        logger.info(f"Starting processing for file: {file_path}, topic: {topic_name}")
        
        # 1. Load Document
        try:
            # DataLoadService.load is synchronous and returns List[Document]
            loaded_docs = self.data_load_service.load(file_path)
        except Exception as e:
             logger.error(f"Failed to load file {file_path}: {e}")
             raise
        
        if not loaded_docs:
            logger.warning(f"No content loaded from {file_path}")
            return

        # 2. Chunk Document
        chunk_texts = []
        chunk_metadatas = []
        
        for doc in loaded_docs:
            # ChunkingService.chunk_document takes a single Document and returns List[str]
            chunks = self.chunking_service.chunk_document(doc)
            for chunk_text in chunks:
                chunk_texts.append(chunk_text)
                # Preserve metadata from the original document
                chunk_metadatas.append(doc.metadata)

        logger.info(f"Generated {len(chunk_texts)} chunks from {len(loaded_docs)} documents.")

        if not chunk_texts:
            logger.warning("No chunks generated.")
            return

        # 3. Generate Embeddings
        embeddings = self.embedding_service.generate_embeddings(chunk_texts)
        
        if len(embeddings) != len(chunk_texts):
             logger.error("Mismatch between number of chunks and embeddings.")
             raise ValueError("Embedding generation failed to match chunk count.")

        # 4. Save to Database
        # 4.1 Ensure Topic exists
        topic = await self.topic_dao.get_topic_by_name(topic_name)
        if not topic:
            logger.info(f"Topic '{topic_name}' not found, creating new one.")
            topic = await self.topic_dao.create_topic(
                name=topic_name, 
                description=f"Auto-created topic for {topic_name}",
                creator_user_id=creator_user_id
            )
        
        # 4.2 Create Parent Document Record
        title = os.path.basename(file_path)
        db_document = await self.vector_dao.create_document(
            file_path=file_path,
            title=title,
            creator_user_id=creator_user_id
        )
        
        # 4.3 Associate Document with Topic
        await self.topic_dao.add_document_to_topic(
            topic_id=topic.id, 
            document_id=db_document.id,
            creator_user_id=creator_user_id
        )

        # 4.4 Save Chunks
        chunks_data = []
        for i, (text, embedding, metadata) in enumerate(zip(chunk_texts, embeddings, chunk_metadatas)):
            chunks_data.append({
                "content": text,
                "embedding": embedding,
                "chunk_index": i,
                "page_number": metadata.get("page_number"),
                "metadata": metadata
            })
        
        await self.vector_dao.add_chunks(db_document.id, chunks_data)
        await self.vector_dao.commit()
        
        logger.info(f"Successfully processed and saved document: {file_path}")
        return db_document.id
