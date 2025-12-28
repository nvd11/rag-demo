from pathlib import Path
from typing import Type

from src.loaders.base_loader import BaseLoader
from src.loaders.pdf_loader import PDFLoader
from src.loaders.txt_loader import TxtLoader


class LoaderFactory:
    """Factory class for creating loader instances based on file extensions."""

    _LOADER_MAP: dict[str, Type[BaseLoader]] = {
        '.pdf': PDFLoader,
        '.txt': TxtLoader,
        '': TxtLoader  # Default to TxtLoader for files with no extension
    }

    @classmethod
    def get_loader(cls, file_path: str) -> BaseLoader:
        """
        Get appropriate loader for the given file path based on extension.
        
        If the file has no extension, it defaults to TxtLoader.

        Args:
            file_path: Path to the file to load

        Returns:
            An instance of the appropriate loader class

        Raises:
            ValueError: If the file extension is not supported
        """
        extension = Path(file_path).suffix.lower()
        
        loader_class = cls._LOADER_MAP.get(extension)
        
        if not loader_class:
            # Filter out empty string from supported list for clearer error message
            supported_exts = [ext for ext in cls._LOADER_MAP.keys() if ext]
            supported_str = ", ".join(sorted(supported_exts))
            raise ValueError(
                f"Unsupported file extension: '{extension}'. "
                f"Supported extensions are: {supported_str}"
            )
            
        return loader_class()

    @classmethod
    def register_loader(cls, extension: str, loader_class: Type[BaseLoader]) -> None:
        """
        Register a new loader for an extension.
        
        Args:
            extension: File extension (e.g., '.md')
            loader_class: The loader class to register
        """
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        cls._LOADER_MAP[extension.lower()] = loader_class
