import pytest
from src.loaders.loader_factory import LoaderFactory
from src.loaders.pdf_loader import PDFLoader
from src.loaders.txt_loader import TxtLoader
from src.loaders.base_loader import BaseLoader


class TestLoaderFactory:
    
    def test_get_pdf_loader(self):
        """Test getting loader for PDF file."""
        loader = LoaderFactory.get_loader("document.pdf")
        assert isinstance(loader, PDFLoader)
        
    def test_get_txt_loader(self):
        """Test getting loader for TXT file."""
        loader = LoaderFactory.get_loader("notes.txt")
        assert isinstance(loader, TxtLoader)
        
    def test_get_loader_case_insensitive(self):
        """Test that file extension matching is case insensitive."""
        loader = LoaderFactory.get_loader("DOCUMENT.PDF")
        assert isinstance(loader, PDFLoader)
        
    def test_get_loader_no_extension(self):
        """Test that files with no extension default to TxtLoader."""
        loader = LoaderFactory.get_loader("README")
        assert isinstance(loader, TxtLoader)
        
    def test_unsupported_extension(self):
        """Test that unsupported extensions raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            LoaderFactory.get_loader("image.jpg")
            
    def test_register_loader(self):
        """Test registering a new loader type."""
        class MockLoader(BaseLoader):
            def supported_extensions(self):
                return [".mock"]
            def load_file(self, source, **kwargs):
                pass
            def load_content(self, source):
                return ""
        
        # Register the mock loader
        LoaderFactory.register_loader(".mock", MockLoader)
        
        # Verify we can get it
        loader = LoaderFactory.get_loader("test.mock")
        assert isinstance(loader, MockLoader)
