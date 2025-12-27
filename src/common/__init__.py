"""
Common exceptions and utilities for the RAG demo application.

This package provides reusable exception classes and validation utilities
that can be used across different components of the application.
"""

from .exceptions import ValidationError, ValidationResult

__all__ = ['ValidationError', 'ValidationResult']