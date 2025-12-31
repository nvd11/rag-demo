# Refactor Plan: Document Filtering Support

## 1. Objective
Enable the retrieval system to filter search results by **Topics** and **Documents**. 
This involves:
1.  Creating a `topics` table to categorize documents.
2.  Associating documents with topics.
3.  Enhancing the retrieval logic to filter by `topic_name` or `document_ids`.

## 2. Database Schema Changes

### 2.1 New Table: `topics`
*   `id` (UUID, PK)
*   `name` (VARCHAR, Unique, e.g., "VisionFive 2")
*   `description` (TEXT)

### 2.2 New Table: `document_topics` (Many-to-Many Relationship)
*   `document_id` (UUID, FK -> documents.id)
*   `topic_id` (UUID, FK -> topics.id)
*   Primary Key: `(document_id, topic_id)`

## 3. Architecture Changes

### 3.1 DAO Layer (`src/dao/vector_dao.py` & new `src/dao/topic_dao.py`)
*   **TopicDAO**: Manage topics and document associations.
    *   `create_topic(name: str, description: str = None, creator_user_id: int = None) -> Topic`
    *   `get_topic_by_name(name: str) -> Optional[Topic]`
    *   `add_document_to_topic(topic_id: UUID, document_id: UUID, creator_user_id: int = None)`
    *   `get_document_ids_by_topic(topic_name: str) -> List[UUID]`
*   **VectorDAO**:
    *   Update `search_similar_chunks` to accept `document_ids: List[UUID]`.
    *   (Optimization) It doesn't need to know about topics directly; the Service layer will resolve Topic -> DocIDs.

### 3.2 Service Layer (`src/services/retrieval_service.py`)
*   **Method**: `search_knowledge_base`
*   **Change**: Add optional parameter `topic: str = None`.
*   **Logic**: 
    *   If `topic` is provided, call `TopicDAO` to get all `document_ids` for that topic.
    *   Pass these `document_ids` to `VectorDAO.search_similar_chunks`.

### 2.3 Tool Layer (`src/tools/knowledge_base_tool.py`)
*   **Method**: `search_similar_chunks`
*   **Change**: Add an optional parameter `document_ids: Optional[List[uuid.UUID]] = None`.
*   **Implementation**:
    *   If `document_ids` is provided, add a `WHERE document_id IN (...)` clause to the SQLAlchemy query.
    *   This ensures the vector search only considers chunks belonging to the specified documents.

### 2.2 Service Layer (`src/services/retrieval_service.py`)
*   **Method**: `search_knowledge_base`
*   **Change**: Add optional parameter `filter_document_ids: Optional[List[uuid.UUID]] = None`.
*   **Logic**: Pass this list down to the DAO's `search_similar_chunks`.

### 2.3 Tool Layer (`src/tools/knowledge_base_tool.py`)
*   **Change**: Update `search_knowledge_base` tool definition.
*   **Note**: For now, the Tool might keep a simple signature (only `query`) if we rely on the Agent's construction time to bind specific document IDs (e.g., creating a "VisionFive 2 Search Tool" that effectively calls `service.search(..., doc_ids=[vf2_id])`).
*   **Advanced**: Alternatively, we can let the LLM decide which doc IDs to search, but LLM usually doesn't know UUIDs. A better pattern is to have the Agent initialized with a scope, or look up Document IDs by name first (Metadata Search).
*   **Plan**: We will update the `create_retrieval_tool` factory to accept a `filter_document_ids` argument, allowing us to create "Scoped Tools".

### 2.4 Agent Layer (`src/agents/knowledge_base_agent.py`)
*   **Class**: `KnowledgeBaseAgent`
*   **Change**:
    *   Update `__init__` to accept `document_ids: Optional[List[uuid.UUID]]`.
    *   When creating the tool, pass these IDs to create a scoped tool for this agent instance.
    *   This allows us to instantiate a `KnowledgeBaseAgent` specifically for "VisionFive 2" documents.

## 3. Implementation Steps

1.  **Refactor DAO**: Update `src/dao/vector_dao.py` to support `IN` clause filtering.
2.  **Refactor Service**: Update `src/services/retrieval_service.py` to pass the filter.
3.  **Refactor Tool**: Update `src/tools/knowledge_base_tool.py` factory function.
4.  **Refactor Agent**: Update `src/agents/knowledge_base_agent.py` to support scoping.
5.  **Tests**: Update `test/dao/test_vector_dao_search.py` to verify filtering works.

## 4. Ingestion Refactoring (`src/services/data_load_service.py`)

The data ingestion process needs to be updated to support associating documents with topics upon upload.

*   **Method**: `process_document` (or equivalent entry point)
*   **Change**: Add optional parameter `topic_name: str = None` and `creator_user_id: int = None`.
*   **Logic**:
    1.  Create Document (existing logic).
    2.  If `topic_name` is provided:
        *   Check if Topic exists (using `TopicDAO`).
        *   If not, create it.
        *   Associate the new Document with the Topic.

## 5. Verification
*   Create a test with 2 documents.
*   Search with filter -> Should only return chunks from the target document.
*   Search without filter -> Should return chunks from both (based on similarity).
