-- Maat Agent Messaging v0
-- Cross-agent communication via Postgres NOTIFY/LISTEN.
-- Safe to re-run (IF NOT EXISTS).

-- ── Agent Messages ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS maat_agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent VARCHAR(128) NOT NULL,
    to_agent VARCHAR(128),              -- NULL = broadcast
    message_type VARCHAR(32) NOT NULL DEFAULT 'notify'
        CHECK (message_type IN ('delegate', 'notify', 'query', 'reply', 'broadcast')),
    subject VARCHAR(256),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    correlation_id UUID,                -- ties request→reply chains
    in_reply_to UUID REFERENCES maat_agent_messages(id),
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'delivered', 'read', 'replied', 'failed', 'expired')),
    priority VARCHAR(16) NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    ttl_seconds INTEGER DEFAULT 86400,  -- 24h default; NULL = never expire
    expires_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- ── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS maat_agent_messages_to_agent_idx
    ON maat_agent_messages (to_agent, status, created_at DESC);
CREATE INDEX IF NOT EXISTS maat_agent_messages_from_agent_idx
    ON maat_agent_messages (from_agent, created_at DESC);
CREATE INDEX IF NOT EXISTS maat_agent_messages_correlation_idx
    ON maat_agent_messages (correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS maat_agent_messages_status_idx
    ON maat_agent_messages (status, created_at);
CREATE INDEX IF NOT EXISTS maat_agent_messages_expires_idx
    ON maat_agent_messages (expires_at) WHERE expires_at IS NOT NULL AND status = 'pending';
CREATE INDEX IF NOT EXISTS maat_agent_messages_broadcast_idx
    ON maat_agent_messages (created_at DESC) WHERE to_agent IS NULL;

-- ── NOTIFY trigger: push new messages to listening agents ──────────────────
CREATE OR REPLACE FUNCTION maat_agent_message_notify() RETURNS trigger AS $$
DECLARE
    channel_name TEXT;
BEGIN
    -- Notify the target agent's channel
    IF NEW.to_agent IS NOT NULL THEN
        channel_name := 'maat_agent_' || replace(NEW.to_agent, '-', '_');
        PERFORM pg_notify(channel_name, json_build_object(
            'id', NEW.id,
            'from_agent', NEW.from_agent,
            'message_type', NEW.message_type,
            'subject', NEW.subject,
            'priority', NEW.priority,
            'created_at', NEW.created_at
        )::text);
    ELSE
        -- Broadcast: notify on the broadcast channel
        PERFORM pg_notify('maat_agent_broadcast', json_build_object(
            'id', NEW.id,
            'from_agent', NEW.from_agent,
            'message_type', NEW.message_type,
            'subject', NEW.subject,
            'priority', NEW.priority,
            'created_at', NEW.created_at
        )::text);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS maat_agent_message_notify_trigger ON maat_agent_messages;
CREATE TRIGGER maat_agent_message_notify_trigger
    AFTER INSERT ON maat_agent_messages
    FOR EACH ROW EXECUTE FUNCTION maat_agent_message_notify();

-- ── Message delivery log (audit trail) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS maat_agent_message_delivery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES maat_agent_messages(id) ON DELETE CASCADE,
    agent_id VARCHAR(128) NOT NULL,
    machine_id VARCHAR(128),
    event VARCHAR(32) NOT NULL
        CHECK (event IN ('notified', 'delivered', 'read', 'replied', 'failed', 'expired')),
    error_detail TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS maat_agent_message_delivery_msg_idx
    ON maat_agent_message_delivery (message_id, occurred_at);
CREATE INDEX IF NOT EXISTS maat_agent_message_delivery_agent_idx
    ON maat_agent_message_delivery (agent_id, occurred_at DESC);

-- ── Cleanup: mark expired messages ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION maat_agent_message_expire() RETURNS void AS $$
BEGIN
    UPDATE maat_agent_messages
    SET status = 'expired'
    WHERE status = 'pending'
      AND expires_at IS NOT NULL
      AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ── Plane metadata ─────────────────────────────────────────────────────────
INSERT INTO maat_metadata (key, value)
VALUES (
    'agent_messaging',
    '{
        "version": "0.1.0",
        "schema": "maat.agent_messaging.v0",
        "transport": "pg_notify_listen",
        "doctrine": "hermes/docs/MAAT-AGENT-MESSAGING-v0.md",
        "channels": ["maat_agent_<agent_id>", "maat_agent_broadcast"],
        "message_types": ["delegate", "notify", "query", "reply", "broadcast"],
        "governance": "enrolled agents only; ring-aware routing planned v0.2"
    }'::jsonb
) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
