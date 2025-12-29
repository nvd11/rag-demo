from typing import Optional, List, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from src.configs.db import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    creator_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # chunks = relationship("DocumentChunkGemini", back_populates="document", cascade="all, delete-orphan")

class DocumentChunkGemini(Base):
    __tablename__ = "document_chunks_gemini"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Remove ForeignKey to avoid hard constraint in DB
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True) 
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768)) # Gemini uses 768 dim
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # Using 'meta_data' in python to avoid conflict with Base.metadata, mapped to 'metadata' column
    meta_data: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default={}) 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # document = relationship("Document", back_populates="chunks")
