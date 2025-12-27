
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic
import os
from pathlib import Path
from loguru import logger
from src.common.exceptions import ValidationError, ValidationResult

# Define a Type Variable 'T' for generic programming.
# Unlike Java where <T> is purely syntax, Python requires T to be defined as an object.
# This allows BaseLoader to be parameterized, e.g., BaseLoader[str] or BaseLoader[Document],
# ensuring type safety for the 'load' method return value in subclasses.
T = TypeVar('T')


class LoaderInterface(Protocol):
    """Protocol for all data loaders."""
    
    def load(self, source: str, **kwargs) -> T:
        """Load data from source and return parsed object."""
        ...
    
    def validate_source(self, source: str) -> ValidationResult:
        """Validate if source is supported by this loader."""
        ...


class BaseLoader(ABC, Generic[T]):
    """Abstract base class for all data loaders."""
    
    def load(self, source: str, **kwargs) -> T:
        """
        Load and parse data from source with validation.
        
        This method provides a default implementation that includes validation
        before delegating to the abstract load_file method.
        """
        # Step 1: Execute validation
        validation_result = self.validate_source(source)
        
        # Step 2: Check validation result
        if not validation_result.is_valid:
            # Step 3: Log error
            self._log_error(f"Validation failed: {validation_result.error_message}")
            
            # Step 4: Raise exception with detailed information
            raise ValidationError(
                message=validation_result.error_message or "Unknown validation error",
                error_code=validation_result.error_code,
                source=source
            )
        
        # Step 5: Validation passed, continue loading
        try:
            return self.load_file(source, **kwargs)
        except Exception as e:
            logger.error(f"Load failed after validation: {e}")
            raise

    @abstractmethod
    def load_file(self, source: str, **kwargs) -> T:
        """Load and parse data from source."""
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        pass
    
    def validate_source(self, source: str) -> ValidationResult:
        """
        Validate if source can be processed by this loader.
        
        Default implementation:
        1. Check if source path is empty
        2. Check if file exists
        3. Check if file extension is supported
        
        Args:
            source: Path to the source file
            
        Returns:
            ValidationResult: Contains validation status and detailed error info
        """
        # Check 1: Empty path
        if not source or not source.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Source path cannot be empty",
                error_code="EMPTY_SOURCE"
            )
        
        # Check 2: File existence
        if not os.path.exists(source):
            return ValidationResult(
                is_valid=False,
                error_message=f"File does not exist: {source}",
                error_code="FILE_NOT_FOUND"
            )
        
        # Check 3: File extension
        file_path = Path(source)
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_extensions:
            return ValidationResult(
                is_valid=False,
                error_message=f"Unsupported file extension: {extension}. Supported extensions: {self.supported_extensions}",
                error_code="UNSUPPORTED_EXTENSION"
            )
        
        return ValidationResult(is_valid=True)
    
    def get_file_info(self, source: str) -> dict:
        """Get metadata about the source file."""
        if os.path.exists(source):
            stat = os.stat(source)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        return {'exists': False}
    
    def _log_error(self, message: str, source: str | None = None) -> None:
        """Helper method for consistent error logging."""
        error_msg = f"{message}"
        if source:
            error_msg += f" (source: {source})"
        logger.error(f"[{self.__class__.__name__}] {error_msg}")