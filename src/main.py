import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.configs.config import project_path
from src.services.doc_data_service import DocDataService


def main():
    """Main function to download VisionFive2 PDF document."""
    try:
        # Initialize document service
        doc_service = DocDataService()
        
        # Download the PDF document
        pdf_url = 'https://doc.rvspace.org/VisionFive2/PDF/VisionFive2_DS.pdf'
        print(f"Downloading PDF from: {pdf_url}")
        
        file_path = doc_service.download(pdf_url, overwrite=True)
        print(f"Successfully downloaded to: {file_path}")
        
        # Verify file exists and show details
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            print(f"File: {file_name}")
            print(f"Size: {file_size} bytes ({file_size/1024:.2f} KB)")
        else:
            print("Error: Download failed - file not found")
            
    except ValueError as e:
        print(f"Validation error: {e}")
        return 1
    except IOError as e:
        print(f"Download error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    






    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)