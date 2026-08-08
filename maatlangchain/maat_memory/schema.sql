-- Maat Memory PostgreSQL Schema
-- Cross-session memory system for Cursor and OpenCode agents

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Sessions table
CREATE TABLE IF NOT EXISTS maat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    summary TEXT,
    key_points JSONB DEFAULT '[]'::jsonb,
    files_modified JSONB DEFAULT '[]'::jsonb,
    tasks_completed JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Conversations table with vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS maat_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES maat_sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    user_query TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    -- Combined text for embedding (user_query + agent_response)
    combined_text TEXT GENERATED ALWAYS AS (user_query || ' ' || agent_response) STORED,
    -- Vector embedding for semantic search
    embedding vector(384),  -- all-MiniLM-L6-v2 dimension
    tools_used JSONB DEFAULT '[]'::jsonb,
    files_accessed JSONB DEFAULT '[]'::jsonb,
    decisions_made JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS maat_conversations_embedding_idx 
    ON maat_conversations 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create index for agent and timestamp queries
CREATE INDEX IF NOT EXISTS maat_conversations_agent_timestamp_idx 
    ON maat_conversations (agent, timestamp DESC);

-- Audit trail table
CREATE TABLE IF NOT EXISTS maat_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource TEXT NOT NULL,
    before_data JSONB,
    after_data JSONB,
    reason TEXT,
    maat_compliance JSONB DEFAULT '{"truth": true, "balance": true, "order": true, "self_reflection": true}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index for audit queries
CREATE INDEX IF NOT EXISTS maat_audit_trail_agent_timestamp_idx 
    ON maat_audit_trail (agent, timestamp DESC);

-- Tasks table
CREATE TABLE IF NOT EXISTS maat_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    related_files JSONB DEFAULT '[]'::jsonb,
    dependencies JSONB DEFAULT '[]'::jsonb,
    completion_notes TEXT
);

-- Create index for task queries
CREATE INDEX IF NOT EXISTS maat_tasks_agent_status_idx 
    ON maat_tasks (agent, status);

-- Decisions table
CREATE TABLE IF NOT EXISTS maat_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    context TEXT NOT NULL,
    options_considered JSONB DEFAULT '[]'::jsonb,
    decision_made TEXT NOT NULL,
    rationale TEXT NOT NULL,
    outcome TEXT,
    maat_alignment JSONB DEFAULT '{"truth": "", "balance": "", "order": "", "self_reflection": ""}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Changes table
CREATE TABLE IF NOT EXISTS maat_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    summary TEXT NOT NULL,
    diff_preview TEXT,
    reason TEXT,
    reverted BOOLEAN DEFAULT FALSE,
    revert_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index for change queries
CREATE INDEX IF NOT EXISTS maat_changes_agent_file_idx 
    ON maat_changes (agent, file_path);

-- Errors table
CREATE TABLE IF NOT EXISTS maat_errors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    stack_trace TEXT,
    context_data JSONB DEFAULT '{}'::jsonb,
    resolution TEXT,
    prevention TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Learnings table
CREATE TABLE IF NOT EXISTS maat_learnings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    agent VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    insight TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    applied BOOLEAN DEFAULT FALSE,
    application_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Agent memory table (replaces JSON agent_memory structure)
CREATE TABLE IF NOT EXISTS maat_agent_memory (
    agent VARCHAR(50) PRIMARY KEY,
    session_id UUID REFERENCES maat_sessions(id) ON DELETE SET NULL,
    last_updated TIMESTAMP WITH TIME ZONE,
    context_data JSONB DEFAULT '[]'::jsonb,
    preferences JSONB DEFAULT '{}'::jsonb,
    work_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- System metadata table
CREATE TABLE IF NOT EXISTS maat_metadata (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Insert default metadata
INSERT INTO maat_metadata (key, value) 
VALUES (
    'system_info',
    '{
        "version": "1.0.0",
        "system": "MaatLangChain Cross-Session Memory",
        "purpose": "Shared memory for Cursor and OpenCode agents",
        "governance": "Maat principles"
    }'::jsonb
) ON CONFLICT (key) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_maat_sessions_updated_at 
    BEFORE UPDATE ON maat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maat_tasks_updated_at 
    BEFORE UPDATE ON maat_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maat_agent_memory_updated_at 
    BEFORE UPDATE ON maat_agent_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maat_metadata_updated_at 
    BEFORE UPDATE ON maat_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function for semantic search in conversations
CREATE OR REPLACE FUNCTION maat_search_conversations(
    query_embedding vector(384),
    agent_filter VARCHAR(50) DEFAULT NULL,
    limit_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    session_id UUID,
    "timestamp" TIMESTAMP WITH TIME ZONE,
    agent VARCHAR(50),
    user_query TEXT,
    agent_response TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.session_id,
        c.timestamp,
        c.agent,
        c.user_query,
        c.agent_response,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM maat_conversations c
    WHERE 
        (agent_filter IS NULL OR c.agent = agent_filter)
        AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

