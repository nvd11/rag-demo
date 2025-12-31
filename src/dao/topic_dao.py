from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from src.models.document_model import Topic, Document, document_topic_association
from typing import List, Optional
import uuid
from loguru import logger

class TopicDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_topic(self, name: str, description: Optional[str] = None, creator_user_id: Optional[int] = None) -> Topic:
        """
        Creates a new Topic.
        """
        try:
            topic = Topic(
                name=name,
                description=description,
                creator_user_id=creator_user_id
            )
            self.session.add(topic)
            await self.session.flush()
            logger.info(f"Created topic '{name}' with ID: {topic.id}")
            return topic
        except Exception as e:
            logger.error(f"Error creating topic: {e}")
            raise e

    async def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """
        Retrieves a topic by its unique name.
        """
        result = await self.session.execute(select(Topic).where(Topic.name == name))
        return result.scalars().first()

    async def add_document_to_topic(self, topic_id: uuid.UUID, document_id: uuid.UUID, creator_user_id: Optional[int] = None) -> None:
        """
        Associates a document with a topic.
        """
        try:
            # Check if association already exists to avoid duplicates (though PK constraint handles this)
            stmt = insert(document_topic_association).values(
                topic_id=topic_id,
                document_id=document_id,
                creator_user_id=creator_user_id
            )
            await self.session.execute(stmt)
            await self.session.flush()
            logger.info(f"Associated document {document_id} with topic {topic_id}")
        except Exception as e:
            # Handle unique constraint violation gracefully if needed
            logger.error(f"Error associating document to topic: {e}")
            raise e

    async def get_document_ids_by_topic(self, topic_name: str) -> List[uuid.UUID]:
        """
        Retrieves all document IDs associated with a given topic name.
        """
        stmt = (
            select(Document.id)
            .join(document_topic_association, Document.id == document_topic_association.c.document_id)
            .join(Topic, Topic.id == document_topic_association.c.topic_id)
            .where(Topic.name == topic_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
