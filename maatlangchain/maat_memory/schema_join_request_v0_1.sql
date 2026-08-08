-- Join ritual v0.1 hardening — operator authority + identity split
-- Safe to re-run.

CREATE TABLE IF NOT EXISTS maat_operator_authority (
    principal_id VARCHAR(128) PRIMARY KEY REFERENCES maat_principals(principal_id),
    token_hash VARCHAR(128) NOT NULL,
    display_name TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'revoked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rotated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

ALTER TABLE maat_join_requests
    ADD COLUMN IF NOT EXISTS operator_principal_id VARCHAR(128);
ALTER TABLE maat_join_requests
    ADD COLUMN IF NOT EXISTS decided_by_agent VARCHAR(128);
ALTER TABLE maat_join_requests
    ADD COLUMN IF NOT EXISTS decided_by_principal VARCHAR(128);
ALTER TABLE maat_join_requests
    ADD COLUMN IF NOT EXISTS approved_scopes JSONB;
ALTER TABLE maat_join_requests
    ADD COLUMN IF NOT EXISTS denied_scopes JSONB;

-- Backfill operator principal from principal_id where missing
UPDATE maat_join_requests
SET operator_principal_id = COALESCE(operator_principal_id, principal_id)
WHERE operator_principal_id IS NULL;

ALTER TABLE maat_join_sentinel_events
    ADD COLUMN IF NOT EXISTS event_hash VARCHAR(128);
ALTER TABLE maat_join_sentinel_events
    ADD COLUMN IF NOT EXISTS previous_event_hash VARCHAR(128);
