from pydantic import BaseModel
from langchain_core.documents import Document

class ContentExtractionService(BaseModel):
    """Service to extract string content from Document objects."""

    def extract_content(self, document: Document) -> str:
        """
        Extract the full text content from a Document object.
        
        This method retrieves the 'page_content' from the Document.
        
        Note on Pagination:
        Our custom loaders (e.g., PDFLoader) merge multiple pages into a single
        Document object's page_content, separated by markers (e.g., '--- Page Break ---').
        Therefore, this single string represents the entire document's content.

        Args:
            document: The Document object to process.

        Returns:
            str: The extracted text content.
        """
        if not document or not document.page_content:
            return ""
            
        return document.page_content
