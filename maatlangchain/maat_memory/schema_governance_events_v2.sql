-- Correlation + source for cross-system queries (Guard / Forge / Sentinel).

ALTER TABLE maat_governance_events
    ADD COLUMN IF NOT EXISTS correlation_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS source_service VARCHAR(64);

CREATE INDEX IF NOT EXISTS maat_governance_events_correlation_idx
    ON maat_governance_events (correlation_id)
    WHERE correlation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS maat_governance_events_source_ts_idx
    ON maat_governance_events (source_service, timestamp DESC);
