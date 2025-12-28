import os
import pytest
import src.configs.config
from pathlib import Path
from src.loaders.pdf_loader import PDFLoader
from src.common.exceptions import ValidationError
from langchain_core.documents import Document
from src.configs.config import project_path, yaml_configs

# Get docs_dir from config or default to rag_docs
rag_config = yaml_configs.get("rag", {})
docs_dir = rag_config.get("docs_dir", "rag_docs")
PDF_PATH = os.path.join(project_path, docs_dir, "VisionFive2_DS.pdf")

class TestPDFLoader:
    
    @pytest.fixture
    def loader(self):
        """Create a PDFLoader instance."""
        return PDFLoader()
    
    def test_load_file_success(self, loader):
        """Test successful loading of the VisionFive2_DS.pdf file."""
        if not os.path.exists(PDF_PATH):
            pytest.skip(f"Test file not found: {PDF_PATH}")
            
        document = loader.load_file(PDF_PATH)
        
        # Verify return type
        assert isinstance(document, Document)
        
        # Verify metadata
        assert document.metadata['source'] == PDF_PATH
        assert document.metadata['file_type'] == 'pdf'
        assert document.metadata['file_size'] > 0
        assert 'total_pages' in document.metadata
        
        # Verify content
        assert len(document.page_content) > 0
        assert "VisionFive" in document.page_content or "StarFive" in document.page_content

    def test_load_file_specific_pages(self, loader):
        """Test loading specific pages from the PDF."""
        if not os.path.exists(PDF_PATH):
            pytest.skip(f"Test file not found: {PDF_PATH}")
            
        # Load only the first page
        document = loader.load_file(PDF_PATH, pages=[1])
        
        assert isinstance(document, Document)
        assert document.metadata['total_pages'] == 1
        assert document.metadata['pages_loaded'] == [1]
        
    def test_load_file_invalid_path(self, loader):
        """Test loading a non-existent file."""
        with pytest.raises(ValidationError) as excinfo:
            loader.load_file("non_existent_file.pdf")
        
        assert "Failed to load PDF" in str(excinfo.value)

    def test_supported_extensions(self, loader):
        """Test supported extensions property."""
        assert ".pdf" in loader.supported_extensions
        assert len(loader.supported_extensions) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
