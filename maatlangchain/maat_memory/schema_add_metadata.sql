-- Migration: Add metadata columns for machine/terminal tracking
-- This adds machine, terminal, and project information to sessions and conversations

-- Add metadata column to maat_sessions
ALTER TABLE maat_sessions 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Add metadata to conversations too
ALTER TABLE maat_conversations 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Create indexes for metadata queries (GIN index for JSONB)
CREATE INDEX IF NOT EXISTS maat_sessions_metadata_idx 
ON maat_sessions USING GIN (metadata);

CREATE INDEX IF NOT EXISTS maat_conversations_metadata_idx 
ON maat_conversations USING GIN (metadata);

-- Create specific indexes for common queries
CREATE INDEX IF NOT EXISTS maat_sessions_hostname_idx 
ON maat_sessions ((metadata->>'hostname'));

CREATE INDEX IF NOT EXISTS maat_sessions_machine_id_idx 
ON maat_sessions ((metadata->>'machine_id'));

CREATE INDEX IF NOT EXISTS maat_sessions_terminal_id_idx 
ON maat_sessions ((metadata->>'terminal_id'));

CREATE INDEX IF NOT EXISTS maat_conversations_hostname_idx 
ON maat_conversations ((metadata->>'hostname'));

CREATE INDEX IF NOT EXISTS maat_conversations_terminal_id_idx 
ON maat_conversations ((metadata->>'terminal_id'));

