import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.services.data_processing_service import DataProcessingService
from src.models.document_model import Document as DB_Document
from langchain_core.documents import Document as LC_Document
import uuid

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_vector_dao():
    dao = AsyncMock()
    # Mock create_document to return a DB Document with a UUID
    db_doc = MagicMock(spec=DB_Document)
    db_doc.id = uuid.uuid4()
    dao.create_document.return_value = db_doc
    return dao

@pytest.fixture
def mock_data_load_service():
    service = MagicMock()
    return service

@pytest.fixture
def mock_chunking_service():
    service = MagicMock()
    return service

@pytest.fixture
def mock_embedding_service():
    service = MagicMock()
    return service

@pytest.fixture
def processing_service(mock_session, mock_vector_dao, mock_data_load_service, mock_chunking_service, mock_embedding_service):
    # Patch dependencies inside DataProcessingService
    with patch("src.services.data_processing_service.VectorDAO", return_value=mock_vector_dao), \
         patch("src.services.data_processing_service.DataLoadService", return_value=mock_data_load_service), \
         patch("src.services.data_processing_service.ChunkingService", return_value=mock_chunking_service), \
         patch("src.services.data_processing_service.EmbeddingService", return_value=mock_embedding_service):
        
        service = DataProcessingService(mock_session)
        # Ensure our fixtures are actually used by the instance (redundant if patch works, but safer)
        service.vector_dao = mock_vector_dao
        service.data_load_service = mock_data_load_service
        service.chunking_service = mock_chunking_service
        service.embedding_service = mock_embedding_service
        return service

@pytest.mark.asyncio
async def test_process_file_success(processing_service, mock_vector_dao, mock_data_load_service, mock_chunking_service, mock_embedding_service):
    # --- Given ---
    file_path = "test.pdf"
    
    # Mock Document Loading
    mock_lc_doc = LC_Document(page_content="Full content", metadata={"page": 1})
    mock_data_load_service.load.return_value = [mock_lc_doc]
    
    # Mock Chunking
    chunk1 = "Chunk 1"
    chunk2 = "Chunk 2"
    mock_chunking_service.chunk_document.return_value = [chunk1, chunk2]
    
    # Mock Embedding
    mock_embedding_service.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
    
    # --- When ---
    doc_id = await processing_service.process_file(file_path)
    
    # --- Then ---
    # 1. Verify return value
    assert doc_id is not None
    
    # 2. Verify service interactions
    mock_data_load_service.load.assert_called_once_with(file_path)
    mock_chunking_service.chunk_document.assert_called_once_with(mock_lc_doc)
    mock_embedding_service.generate_embeddings.assert_called_once_with([chunk1, chunk2])
    
    # 3. Verify Database interactions
    mock_vector_dao.create_document.assert_called_once()
    mock_vector_dao.add_chunks.assert_called_once()
    mock_vector_dao.commit.assert_called_once()
    
    # 4. Verify data passed to DB
    call_args = mock_vector_dao.add_chunks.call_args
    assert call_args is not None
    chunks_data = call_args[0][1] # second arg is chunks_data
    
    assert len(chunks_data) == 2
    
    # Check first chunk data
    assert chunks_data[0]["content"] == chunk1
    assert chunks_data[0]["embedding"] == [0.1, 0.2]
    assert chunks_data[0]["metadata"] == {"page": 1}
    
    # Check second chunk data
    assert chunks_data[1]["content"] == chunk2
    assert chunks_data[1]["embedding"] == [0.3, 0.4]
    assert chunks_data[1]["metadata"] == {"page": 1}

@pytest.mark.asyncio
async def test_process_file_load_returns_empty(processing_service, mock_data_load_service, mock_vector_dao):
    mock_data_load_service.load.return_value = []
    
    result = await processing_service.process_file("empty.pdf")
    
    assert result is None
    mock_vector_dao.create_document.assert_not_called()

@pytest.mark.asyncio
async def test_process_file_chunking_returns_empty(processing_service, mock_data_load_service, mock_chunking_service, mock_vector_dao):
    mock_data_load_service.load.return_value = [LC_Document(page_content="")]
    mock_chunking_service.chunk_document.return_value = []
    
    result = await processing_service.process_file("test.pdf")
    
    assert result is None
    mock_vector_dao.create_document.assert_not_called()

@pytest.mark.asyncio
async def test_process_file_embedding_mismatch(processing_service, mock_data_load_service, mock_chunking_service, mock_embedding_service):
    mock_data_load_service.load.return_value = [LC_Document(page_content="content")]
    mock_chunking_service.chunk_document.return_value = ["c1", "c2"]
    # Return only 1 embedding for 2 chunks
    mock_embedding_service.generate_embeddings.return_value = [[0.1]]
    
    with pytest.raises(ValueError, match="Embedding generation failed to match chunk count"):
        await processing_service.process_file("test.pdf")

@pytest.mark.asyncio
async def test_process_file_load_exception(processing_service, mock_data_load_service):
    mock_data_load_service.load.side_effect = Exception("Load failed")
    
    with pytest.raises(Exception, match="Load failed"):
        await processing_service.process_file("test.pdf")
