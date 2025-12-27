# Common Utilities

This package provides shared exception classes and utilities for the RAG demo application.

## Components

### Exceptions (`src.common.exceptions`)

#### `ValidationResult`
A `NamedTuple` that contains validation results with detailed error information:

```python
from src.common import ValidationResult

# Successful validation
result = ValidationResult(is_valid=True)

# Failed validation with details
result = ValidationResult(
    is_valid=False,
    error_message="File does not exist: /path/to/file.txt",
    error_code="FILE_NOT_FOUND"
)
```

#### `ValidationError`
A custom exception class for validation errors with structured information:

```python
from src.common import ValidationError

# Basic usage
raise ValidationError("Invalid file format")

# With error code and source
raise ValidationError(
    message="Unsupported file extension: .exe",
    error_code="UNSUPPORTED_EXTENSION",
    source="/path/to/file.exe"
)

# Convert to dictionary for API responses
error.to_dict()
# {
#     'message': 'Unsupported file extension: .exe',
#     'error_code': 'UNSUPPORTED_EXTENSION',
#     'source': '/path/to/file.exe',
#     'type': 'ValidationError'
# }
```

## Usage Examples

### In Data Loaders

```python
from src.common import ValidationResult, ValidationError

def validate_file(self, source: str) -> ValidationResult:
    if not source:
        return ValidationResult(
            is_valid=False,
            error_message="Source path cannot be empty",
            error_code="EMPTY_SOURCE"
        )
    
    if not os.path.exists(source):
        return ValidationResult(
            is_valid=False,
            error_message=f"File does not exist: {source}",
            error_code="FILE_NOT_FOUND"
        )
    
    return ValidationResult(is_valid=True)

def load_file(self, source: str):
    result = self.validate_file(source)
    if not result.is_valid:
        raise ValidationError(
            message=result.error_message,
            error_code=result.error_code,
            source=source
        )
    
    # Continue with loading...
```

### In API Services

```python
from src.common import ValidationError

try:
    data = loader.load(source)
except ValidationError as e:
    return {
        'success': False,
        'error': e.to_dict()
    }
```

## Error Codes

Standard error codes used across the application:

- `EMPTY_SOURCE`: Source path is empty or None
- `FILE_NOT_FOUND`: File does not exist at the given path
- `UNSUPPORTED_EXTENSION`: File extension is not supported
- `INVALID_FORMAT`: File format is invalid or corrupted
- `PERMISSION_DENIED`: Insufficient permissions to access the file

## Import Patterns

```python
# Import specific classes
from src.common import ValidationError, ValidationResult

# Or import the whole package
from src.common.exceptions import ValidationError, ValidationResult
```