# MAAT Portability Guarantee

## The Promise

Any compliant MAAT implementation must preserve:

1. **Identity** across runtime changes
2. **Task history** across model changes
3. **Memory** across backend changes
4. **Policies** across UI changes
5. **Event logs** across transport changes

If a user changes their model from Ollama to OpenAI, they do not lose who they are.
If a user changes their database from Postgres to SQLite, they do not lose what they know.
If a user changes their agent runtime, their policies still hold.

## What Migration Means

Migration is not "export and pray."

Migration is a **first-class operation** with guarantees:

```
maat migrate --from postgres --to sqlite
maat migrate --export identity+memory+policy --output maat-backup.json
maat migrate --import maat-backup.json
```

### What Gets Exported

| Layer | Format | Guarantee |
|-------|--------|-----------|
| Identity | JSON (maat:identity:v1) | Lossless |
| Memory | JSON array (maat:memory:v1) | Lossless, including class and reversibility |
| Policy | JSON (maat:policy:v1) | Lossless, including rule evaluation order |
| Tasks | JSON array (maat:task:v1) | Lossless, including status history |
| Events | JSONL (maat:event:v1) | Append-only, never truncated on export |
| Learning | JSON array (maat:learning:v1) | Including before/after snapshots |

### What Does NOT Get Exported

- Embeddings (re-embed with the new model)
- Adapter configs (these are environment-specific)
- Session state (ephemeral by design)

## Embedding Portability

Embeddings are model-specific. When you change embedding models:

1. Export all memory content (text, not vectors)
2. Re-embed with the new model
3. Store with `embedding_model` field updated

This is why the memory schema stores `embedding_model` — so you always know what generated the vectors.

## The Test

A MAAT implementation passes portability if:

1. Export identity + memory + policy from Runtime A
2. Import into Runtime B (different model, different DB)
3. Agent can answer all 9 questions correctly:
   - Who am I? ✓
   - What am I allowed to do? ✓
   - What do I remember? ✓
   - What tools can I use? ✓
   - What tasks exist? ✓
   - What events have occurred? ✓
   - What can I learn? ✓
   - What requires escalation? ✓
   - What part of me can be swapped? ✓

If any answer is lost, the migration is non-compliant.
