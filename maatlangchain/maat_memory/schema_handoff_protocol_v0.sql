-- Maat Handoff Protocol v0
-- Standard offer → receive → acknowledge → verify flow + ring visibility tier.
-- Safe to re-run.

-- ── Artifact visibility ring (column, not only metadata.audience) ─────────
ALTER TABLE maat_artifacts
    ADD COLUMN IF NOT EXISTS ring VARCHAR(32) NOT NULL DEFAULT 'outer';

DO $$
BEGIN
    ALTER TABLE maat_artifacts
        ADD CONSTRAINT maat_artifacts_ring_check
        CHECK (ring IN ('inner', 'middle', 'outer'));
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

CREATE INDEX IF NOT EXISTS maat_artifacts_ring_idx ON maat_artifacts (ring);
CREATE INDEX IF NOT EXISTS maat_artifacts_ring_produced_idx
    ON maat_artifacts (ring, produced_at DESC NULLS LAST);

-- Backfill from metadata.audience / metadata.ring when still default outer
UPDATE maat_artifacts SET ring = CASE
    WHEN COALESCE(metadata->>'ring', '') IN ('inner', 'middle', 'outer')
        THEN metadata->>'ring'
    WHEN COALESCE(metadata->>'audience', '') IN (
        'every_lab_agent', 'public', 'outer', 'visitor'
    ) THEN 'outer'
    WHEN COALESCE(metadata->>'audience', '') IN (
        'scholarship', 'middle', 'scholar', 'fleet_ops'
    ) THEN 'middle'
    WHEN COALESCE(metadata->>'audience', '') IN (
        'inner', 'principal_private', 'canon', 'lab_inner'
    ) THEN 'inner'
    ELSE ring
END
WHERE ring = 'outer'
   OR COALESCE(metadata->>'ring', '') IN ('inner', 'middle', 'outer');

-- Keep metadata.ring mirrored for older readers
UPDATE maat_artifacts
SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('ring', ring)
WHERE COALESCE(metadata->>'ring', '') IS DISTINCT FROM ring;

-- ── Session presence ring (acting clearance this session) ─────────────────
ALTER TABLE maat_session_presence
    ADD COLUMN IF NOT EXISTS ring VARCHAR(32) NOT NULL DEFAULT 'outer';

DO $$
BEGIN
    ALTER TABLE maat_session_presence
        ADD CONSTRAINT maat_session_presence_ring_check
        CHECK (ring IN ('inner', 'middle', 'outer'));
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

-- ── Handoffs (standard protocol ledger) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS maat_handoffs (
    handoff_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol VARCHAR(64) NOT NULL DEFAULT 'maat.handoff.v0',
    kind VARCHAR(32) NOT NULL DEFAULT 'work'
        CHECK (kind IN ('work', 'signup', 'artifact', 'revoke')),
    status VARCHAR(32) NOT NULL DEFAULT 'offered'
        CHECK (status IN (
            'offered', 'received', 'acknowledged', 'verified',
            'rejected', 'expired', 'superseded'
        )),
    from_agent VARCHAR(128) NOT NULL,
    to_agent VARCHAR(128),                 -- NULL = open claim (first eligible)
    principal_id VARCHAR(128),
    machine_id VARCHAR(128),
    ring VARCHAR(32) NOT NULL DEFAULT 'outer'
        CHECK (ring IN ('inner', 'middle', 'outer')),
    summary TEXT NOT NULL DEFAULT '',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    challenge JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_by VARCHAR(128),
    acknowledged_by VARCHAR(128),
    verified_by VARCHAR(128),
    reject_reason TEXT,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ,
    offered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    received_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_handoffs_status_idx
    ON maat_handoffs (status, offered_at DESC);
CREATE INDEX IF NOT EXISTS maat_handoffs_to_agent_idx
    ON maat_handoffs (to_agent, status);
CREATE INDEX IF NOT EXISTS maat_handoffs_from_agent_idx
    ON maat_handoffs (from_agent, offered_at DESC);
CREATE INDEX IF NOT EXISTS maat_handoffs_kind_idx
    ON maat_handoffs (kind, status);

-- ── Invites (signup tokens; one-time, ring-capped) ────────────────────────
CREATE TABLE IF NOT EXISTS maat_invites (
    invite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    principal_id VARCHAR(128) NOT NULL,
    intended_ring VARCHAR(32) NOT NULL DEFAULT 'outer'
        CHECK (intended_ring IN ('inner', 'middle', 'outer')),
    intended_tool VARCHAR(64),
    intended_machine VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'issued'
        CHECK (status IN ('issued', 'claimed', 'consumed', 'revoked', 'expired')),
    handoff_id UUID REFERENCES maat_handoffs(handoff_id) ON DELETE SET NULL,
    created_by VARCHAR(128) NOT NULL,
    claimed_by VARCHAR(128),
    consumed_by VARCHAR(128),
    expires_at TIMESTAMPTZ NOT NULL,
    claimed_at TIMESTAMPTZ,
    consumed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_invites_status_idx ON maat_invites (status, expires_at);
CREATE INDEX IF NOT EXISTS maat_invites_principal_idx ON maat_invites (principal_id);
