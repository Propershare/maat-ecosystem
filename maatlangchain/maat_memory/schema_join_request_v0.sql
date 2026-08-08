-- Maat Join Request → Head Operator decide → local produce (v0)
-- Agent knocks; Imhotep allows/denies; Sentinel/gitMaat records; local agent produces materials.
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS maat_join_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN (
            'pending', 'allowed', 'denied', 'expired', 'produced', 'revoked'
        )),
    -- Who is knocking
    requesting_agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    hostname TEXT,
    os_user TEXT,
    tool_type VARCHAR(64) NOT NULL DEFAULT 'cursor',
    workspace_root TEXT,
    workspace_slug TEXT,
    -- For whom / what
    principal_id VARCHAR(128) NOT NULL DEFAULT 'imhotep',
    requested_ring VARCHAR(32) NOT NULL DEFAULT 'outer'
        CHECK (requested_ring IN ('inner', 'middle', 'outer')),
    requested_role VARCHAR(64) NOT NULL DEFAULT 'fleet_tester',
    working_on TEXT NOT NULL,
    requested_organs JSONB NOT NULL DEFAULT '[]'::jsonb,
    identity_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    message TEXT,
    -- Head Operator decision
    decided_by VARCHAR(128),
    decided_at TIMESTAMPTZ,
    decision VARCHAR(32)
        CHECK (decision IS NULL OR decision IN ('allow', 'deny')),
    decision_reason TEXT,
    -- Provision (one-time redeem after allow)
    grant_id UUID,
    provision_token_hash VARCHAR(128),
    provision_expires_at TIMESTAMPTZ,
    produced_at TIMESTAMPTZ,
    birth_id UUID,
    -- Sentinel / governance
    correlation_id VARCHAR(128),
    sentinel_case_id VARCHAR(128),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '48 hours')
);

CREATE INDEX IF NOT EXISTS maat_join_requests_status_idx
    ON maat_join_requests (status, created_at DESC);
CREATE INDEX IF NOT EXISTS maat_join_requests_principal_idx
    ON maat_join_requests (principal_id, status);
CREATE INDEX IF NOT EXISTS maat_join_requests_agent_idx
    ON maat_join_requests (requesting_agent_id, created_at DESC);

CREATE TABLE IF NOT EXISTS maat_join_grants (
    grant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES maat_join_requests(request_id) ON DELETE CASCADE,
    agent_id VARCHAR(128) NOT NULL,
    principal_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    ring VARCHAR(32) NOT NULL DEFAULT 'outer',
    role VARCHAR(64) NOT NULL DEFAULT 'fleet_tester',
    working_on TEXT NOT NULL,
    scopes JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_organs JSONB NOT NULL DEFAULT '[]'::jsonb,
    discovery_url TEXT,
    session_token_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'issued'
        CHECK (status IN ('issued', 'redeemed', 'revoked', 'expired')),
    issued_by VARCHAR(128) NOT NULL,
    redeemed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    local_bundle JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_join_grants_status_idx ON maat_join_grants (status, expires_at);
CREATE INDEX IF NOT EXISTS maat_join_grants_agent_idx ON maat_join_grants (agent_id);

-- Append-only join sentinel ledger (Head Operator + system)
CREATE TABLE IF NOT EXISTS maat_join_sentinel_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES maat_join_requests(request_id) ON DELETE SET NULL,
    grant_id UUID,
    event_type VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    decision VARCHAR(32),
    summary TEXT NOT NULL DEFAULT '',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_join_sentinel_request_idx
    ON maat_join_sentinel_events (request_id, occurred_at ASC);
CREATE INDEX IF NOT EXISTS maat_join_sentinel_type_idx
    ON maat_join_sentinel_events (event_type, occurred_at DESC);
