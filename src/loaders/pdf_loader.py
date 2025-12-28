
from typing import Dict, Any
from pathlib import Path
from loguru import logger
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from src.loaders.base_loader import BaseLoader
from src.common.exceptions import ValidationError


class PDFLoader(BaseLoader[Document]):
    """PDF document loader using langchain's PyPDFLoader."""
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['.pdf']
    
    def load_file(self, source: str, **kwargs) -> Document:
        """
        Load and parse PDF file content.
        
        Args:
            source: Path to the PDF file
            **kwargs: Additional options for PDF processing
                - extract_images: bool = False - Whether to extract images
                - pages: list[int] = None - Specific pages to load
                - password: str = None - Password for encrypted PDFs
        
        Returns:
            Document: Loaded document with page content and metadata
            
        Raises:
            ValidationError: If PDF processing fails
        """
        try:
            # Configure loader options
            extract_images = kwargs.get('extract_images', False)
            pages = kwargs.get('pages', None)
            password = kwargs.get('password', None)
            
            logger.info(f"Loading PDF: {source}")
            
            # Initialize PyPDFLoader with options
            loader = PyPDFLoader(
                file_path=source,
                extract_images=extract_images,
                password=password
            )
            
            # Load pages
            if pages:
                # Load specific pages
                documents = []
                for page_num in pages:
                    try:
                        page_doc = loader.load()[page_num - 1] if page_num > 0 else None
                        if page_doc:
                            documents.append(page_doc)
                    except IndexError:
                        logger.warning(f"Page {page_num} not found in {source}")
                
                if not documents:
                    raise ValidationError(
                        message="No valid pages found",
                        error_code="INVALID_PAGES",
                        source=source
                    )
                
                # Combine pages into single document
                combined_content = "\n\n--- Page Break ---\n\n".join(
                    doc.page_content for doc in documents
                )
                
                metadata = {
                    'source': source,
                    'file_type': 'pdf',
                    'total_pages': len(documents),
                    'pages_loaded': pages,
                    'file_size': Path(source).stat().st_size
                }
                
                return Document(page_content=combined_content, metadata=metadata)
            else:
                # Load all pages
                documents = loader.load()
                
                if not documents:
                    raise ValidationError(
                        message="PDF is empty or could not be read",
                        error_code="EMPTY_PDF",
                        source=source
                    )
                
                # Combine all pages
                combined_content = "\n\n--- Page Break ---\n\n".join(
                    doc.page_content for doc in documents
                )
                
                # Extract metadata from first document
                metadata = documents[0].metadata.copy() if documents else {}
                metadata.update({
                    'source': source,
                    'file_type': 'pdf',
                    'total_pages': len(documents),
                    'file_size': Path(source).stat().st_size
                })
                
                return Document(page_content=combined_content, metadata=metadata)
                
        except Exception as e:
            error_msg = f"Failed to load PDF: {str(e)}"
            logger.error(error_msg)
            
            raise ValidationError(
                message=error_msg,
                error_code="PDF_LOAD_ERROR",
                source=source
            ) from e
    
    def _extract_metadata(self, source: str, documents: list[Document]) -> Dict[str, Any]:
        """Extract and combine metadata from loaded documents."""
        if not documents:
            return {}
        
        metadata = documents[0].metadata.copy() if documents[0].metadata else {}
        
        # Add file-specific metadata
        try:
            file_stat = Path(source).stat()
            metadata.update({
                'source': source,
                'file_type': 'pdf',
                'total_pages': len(documents),
                'file_size': file_stat.st_size,
                'modified_time': file_stat.st_mtime
            })
        except Exception as e:
            logger.warning(f"Could not extract file metadata: {e}")
        
        return metadata
    
    def load_content(self, source: str) -> str:
        """
        Legacy method for backward compatibility.
        
        Args:
            source: Path to the PDF file
            
        Returns:
            str: Extracted text content from all pages
        """
        document = self.load(source)
        return document.page_content