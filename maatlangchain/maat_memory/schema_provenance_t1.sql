-- T1 content provenance + Fix 02 storage_class coherence
-- Law: no DEFAULT on content_origin (writers must state provenance).
-- Existing rows → legacy_unclassified (honest past; quarantined at render).
-- Safe to re-run (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS / DO blocks).

BEGIN;

-- ── Enum-like CHECK helpers via TEXT + CHECK (portable; no CREATE TYPE dependency) ──

-- maat_decisions
ALTER TABLE maat_decisions
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_decisions
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_decisions
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_decisions_content_origin_chk'
  ) THEN
    ALTER TABLE maat_decisions
      ADD CONSTRAINT maat_decisions_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

-- Explicitly refuse DEFAULT trust inheritance
ALTER TABLE maat_decisions ALTER COLUMN content_origin DROP DEFAULT;

-- maat_tasks
ALTER TABLE maat_tasks
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_tasks
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_tasks
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_tasks_content_origin_chk'
  ) THEN
    ALTER TABLE maat_tasks
      ADD CONSTRAINT maat_tasks_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

ALTER TABLE maat_tasks ALTER COLUMN content_origin DROP DEFAULT;

-- maat_learnings
ALTER TABLE maat_learnings
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_learnings
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_learnings
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_learnings_content_origin_chk'
  ) THEN
    ALTER TABLE maat_learnings
      ADD CONSTRAINT maat_learnings_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

ALTER TABLE maat_learnings ALTER COLUMN content_origin DROP DEFAULT;

-- maat_changes
ALTER TABLE maat_changes
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_changes
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_changes
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_changes_content_origin_chk'
  ) THEN
    ALTER TABLE maat_changes
      ADD CONSTRAINT maat_changes_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

ALTER TABLE maat_changes ALTER COLUMN content_origin DROP DEFAULT;

-- maat_conversations (user paste / agent reply mixed — origin on row is coarse)
ALTER TABLE maat_conversations
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_conversations
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_conversations
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_conversations_content_origin_chk'
  ) THEN
    ALTER TABLE maat_conversations
      ADD CONSTRAINT maat_conversations_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

ALTER TABLE maat_conversations ALTER COLUMN content_origin DROP DEFAULT;

-- maat_artifacts
ALTER TABLE maat_artifacts
  ADD COLUMN IF NOT EXISTS content_origin TEXT;

UPDATE maat_artifacts
  SET content_origin = 'legacy_unclassified'
  WHERE content_origin IS NULL;

ALTER TABLE maat_artifacts
  ALTER COLUMN content_origin SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_artifacts_content_origin_chk'
  ) THEN
    ALTER TABLE maat_artifacts
      ADD CONSTRAINT maat_artifacts_content_origin_chk
      CHECK (content_origin IN (
        'agent_authored',
        'human_authored',
        'system_generated',
        'external_untrusted',
        'derived_untrusted',
        'legacy_unclassified'
      ));
  END IF;
END $$;

ALTER TABLE maat_artifacts ALTER COLUMN content_origin DROP DEFAULT;

-- ── Fix 02: storage_class as declared NOT NULL with coherence CHECK ──────────
-- object_backed requires digest; reference_only requires URI.
-- Existing rows: infer class from columns, else reference_only if uri set else object_backed if digest.

ALTER TABLE maat_artifacts
  ADD COLUMN IF NOT EXISTS storage_class TEXT;

-- Honest debt: rows with neither digest nor URI get an explicit legacy URI marker
-- so reference_only coherence holds without inventing a digest.
UPDATE maat_artifacts
  SET uri = 'maat://legacy_unclassified/' || id::text
  WHERE (uri IS NULL OR uri = '')
    AND (content_sha256 IS NULL OR content_sha256 = '');

UPDATE maat_artifacts
  SET storage_class = CASE
    WHEN content_sha256 IS NOT NULL AND content_sha256 <> '' THEN 'object_backed'
    WHEN uri IS NOT NULL AND uri <> '' THEN 'reference_only'
    ELSE 'reference_only'
  END
  WHERE storage_class IS NULL;

ALTER TABLE maat_artifacts
  ALTER COLUMN storage_class SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_artifacts_storage_class_chk'
  ) THEN
    ALTER TABLE maat_artifacts
      ADD CONSTRAINT maat_artifacts_storage_class_chk
      CHECK (storage_class IN ('object_backed', 'reference_only'));
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'maat_artifacts_storage_coherence_chk'
  ) THEN
    ALTER TABLE maat_artifacts
      ADD CONSTRAINT maat_artifacts_storage_coherence_chk
      CHECK (
        (storage_class = 'object_backed'
          AND content_sha256 IS NOT NULL AND content_sha256 <> '')
        OR
        (storage_class = 'reference_only'
          AND uri IS NOT NULL AND uri <> '')
      );
  END IF;
END $$;

ALTER TABLE maat_artifacts ALTER COLUMN storage_class DROP DEFAULT;

-- Debt index (verify query 3: count until zero)
CREATE INDEX IF NOT EXISTS maat_tasks_legacy_origin_idx
  ON maat_tasks (content_origin)
  WHERE content_origin = 'legacy_unclassified';

CREATE INDEX IF NOT EXISTS maat_decisions_legacy_origin_idx
  ON maat_decisions (content_origin)
  WHERE content_origin = 'legacy_unclassified';

COMMIT;

-- ── Verify queries (run after migrate; debt must be visible) ────────────────
-- 1) No DEFAULT on content_origin:
--    SELECT column_default FROM information_schema.columns
--    WHERE table_name='maat_tasks' AND column_name='content_origin';
--    → NULL
-- 2) INSERT without origin fails:
--    INSERT INTO maat_tasks (agent, title) VALUES ('x','y');  -- ERROR
-- 3) Legacy debt:
--    SELECT 'maat_tasks' AS t, COUNT(*) FROM maat_tasks WHERE content_origin='legacy_unclassified'
--    UNION ALL ...
