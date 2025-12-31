-- SQL Script to create tables for RAG system with Gemini Embeddings
-- Target Database: PostgreSQL with pgvector extension
-- Model: Google Gemini text-embedding-004 (Dimension: 768)

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create documents table (Parent table)
-- Stores metadata about the original documents.
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- File path or URL to the source document
    file_path VARCHAR(1024) NOT NULL,
    
    -- Optional title or display name
    title VARCHAR(255),
    
    -- User ID of the creator/uploader
    creator_user_id INTEGER,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on creator_user_id for filtering documents by user
CREATE INDEX IF NOT EXISTS idx_documents_creator 
ON documents(creator_user_id);


-- 3. Create document_chunks_gemini table (Child table)
-- Stores the actual text chunks and their embeddings.
-- Linked to documents table via foreign key.
CREATE TABLE IF NOT EXISTS document_chunks_gemini (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Key linking to the documents table
    -- Hard foreign key removed as requested.
    document_id UUID NOT NULL,
    
    -- The actual text content of the chunk
    content TEXT NOT NULL,
    
    -- Embedding vector. 768 dimensions for Gemini.
    embedding vector(768),
    
    -- Metadata specific to the chunk
    page_number INTEGER,              -- Page number in the original document
    chunk_index INTEGER NOT NULL,     -- Order index in the original document
    
    -- Flexible metadata storage
    metadata JSONB DEFAULT '{}',
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Indexes for Chunks

-- 4.1 Vector Index (HNSW)
-- Optimized for Cosine Similarity search.
CREATE INDEX IF NOT EXISTS idx_document_chunks_gemini_embedding 
ON document_chunks_gemini USING hnsw (embedding vector_cosine_ops);

-- 4.2 Foreign Key Index
-- Crucial for join performance and deletion speed.
CREATE INDEX IF NOT EXISTS idx_document_chunks_gemini_document_id 
ON document_chunks_gemini(document_id);

-- Usage Example:
-- 1. Insert Document:
-- INSERT INTO documents (file_path, creator_user_id) VALUES ('docs/manual.pdf', 101) RETURNING id;
-- (Assume returned id is '550e8400-e29b-41d4-a716-446655440000')

-- 2. Insert Chunks:
-- INSERT INTO document_chunks_gemini (document_id, content, embedding, chunk_index) 
-- VALUES ('550e8400-e29b-41d4-a716-446655440000', 'chunk text...', '[...]', 0);

-- 3. Search:
-- SELECT c.content, d.file_path 
-- FROM document_chunks_gemini c
-- JOIN documents d ON c.document_id = d.id
-- ORDER BY c.embedding <=> '[...]' LIMIT 5;
