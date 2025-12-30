from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.document_model import Document, DocumentChunkGemini
from typing import List, Dict, Any, Sequence
import uuid
from loguru import logger

class VectorDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, file_path: str, title: str | None = None, creator_user_id: int | None = None) -> Document:
        """
        Creates a new Document record.
        """
        try:
            document = Document(
                file_path=file_path,
                title=title,
                creator_user_id=creator_user_id
            )
            self.session.add(document)
            await self.session.flush()
            logger.info(f"Created document with ID: {document.id}")
            return document
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise e

    async def add_chunks(self, document_id: uuid.UUID, chunks_data: List[Dict[str, Any]]) -> List[DocumentChunkGemini]:
        """
        Adds multiple chunks to a document.
        chunks_data should be a list of dicts containing:
        - content: str
        - embedding: List[float]
        - chunk_index: int
        - page_number: int (optional)
        - metadata: dict (optional)
        """
        try:
            chunks = []
            for data in chunks_data:
                chunk = DocumentChunkGemini(
                    document_id=document_id,
                    content=data["content"],
                    embedding=data["embedding"],
                    chunk_index=data["chunk_index"],
                    page_number=data.get("page_number"),
                    meta_data=data.get("metadata", {})
                )
                chunks.append(chunk)
            
            self.session.add_all(chunks)
            await self.session.flush()
            logger.info(f"Added {len(chunks)} chunks to document {document_id}")
            return chunks
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            raise e
    
    async def get_document_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalars().first()

    async def search_similar_chunks(self, query_embedding: List[float], limit: int = 5) -> Sequence[tuple[DocumentChunkGemini, float]]:
        """
        Searches for document chunks similar to the query embedding using Cosine Distance.
        Returns a list of tuples (chunk, distance).
        
        SQL Equivalence:
        SELECT *, embedding <=> '[...]' as distance
        FROM document_chunks_gemini
        ORDER BY distance
        LIMIT 5;
        
        Note: 
        - The `<=>` operator represents Cosine Distance in pgvector.
        - Lower distance means higher similarity.
        - SQLAlchemy has no built-in support for vector operations (Cosine/Euclidean distance) as it only supports standard SQL.
        - Vector Search is a special feature provided by the `pgvector` extension for PostgreSQL using non-standard operators (like `<=>`).
        - We rely on the `pgvector-python` library to teach SQLAlchemy how to generate these special operators.
        """
        try:
            # Calculate distance using pgvector operator
            distance_col = DocumentChunkGemini.embedding.cosine_distance(query_embedding).label("distance")
            
            # Select both the chunk object and the distance value
            stmt = select(DocumentChunkGemini, distance_col).order_by(distance_col).limit(limit)
            
            result = await self.session.execute(stmt)
            # Result contains tuples of (DocumentChunkGemini, distance)
            # We use result.all() instead of result.scalars().all() because we are returning multiple columns
            return result.all()  # type: ignore
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            raise e

    async def commit(self):
        await self.session.commit()
