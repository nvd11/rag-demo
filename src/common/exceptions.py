"""
Common exception classes and validation utilities.

This module provides reusable exception classes and validation result types
that can be used across different components of the application.
"""

from typing import NamedTuple


class ValidationResult(NamedTuple):
    """
    Result of source validation with detailed error information.
    
    Attributes:
        is_valid: Whether the validation passed
        error_message: Detailed error message if validation failed
        error_code: Error code for programmatic handling
    """
    is_valid: bool
    error_message: str | None = None
    error_code: str | None = None


class ValidationError(Exception):
    """
    Custom exception class for validation errors with detailed information.
    
    This exception provides structured error information that can be used
    for both user-facing error messages and programmatic error handling.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code for handling different error types
        source: The source that caused the validation error (e.g., file path)
    """
    
    def __init__(self, message: str, error_code: str | None = None, source: str | None = None):
        self.message = message
        self.error_code = error_code
        self.source = source
        super().__init__(self.message)
    
    def __str__(self):
        """Return a formatted string representation of the error."""
        parts = [self.message]
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        if self.source:
            parts.append(f"Source: {self.source}")
        return " | ".join(parts)
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for serialization."""
        return {
            'message': self.message,
            'error_code': self.error_code,
            'source': self.source,
            'type': self.__class__.__name__
        }