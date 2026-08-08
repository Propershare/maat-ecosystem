-- Maat Memory Plane v0
-- Fleet registry, learning snapshots, storage roots, session presence.
-- Safe to re-run (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).

-- ── Machines ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS maat_machines (
    machine_id VARCHAR(128) PRIMARY KEY,
    hostname VARCHAR(128) NOT NULL,
    storage_roots JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(32) NOT NULL DEFAULT 'enrolled'
        CHECK (status IN ('enrolled', 'revoked', 'degraded')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_machines_status_idx ON maat_machines (status);
CREATE INDEX IF NOT EXISTS maat_machines_hostname_idx ON maat_machines (hostname);

-- ── Agents ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS maat_agents (
    agent_id VARCHAR(128) PRIMARY KEY,
    machine_id VARCHAR(128) REFERENCES maat_machines(machine_id) ON DELETE SET NULL,
    tool_type VARCHAR(64) NOT NULL DEFAULT 'cursor',
    ring VARCHAR(32) NOT NULL DEFAULT 'outer'
        CHECK (ring IN ('inner', 'middle', 'outer')),
    role VARCHAR(64) NOT NULL DEFAULT 'general',
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(32) NOT NULL DEFAULT 'enrolled'
        CHECK (status IN ('enrolled', 'revoked', 'suspended')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_agents_status_idx ON maat_agents (status);
CREATE INDEX IF NOT EXISTS maat_agents_machine_idx ON maat_agents (machine_id);

-- ── Session presence (live; not transcript store) ─────────────────────────
CREATE TABLE IF NOT EXISTS maat_session_presence (
    session_id UUID PRIMARY KEY,
    schema_version VARCHAR(64) NOT NULL DEFAULT 'swarm.session.v1',
    agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    role VARCHAR(64) NOT NULL DEFAULT 'general',
    task_id VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'idle', 'complete', 'failed')),
    current_topic TEXT,
    current_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    memory_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS maat_session_presence_active_idx
    ON maat_session_presence (status, last_seen_at DESC);
CREATE INDEX IF NOT EXISTS maat_session_presence_agent_idx
    ON maat_session_presence (agent_id, last_seen_at DESC);

-- ── Storage resolve map (logical → host path / object key) ────────────────
CREATE TABLE IF NOT EXISTS maat_storage_roots (
    root_id VARCHAR(128) PRIMARY KEY,
    storage_class VARCHAR(32) NOT NULL
        CHECK (storage_class IN (
            'constitutional', 'coordination', 'learning', 'artifact', 'ephemeral'
        )),
    scheme VARCHAR(32) NOT NULL DEFAULT 'file',
    base_uri TEXT NOT NULL,
    machine_id VARCHAR(128) REFERENCES maat_machines(machine_id) ON DELETE CASCADE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_storage_roots_machine_idx ON maat_storage_roots (machine_id);

-- ── Learning snapshot columns (extend existing maat_learnings) ────────────
ALTER TABLE maat_learnings
    ADD COLUMN IF NOT EXISTS learning_type VARCHAR(64) DEFAULT 'memory_consolidation',
    ADD COLUMN IF NOT EXISTS before_snapshot JSONB,
    ADD COLUMN IF NOT EXISTS after_snapshot JSONB,
    ADD COLUMN IF NOT EXISTS approved_by VARCHAR(128),
    ADD COLUMN IF NOT EXISTS reversible BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS rolled_back BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS storage_class VARCHAR(32) NOT NULL DEFAULT 'learning',
    ADD COLUMN IF NOT EXISTS machine_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS guard_decision VARCHAR(32),
    ADD COLUMN IF NOT EXISTS content_sha256 VARCHAR(64);

-- Widen agent columns where historically VARCHAR(50) is too tight for plane IDs
DO $$
BEGIN
    ALTER TABLE maat_learnings ALTER COLUMN agent TYPE VARCHAR(128);
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- ── Artifact object store (Balance — portable bytes, not host file://) ────
-- Catalog (maat_artifacts) can point at maat://object/<sha256>.
-- Any enrolled machine with PG access can fetch content without shared NFS.
CREATE TABLE IF NOT EXISTS maat_artifact_objects (
    sha256 VARCHAR(64) PRIMARY KEY,
    content BYTEA NOT NULL,
    content_type VARCHAR(128) NOT NULL DEFAULT 'application/octet-stream',
    byte_len INTEGER NOT NULL,
    logical_path TEXT,
    slug VARCHAR(128),
    source_uri TEXT,
    machine_id VARCHAR(128),
    public_uri TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_artifact_objects_slug_idx
    ON maat_artifact_objects (slug) WHERE slug IS NOT NULL;
CREATE INDEX IF NOT EXISTS maat_artifact_objects_created_idx
    ON maat_artifact_objects (created_at DESC);

-- Catalog portability columns (safe if already present)
ALTER TABLE maat_artifacts
    ADD COLUMN IF NOT EXISTS content_sha256 VARCHAR(64),
    ADD COLUMN IF NOT EXISTS portable_uri TEXT;

CREATE INDEX IF NOT EXISTS maat_artifacts_sha_idx
    ON maat_artifacts (content_sha256) WHERE content_sha256 IS NOT NULL;
CREATE INDEX IF NOT EXISTS maat_artifacts_portable_idx
    ON maat_artifacts (portable_uri) WHERE portable_uri IS NOT NULL;

-- ── Plane metadata ────────────────────────────────────────────────────────
INSERT INTO maat_metadata (key, value)
VALUES (
    'memory_plane',
    '{
        "version": "0.2.0",
        "schema": "maat.memory_plane.v0",
        "phase": "C_object_store",
        "doctrine": "hermes/docs/MAAT-MEMORY-PLANE-v0.md",
        "stack": "package/run/should/prove/resist/attest",
        "balance": "maat://object/<sha256> + optional https public_uri"
    }'::jsonb
) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
