from pydantic import BaseModel
from langchain_core.documents import Document
from src.loaders.loader_factory import LoaderFactory

class DataLoadService(BaseModel):
    """Service for loading documents using appropriate loaders."""

    def load(self, filepath: str) -> list[Document]:
        """
        Load a document from the given file path.
        
        Uses LoaderFactory to determine the appropriate loader based on file extension.
        
        Args:
            filepath: Path to the file to load
            
        Returns:
            list[Document]: The loaded document objects
        """
        # get loader from the factory based on the file extension
        loader = LoaderFactory.get_loader(filepath)

        return loader.load(filepath)


data_load_service = DataLoadService()
