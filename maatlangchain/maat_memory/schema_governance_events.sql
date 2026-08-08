-- Compact governance events (Guard / Forge) for analytics and Studio — not full request dumps.

CREATE TABLE IF NOT EXISTS maat_governance_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    record_type VARCHAR(64) NOT NULL,
    machine_id VARCHAR(256),
    agent VARCHAR(128) NOT NULL DEFAULT 'system',
    explanation_id VARCHAR(128),
    task_id VARCHAR(256),
    session_id VARCHAR(256),
    correlation_id VARCHAR(128),
    source_service VARCHAR(64),
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS maat_governance_events_record_ts_idx
    ON maat_governance_events (record_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS maat_governance_events_machine_ts_idx
    ON maat_governance_events (machine_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS maat_governance_events_explanation_idx
    ON maat_governance_events (explanation_id)
    WHERE explanation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS maat_governance_events_task_idx
    ON maat_governance_events (task_id)
    WHERE task_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS maat_governance_events_payload_gin
    ON maat_governance_events USING GIN (payload);

CREATE INDEX IF NOT EXISTS maat_governance_events_correlation_idx
    ON maat_governance_events (correlation_id)
    WHERE correlation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS maat_governance_events_source_ts_idx
    ON maat_governance_events (source_service, timestamp DESC);
