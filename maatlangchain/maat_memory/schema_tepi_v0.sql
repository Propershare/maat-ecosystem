-- Maat TEPI v0 — Temporal · Episodic · Principal · Identity-path
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS maat_principals (
    principal_id VARCHAR(128) PRIMARY KEY,
    display_name TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'revoked')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS maat_tepi_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    principal_id VARCHAR(128) NOT NULL REFERENCES maat_principals(principal_id),
    agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    ring VARCHAR(32) NOT NULL CHECK (ring IN ('inner', 'middle', 'outer')),
    episode_id VARCHAR(128),
    event_type VARCHAR(64) NOT NULL,
    summary TEXT,
    memory_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_tepi_log_principal_idx
    ON maat_tepi_log (principal_id, seen_at DESC);
CREATE INDEX IF NOT EXISTS maat_tepi_log_agent_idx
    ON maat_tepi_log (agent_id, seen_at DESC);
CREATE INDEX IF NOT EXISTS maat_tepi_log_episode_idx
    ON maat_tepi_log (episode_id);

ALTER TABLE maat_agents
    ADD COLUMN IF NOT EXISTS principal_id VARCHAR(128);

DO $$
BEGIN
    ALTER TABLE maat_agents
        ADD CONSTRAINT maat_agents_principal_fk
        FOREIGN KEY (principal_id) REFERENCES maat_principals(principal_id)
        ON DELETE SET NULL;
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

CREATE INDEX IF NOT EXISTS maat_agents_principal_idx ON maat_agents (principal_id);

-- Seed lab sovereign if empty (idempotent)
INSERT INTO maat_principals (principal_id, display_name, metadata)
VALUES ('imhotep', 'Imhotep', '{"lab":"tehuti","role":"sovereign"}'::jsonb)
ON CONFLICT (principal_id) DO NOTHING;
