from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from src.configs.db import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path = Column(String(1024), nullable=False)
    title = Column(String(255))
    creator_user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # chunks = relationship("DocumentChunkGemini", back_populates="document", cascade="all, delete-orphan")

class DocumentChunkGemini(Base):
    __tablename__ = "document_chunks_gemini"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Remove ForeignKey to avoid hard constraint in DB
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True) 
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768)) # Gemini uses 768 dim
    page_number = Column(Integer)
    chunk_index = Column(Integer, nullable=False)
    # Using 'meta_data' in python to avoid conflict with Base.metadata, mapped to 'metadata' column
    meta_data = Column("metadata", JSONB, default={}) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # document = relationship("Document", back_populates="chunks")
