# Maat Provenance (T1)

**Frame is the control; detection is only a tripwire.**

## What this is

Nonce-delimited quarantine + declared `content_origin` so untrusted Memory cannot break out of its render frame, and writers cannot inherit trust by silence.

## Controls

| Control | Behavior |
|---------|----------|
| Quarantine frame | 128-bit nonce per render; body cannot forge closer |
| No DEFAULT on `content_origin` | INSERT must state provenance |
| Legacy rows | `legacy_unclassified` → quarantined; debt visible until zero |
| Fail-closed derive | absent/unknown source → `derived_untrusted`, never `agent_authored` |
| Unknown enum | `ProvenanceError` — refuses to guess |
| Unscoped write | `ScopeViolation` — absence ≠ compliance |

## Run tests (no DB)

```bash
cd /mnt/data_drive/maatlangchain
python3 -m maat_memory.maat_provenance.test_provenance
# or:
python3 maat_memory/maat_provenance/test_provenance.py
```

Expect: `20/20 controls held`

## Migrate

```bash
psql "$PGVECTOR_DB_URL" -f maat_memory/schema_provenance_t1.sql
```

## Wire (API half of T1)

- `log_task(..., origin=)` / `log_decision(..., origin=)` — required
- Session bootstrap: `render_memory_context(rows)`

## Not T1

- T2 autonomy budget
- T3 credential split — **Hermes slice done** (`maat_credentials/`); n8n/ka-auth/daemon remain debt
