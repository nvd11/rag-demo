import pytest
from langchain_core.documents import Document
from src.services.chunking_service import ChunkingService

class TestChunkingService:
    
    def test_chunk_document_basic(self):
        """Test basic chunking functionality."""
        # Create a document with length > 50 chars
        content = "a" * 120
        doc = Document(page_content=content, metadata={})
        
        # Set chunk_size to 50
        service = ChunkingService(chunk_size=50, chunk_overlap=0)
        chunks = service.chunk_document(doc)
        
        assert len(chunks) > 1
        assert len(chunks[0]) <= 50
        
    def test_chunk_document_with_overlap(self):
        """Test chunking with overlap."""
        content = "1234567890" * 2  # "12345678901234567890" (20 chars)
        doc = Document(page_content=content, metadata={})
        
        # Chunk size 10, overlap 5
        # Expected: "1234567890", "6789012345", ...
        service = ChunkingService(chunk_size=10, chunk_overlap=5)
        chunks = service.chunk_document(doc)
        
        assert len(chunks) >= 2
        # Check overlap: end of first chunk should match start of second chunk
        assert chunks[0][-5:] == chunks[1][:5]
        
    def test_chunk_empty_document(self):
        """Test chunking an empty document."""
        doc = Document(page_content="", metadata={})
        service = ChunkingService()
        chunks = service.chunk_document(doc)
        assert chunks == []
        
    def test_chunk_none_document(self):
        """Test chunking None."""
        # Type hinting says Document, but runtime could be None
        service = ChunkingService()
        chunks = service.chunk_document(None) # type: ignore
        assert chunks == []
