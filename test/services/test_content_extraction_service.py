import pytest
from langchain_core.documents import Document
from src.services.content_extraction_service import ContentExtractionService

class TestContentExtractionService:
    
    def test_extract_simple_content(self):
        """Test extracting content from a simple document."""
        doc = Document(page_content="Hello World", metadata={})
        service = ContentExtractionService()
        result = service.extract_content(doc)
        assert result == "Hello World"
        
    def test_extract_multipage_content(self):
        """Test extracting content from a document simulating multiple pages."""
        content = "Page 1 content\n\n--- Page Break ---\n\nPage 2 content"
        doc = Document(page_content=content, metadata={})
        service = ContentExtractionService()
        result = service.extract_content(doc)
        assert result == content
        assert "Page 1" in result
        assert "Page 2" in result
        
    def test_extract_empty_content(self):
        """Test extracting from a document with empty content."""
        doc = Document(page_content="", metadata={})
        service = ContentExtractionService()
        result = service.extract_content(doc)
        assert result == ""