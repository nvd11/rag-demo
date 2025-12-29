from typing import List
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService(BaseModel):
    """Service for splitting documents into smaller text chunks."""
    
    chunk_size: int = Field(default=1000, description="Maximum size of chunks")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    
    def chunk_document(self, document: Document) -> List[str]:
        """
        Split the document content into a list of string chunks.
        
        Args:
            document: The document to split.
            
        Returns:
            List[str]: A list of text chunks.
        """
        if not document or not document.page_content:
            return []
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        return text_splitter.split_text(document.page_content)
