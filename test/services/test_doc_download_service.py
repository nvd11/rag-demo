import src.configs.config
import os
import pytest
import tempfile
import shutil
from pathlib import Path



# Import dependencies
from src.configs.config import project_path as config_project_path
from src.services.doc_download_service import DocDownloadService


class TestDocDownloadServiceDownload:
    """Test cases for DocDownloadService.download() method without mocking."""
    
    
    
    @pytest.fixture
    def doc_service(self):
        """Create DocDownloadService instance with temporary directory."""
        # Create unique temporary directory for each test
        temp_dir = tempfile.mkdtemp(prefix="test_docs_")
        service = DocDownloadService()
        yield service, temp_dir  # Return both service and temp directory
        
        # Cleanup temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_download_text_file_success(self, doc_service):
        """Test successful download of a text file."""
        # Use a reliable public text file
        url = "https://httpbin.org/robots.txt"
        service, temp_dir = doc_service
        
        file_path = service.download(url, target_dir=temp_dir)
        
        # Verify file was created
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
            assert "User-agent" in content or "Disallow" in content
        
        # Verify file is in correct directory
        assert Path(file_path).parent == Path(temp_dir)
    
    def test_download_with_custom_filename(self, doc_service):
        """Test download with custom filename."""
        url = "https://httpbin.org/robots.txt"
        custom_filename = "my_custom_robots.txt"
        service, temp_dir = doc_service
        
        file_path = service.download(url, filename=custom_filename, target_dir=temp_dir)
        
        # Verify filename
        assert os.path.basename(file_path) == custom_filename
        assert os.path.exists(file_path)
    
    def test_download_json_file(self, doc_service):
        """Test successful download of a JSON file."""
        url = "https://httpbin.org/json"
        service, temp_dir = doc_service
        
        file_path = service.download(url, target_dir=temp_dir)
        
        # Verify file exists and contains JSON content
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            content = f.read()
            assert "slideshow" in content or "json" in content.lower()
    
    def test_download_overwrite_existing_file(self, doc_service):
        """Test downloading over an existing file with overwrite=True."""
        url = "https://httpbin.org/robots.txt"
        filename = "test_overwrite.txt"
        service, temp_dir = doc_service
        
        # First download
        file_path1 = service.download(url, filename=filename, target_dir=temp_dir)
        assert os.path.exists(file_path1)
        
        # Get original size
        original_size = os.path.getsize(file_path1)
        
        # Second download without overwrite (should fail)
        with pytest.raises(IOError, match="File already exists"):
            service.download(url, filename=filename, overwrite=False, target_dir=temp_dir)
        
        # Second download with overwrite (should succeed)
        file_path2 = service.download(url, filename=filename, overwrite=True, target_dir=temp_dir)
        assert file_path2 == file_path1
        assert os.path.exists(file_path2)
        
        # File should be same size (same content)
        new_size = os.path.getsize(file_path2)
        assert new_size == original_size
    
    def test_download_invalid_url(self, doc_service):
        """Test download with invalid URL."""
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "http://",
            "https://",
            ""
        ]
        service, temp_dir = doc_service
        
        for invalid_url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid URL"):
                service.download(invalid_url, target_dir=temp_dir)
    
    def test_download_invalid_filename(self, doc_service):
        """Test download with invalid filename."""
        url = "https://httpbin.org/robots.txt"
        service, temp_dir = doc_service
        
        invalid_filenames = [".", "..", ""]
        
        for invalid_filename in invalid_filenames:
            with pytest.raises(ValueError, match="Invalid filename"):
                service.download(url, filename=invalid_filename, target_dir=temp_dir)
    
    def test_download_unreachable_url(self, doc_service):
        """Test download with unreachable URL."""
        unreachable_url = "https://nonexistent-domain-12345.com/file.txt"
        service, temp_dir = doc_service
        
        with pytest.raises(IOError, match="Download failed"):
            service.download(unreachable_url, target_dir=temp_dir)
    
    def test_download_automatic_filename_generation(self, doc_service):
        """Test automatic filename generation for different URLs."""
        service, temp_dir = doc_service
        
        # URL with clear filename
        url1 = "https://httpbin.org/robots.txt"
        file_path1 = service.download(url1, target_dir=temp_dir)
        filename1 = os.path.basename(file_path1)
        assert filename1 == "robots.txt"
        
        # URL without clear filename (should generate hash-based name)
        url2 = "https://httpbin.org/"
        file_path2 = service.download(url2, target_dir=temp_dir)
        filename2 = os.path.basename(file_path2)
        assert filename2.startswith("document_")
        assert filename2.endswith(".download")
        assert len(filename2) > 10  # Should contain hash
    
    def test_download_large_file(self, doc_service):
        """Test download of a larger file to test chunking."""
        # Use a moderately sized test file
        url = "https://httpbin.org/bytes/1024"  # 1KB of random data
        service, temp_dir = doc_service
        
        file_path = service.download(url, target_dir=temp_dir)
        
        # Verify file exists and has correct size
        assert os.path.exists(file_path)
        file_size = os.path.getsize(file_path)
        assert file_size == 1024
    
    def test_download_directory_creation(self, doc_service):
        """Test that download creates target directory if it doesn't exist."""
        service, temp_dir = doc_service
        
        # Create a subdirectory to test directory creation
        target_dir = Path(temp_dir) / "test_subdir"
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Download should create the directory
        url = "https://httpbin.org/robots.txt"
        file_path = service.download(url, target_dir=str(target_dir))
        
        # Verify directory was created
        assert target_dir.exists()
        assert target_dir.is_dir()
        assert os.path.exists(file_path)
        assert Path(file_path).parent == target_dir
    
    def test_download_multiple_files(self, doc_service):
        """Test downloading multiple files to the same directory."""
        service, temp_dir = doc_service
        
        urls = [
            "https://httpbin.org/robots.txt",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid"
        ]
        
        downloaded_files = []
        
        for url in urls:
            file_path = service.download(url, target_dir=temp_dir)
            downloaded_files.append(file_path)
            assert os.path.exists(file_path)
        
        # Verify all files are unique
        unique_files = set(downloaded_files)
        assert len(unique_files) == len(downloaded_files)
        
        # Verify all files are in the target directory
        for file_path in downloaded_files:
            assert Path(file_path).parent == Path(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
