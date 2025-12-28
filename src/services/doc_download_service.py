
import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
from typing import Optional

from pydantic import BaseModel, computed_field
from src.configs.config import project_path, yaml_configs


class DocDownloadService(BaseModel):
    """Pydantic-based service for managing document data operations."""
    
    @computed_field  # Pydantic decorator that creates a computed field
    @property      # Python property decorator to make this method accessible as an attribute
    def targetpath(self) -> str:
        """
        Computed target path based on imported project_path.
        
        This field is dynamically calculated each time it's accessed:
        - Uses imported project_path from config (not a class member)
        - Uses os.path.join() to safely combine paths
        - Always reflects the latest project_path from config
        - Automatically creates directory on first access
        - Included in serialization (dict(), json()) 
        - No manual initialization required
        
        Performance Note: os.path.join() is lightweight, so recomputation 
        costs are minimal for this use case.
        """
        rag_config = yaml_configs.get("rag", {})
        docs_dir = rag_config.get("docs_dir", "rag_docs")
        target_path = os.path.join(project_path, docs_dir)
        # Don't automatically create directory here - let download method handle it
        # self._ensure_directory_exists(target_path)
        return target_path
    
    def _ensure_directory_exists(self, directory_path: str, mode: int = 0o755, exist_ok: bool = True) -> None:
        """
        Create directory if it doesn't exist.
        
        Args:
            directory_path: Path to the directory to create
            mode: Permission mode for the directory (default: 0o755)
            exist_ok: If True, don't raise error if directory already exists (default: True)
        
        Raises:
            OSError: If directory creation fails and exist_ok is False
        """
        Path(directory_path).mkdir(parents=True, mode=mode, exist_ok=exist_ok)
    


    def download(self, doc_url: str, filename: Optional[str] = None, overwrite: bool = False, target_dir: Optional[str] = None) -> str:
        """
        Download document from URL and save to target directory.
        
        Args:
            doc_url: URL of the document to download
            filename: Custom filename for the downloaded file (auto-generated if not provided)
            overwrite: Whether to overwrite existing file (default: False)
            target_dir: Custom target directory (uses self.targetpath if not provided)
        
        Returns:
            str: Path to the downloaded file
            
        Raises:
            ValueError: If URL is invalid or filename conflicts
            IOError: If download fails or file already exists when overwrite=False
            urllib.error.URLError: If URL cannot be accessed
        """
        # Validate URL
        parsed_url = urlparse(doc_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {doc_url}")
        
        # Only allow http and https schemes
        if parsed_url.scheme not in ('http', 'https'):
            raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only http and https are supported.")
        
        # Generate filename if not provided
        if filename is None:
            # Use URL filename or generate based on URL hash
            original_filename = Path(parsed_url.path).name
            if original_filename and '.' in original_filename:
                filename = original_filename
            else:
                # Generate filename from URL hash to ensure uniqueness
                url_hash = hashlib.md5(doc_url.encode()).hexdigest()[:8]
                filename = f"document_{url_hash}.download"
        
        # Validate filename
        if not filename or filename in ('.', '..'):
            raise ValueError(f"Invalid filename: {filename}")
        
        # Construct target file path
        base_path = target_dir or self.targetpath
        self._ensure_directory_exists(base_path)
        target_file = Path(base_path) / filename
        
        # Check if file already exists
        if target_file.exists() and not overwrite:
            raise IOError(f"File already exists: {target_file}. Use overwrite=True to replace it.")
        
        # Download the file
        try:
            with urlopen(doc_url) as response:
                # Get file info
                content_length = response.headers.get('content-length')
                
                # Read and save file
                with open(target_file, 'wb') as f:
                    chunk_size = 8192  # 8KB chunks
                    total_size = 0
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_size += len(chunk)
                
                print(f"Downloaded {total_size} bytes to {target_file}")
                if content_length:
                    print(f"Expected size: {content_length} bytes")
                
        except Exception as e:
            # Clean up partially downloaded file
            if target_file.exists():
                target_file.unlink()
            raise IOError(f"Download failed: {e}") from e
        
        return str(target_file)
