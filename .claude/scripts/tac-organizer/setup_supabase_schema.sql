-- ============================================================================
-- AI-Agent-KB Supabase pgvector Schema
-- ============================================================================
-- Purpose: Create vector index table and semantic search function for
--          Tier 2 KB components (commands, agents, skills, hooks, scripts)
--
-- Run via Supabase SQL Editor or psql:
--   psql $SUPABASE_DB_URL -f setup_supabase_schema.sql
-- ============================================================================

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing table if recreating (comment out for production)
-- DROP TABLE IF EXISTS kb_index;
-- DROP FUNCTION IF EXISTS search_kb;

-- ============================================================================
-- KB Index Table
-- ============================================================================
-- Stores embeddings and metadata for KB components
-- Uses OpenAI text-embedding-3-small (1536 dimensions)

CREATE TABLE IF NOT EXISTS kb_index (
    id TEXT PRIMARY KEY,                    -- Unique identifier (folder/filename)
    file_path TEXT NOT NULL,                -- Full path relative to KB root
    folder TEXT NOT NULL,                   -- Top-level folder (commands, agents, skills, etc.)
    type TEXT NOT NULL,                     -- Component type (command, agent, skill, hook, expert)
    name TEXT NOT NULL,                     -- Human-readable name from frontmatter
    summary TEXT NOT NULL,                  -- Purpose/description for display
    tags TEXT[],                            -- Tags from frontmatter (if any)
    embedding vector(1536),                 -- OpenAI text-embedding-3-small embedding
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast similarity search using IVFFlat
-- lists = sqrt(number_of_records) is a good starting point
-- With ~850 records, lists = 30 would be reasonable, using 100 for growth
CREATE INDEX IF NOT EXISTS kb_index_embedding_idx
ON kb_index USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for folder-based filtering
CREATE INDEX IF NOT EXISTS kb_index_folder_idx ON kb_index (folder);

-- Index for type-based filtering
CREATE INDEX IF NOT EXISTS kb_index_type_idx ON kb_index (type);

-- ============================================================================
-- Semantic Search Function
-- ============================================================================
-- Returns KB entries matching a query embedding, ranked by similarity

CREATE OR REPLACE FUNCTION search_kb(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    folder_filter text DEFAULT NULL,
    type_filter text DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    file_path TEXT,
    folder TEXT,
    type TEXT,
    name TEXT,
    summary TEXT,
    tags TEXT[],
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.file_path,
        kb.folder,
        kb.type,
        kb.name,
        kb.summary,
        kb.tags,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM kb_index kb
    WHERE
        1 - (kb.embedding <=> query_embedding) > match_threshold
        AND (folder_filter IS NULL OR kb.folder = folder_filter)
        AND (type_filter IS NULL OR kb.type = type_filter)
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- Search by Folder Function
-- ============================================================================
-- Returns all entries in a folder, optionally filtered by type

CREATE OR REPLACE FUNCTION get_kb_by_folder(
    target_folder text,
    target_type text DEFAULT NULL,
    result_limit int DEFAULT 100
)
RETURNS TABLE (
    id TEXT,
    file_path TEXT,
    type TEXT,
    name TEXT,
    summary TEXT,
    tags TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.file_path,
        kb.type,
        kb.name,
        kb.summary,
        kb.tags
    FROM kb_index kb
    WHERE
        kb.folder = target_folder
        AND (target_type IS NULL OR kb.type = target_type)
    ORDER BY kb.name
    LIMIT result_limit;
END;
$$;

-- ============================================================================
-- Update Timestamp Trigger
-- ============================================================================
-- Automatically update updated_at when a row is modified

CREATE OR REPLACE FUNCTION update_kb_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS kb_index_updated_at ON kb_index;
CREATE TRIGGER kb_index_updated_at
    BEFORE UPDATE ON kb_index
    FOR EACH ROW
    EXECUTE FUNCTION update_kb_timestamp();

-- ============================================================================
-- Statistics View
-- ============================================================================
-- View for monitoring index status

CREATE OR REPLACE VIEW kb_index_stats AS
SELECT
    folder,
    type,
    COUNT(*) as count,
    MAX(updated_at) as last_updated
FROM kb_index
GROUP BY folder, type
ORDER BY folder, type;

-- Grant necessary permissions (adjust role as needed)
-- GRANT SELECT ON kb_index TO authenticated;
-- GRANT EXECUTE ON FUNCTION search_kb TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_kb_by_folder TO authenticated;
-- GRANT SELECT ON kb_index_stats TO authenticated;

-- ============================================================================
-- Sample Queries
-- ============================================================================
-- These are examples, not executed:

-- Search for commit-related content:
-- SELECT * FROM search_kb(
--     '[embedding vector here]'::vector(1536),
--     0.7,  -- threshold
--     10,   -- limit
--     NULL, -- no folder filter
--     NULL  -- no type filter
-- );

-- Get all commands:
-- SELECT * FROM get_kb_by_folder('commands');

-- Get all agents:
-- SELECT * FROM get_kb_by_folder('agents');

-- Check index statistics:
-- SELECT * FROM kb_index_stats;
