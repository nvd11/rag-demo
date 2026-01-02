-- SQL Script to create tables for topic-based filtering

-- 1. Create topics table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    creator_user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_topics_creator ON topics(creator_user_id);

-- 2. Create document_topics association table (many-to-many)
CREATE TABLE IF NOT EXISTS document_topics (
    -- Hard foreign keys removed as requested.
    document_id UUID NOT NULL,
    topic_id UUID NOT NULL,
    creator_user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, topic_id)
);

-- Index for faster lookup
CREATE INDEX IF NOT EXISTS idx_document_topics_topic_id ON document_topics(topic_id);
