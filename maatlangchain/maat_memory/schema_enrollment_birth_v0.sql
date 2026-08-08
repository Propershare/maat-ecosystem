-- Maat Enrollment Birth + Chronology v0
-- Every enrollment gets a birth certificate and an append-only chronology.
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS maat_enrollment_births (
    birth_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    principal_id VARCHAR(128) NOT NULL,
    os_user TEXT,
    tool_type VARCHAR(64) NOT NULL DEFAULT 'cursor',
    ring VARCHAR(32) NOT NULL DEFAULT 'outer'
        CHECK (ring IN ('inner', 'middle', 'outer')),
    role VARCHAR(64) NOT NULL DEFAULT 'general',
    working_on TEXT NOT NULL,
    full_identity JSONB NOT NULL DEFAULT '{}'::jsonb,
    invite_id UUID,
    episode_id VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'alive'
        CHECK (status IN ('alive', 'revoked', 'superseded')),
    born_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS maat_enrollment_births_agent_alive_uidx
    ON maat_enrollment_births (agent_id)
    WHERE status = 'alive';

CREATE INDEX IF NOT EXISTS maat_enrollment_births_principal_idx
    ON maat_enrollment_births (principal_id, born_at DESC);
CREATE INDEX IF NOT EXISTS maat_enrollment_births_machine_idx
    ON maat_enrollment_births (machine_id, born_at DESC);
CREATE INDEX IF NOT EXISTS maat_enrollment_births_agent_idx
    ON maat_enrollment_births (agent_id, born_at DESC);

CREATE TABLE IF NOT EXISTS maat_enrollment_chronology (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_id UUID NOT NULL REFERENCES maat_enrollment_births(birth_id) ON DELETE CASCADE,
    agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    principal_id VARCHAR(128),
    event_type VARCHAR(64) NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    working_on TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_enrollment_chronology_birth_idx
    ON maat_enrollment_chronology (birth_id, occurred_at ASC);
CREATE INDEX IF NOT EXISTS maat_enrollment_chronology_agent_idx
    ON maat_enrollment_chronology (agent_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS maat_enrollment_chronology_type_idx
    ON maat_enrollment_chronology (event_type, occurred_at DESC);

-- Identity fields on agents (explicit; also mirrored in birth.full_identity)
ALTER TABLE maat_agents
    ADD COLUMN IF NOT EXISTS working_on TEXT;
ALTER TABLE maat_agents
    ADD COLUMN IF NOT EXISTS os_user TEXT;
ALTER TABLE maat_agents
    ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE maat_agents
    ADD COLUMN IF NOT EXISTS birth_id UUID;
