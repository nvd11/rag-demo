from typing import Dict, Any
from pathlib import Path
from loguru import logger
from langchain_core.documents import Document

from src.loaders.base_loader import BaseLoader
from src.common.exceptions import ValidationError


class TxtLoader(BaseLoader[Document]):
    """Text file loader for reading plain text documents."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['.txt']
    
    def load_file(self, source: str, **kwargs) -> list[Document]:
        """
        Load and parse plain text file content.
        
        Args:
            source: Path to the text file
            **kwargs: Additional options for text processing
                - encoding: str = 'utf-8' - File encoding
                - errors: str = 'strict' - How to handle encoding errors
        
        Returns:
            list[Document]: Loaded documents
            
        Raises:
            ValidationError: If file reading fails
        """
        try:
            # Configure loader options
            encoding = kwargs.get('encoding', 'utf-8')
            errors = kwargs.get('errors', 'strict')
            
            logger.info(f"Loading text file: {source}")
            
            file_path = Path(source)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {source}")

            # Read content
            with open(file_path, 'r', encoding=encoding, errors=errors) as f:
                content = f.read()
            
            # Construct metadata
            metadata = {
                'source': str(file_path.absolute()),
                'file_type': 'txt',
                'file_size': file_path.stat().st_size,
                'encoding': encoding
            }
            
            return [Document(page_content=content, metadata=metadata)]
                
        except Exception as e:
            error_msg = f"Failed to load text file: {str(e)}"
            logger.error(error_msg)
            
            raise ValidationError(
                message=error_msg,
                error_code="TXT_LOAD_ERROR",
                source=source
            ) from e

    def load_content(self, source: str) -> str:
        """
        Legacy method for backward compatibility.
        
        Args:
            source: Path to the text file
            
        Returns:
            str: Extracted text content
        """
        documents = self.load_file(source)
        if not documents:
            return ""
        return documents[0].page_content
