import os
import pytest
import tempfile
from langchain_core.documents import Document
from src.services.data_load_service import data_load_service

class TestDocLoadService:
    
    def test_load_txt_file(self):
        """Test loading a text file through DocLoadService."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as tmp:
            tmp.write("Hello, World!")
            tmp_path = tmp.name
            
        try:
            service =data_load_service
            document = service.load(tmp_path)
            
            assert isinstance(document, Document)
            assert document.page_content == "Hello, World!"
            assert document.metadata['source'] == tmp_path
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_load_unsupported_file(self):
        """Test loading an unsupported file raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", mode="w", delete=False) as tmp:
            tmp.write("Unsupported content")
            tmp_path = tmp.name
            
        try:
            service = data_load_service
            with pytest.raises(ValueError, match="Unsupported file extension"):
                service.load(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
