
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pypdf

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
            
            # Load basic documents (text layer)
            documents = loader.load()
            
            if not documents:
                raise ValidationError(
                    message="PDF is empty or could not be read",
                    error_code="EMPTY_PDF",
                    source=source
                )

            # Filter pages if requested
            if pages:
                filtered_docs = []
                for page_num in pages:
                    idx = page_num - 1
                    if 0 <= idx < len(documents):
                        filtered_docs.append(documents[idx])
                    else:
                        logger.warning(f"Page {page_num} not found in {source}")
                documents = filtered_docs
                
                if not documents:
                    raise ValidationError(
                        message="No valid pages found",
                        error_code="INVALID_PAGES",
                        source=source
                    )

            # Perform custom OCR if image extraction is enabled
            if extract_images:
                self._enrich_with_ocr(documents, source, pages)

            # Combine pages into single document
            combined_content = "\n\n--- Page Break ---\n\n".join(
                doc.page_content for doc in documents
            )
            
            # Construct final metadata
            metadata = documents[0].metadata.copy() if documents else {}
            metadata.update({
                'source': source,
                'file_type': 'pdf',
                'total_pages': len(documents),
                'file_size': Path(source).stat().st_size
            })
            if pages:
                metadata['pages_loaded'] = pages
            
            return Document(page_content=combined_content, metadata=metadata)
                
        except Exception as e:
            error_msg = f"Failed to load PDF: {str(e)}"
            logger.error(error_msg)
            
            raise ValidationError(
                message=error_msg,
                error_code="PDF_LOAD_ERROR",
                source=source
            ) from e

    def _enrich_with_ocr(self, documents: List[Document], source: str, requested_pages: List[int] | None = None) -> None:
        """
        Extract images from PDF pages, run OCR, and append text to documents.
        This modifies the 'documents' list in-place.
        """
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr_engine = RapidOCR()
            logger.info("Initialized RapidOCR for image text extraction")
        except ImportError:
            logger.warning("rapidocr-onnxruntime not installed. Skipping OCR for images.")
            return

        try:
            reader = pypdf.PdfReader(source)
            
            # Map document index to actual PDF page index
            # If requested_pages is [1, 3], then documents[0] corresponds to page 0, documents[1] to page 2
            doc_page_indices = []
            if requested_pages:
                doc_page_indices = [p - 1 for p in requested_pages]
            else:
                doc_page_indices = list(range(len(documents)))

            for i, page_idx in enumerate(doc_page_indices):
                if page_idx >= len(reader.pages):
                    continue
                    
                page = reader.pages[page_idx]
                images = page.images
                
                if not images:
                    continue
                    
                ocr_texts = []
                for image in images:
                    try:
                        # image.data contains the bytes
                        result, _ = ocr_engine(image.data)
                        if result:
                            # result is a list of [box, text, score]
                            text = "\n".join([line[1] for line in result])
                            if text.strip():
                                ocr_texts.append(f"[Image Text]:\n{text}")
                    except Exception as img_err:
                        logger.warning(f"Failed to OCR image {image.name} on page {page_idx+1}: {img_err}")
                
                if ocr_texts:
                    # Append OCR content to the existing page content
                    documents[i].page_content += "\n\n" + "\n\n".join(ocr_texts)
                    logger.debug(f"Added OCR text from {len(ocr_texts)} images to page {page_idx+1}")

        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
    
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
