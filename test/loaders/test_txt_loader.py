import os
import pytest
import src.configs.config
from pathlib import Path
from src.loaders.txt_loader import TxtLoader
from src.common.exceptions import ValidationError
from langchain_core.documents import Document
from src.configs.config import project_path, yaml_configs

# Get docs_dir from config or default to rag_docs
rag_config = yaml_configs.get("rag", {})
docs_dir = rag_config.get("docs_dir", "rag_docs")
TXT_PATH = os.path.join(project_path, docs_dir, "robots.txt")

class TestTxtLoader:
    
    @pytest.fixture
    def loader(self):
        """Create a TxtLoader instance."""
        return TxtLoader()
    
    def test_load_file_success(self, loader):
        """Test successful loading of a text file."""
        if not os.path.exists(TXT_PATH):
            # Create a temporary robots.txt if it doesn't exist for test purposes
            with open(TXT_PATH, 'w') as f:
                f.write("User-agent: *\nDisallow: /")
    
        documents = loader.load_file(TXT_PATH)
    
        # Verify return type
        assert isinstance(documents, list)
        assert len(documents) > 0
        document = documents[0]
        assert isinstance(document, Document)
        
        # Verify metadata
        assert document.metadata['source'] == TXT_PATH
        assert document.metadata['file_type'] == 'txt'
        assert document.metadata['file_size'] > 0
        assert document.metadata['encoding'] == 'utf-8'
        
        # Verify content
        assert len(document.page_content) > 0
        assert "User-agent" in document.page_content

    def test_load_file_invalid_path(self, loader):
        """Test loading a non-existent file."""
        with pytest.raises(ValidationError) as excinfo:
            loader.load_file("non_existent_file.txt")
        
        assert "Failed to load text file" in str(excinfo.value)

    def test_supported_extensions(self, loader):
        """Test supported extensions property."""
        assert ".txt" in loader.supported_extensions
        assert len(loader.supported_extensions) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
