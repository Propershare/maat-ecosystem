# `guard_cases/` — hand-labeled Tehuti Sentinel cases

**New here?** Start with **[`SIMPLE-START.md`](SIMPLE-START.md)** — same ideas, **no** full review homework. Open the full ritual only when you’re ready.

**Format:** One JSON file per case, valid against  
[`../maat-ecosystem/skeleton/schemas/tehuti_sentinel_case.schema.json`](../maat-ecosystem/skeleton/schemas/tehuti_sentinel_case.schema.json).

**Naming:** `guard_case_<surface>_<nnn>.json` (e.g. `guard_case_tool_call_001.json`) or keep `guard_case_001` style — stay consistent.

## Starter distribution (target)

Prioritize **coverage**, not only volume:

| Count | `surface` |
|------|-----------|
| 10 | `tool_call` |
| 10 | `memory_write` |
| 10 | `retrieval` |
| 10 | `shell_execution` |
| 5 | `scope_drift` |
| 5 | `escalation` |

**Total:** 50 — adjust after you see real gaps.

**Starter batch (10 files):** `guard_case_*.json` in this folder — **synthetic** seeds for **surface coverage** and schema validation; **replace or augment** with redacted real traces as you collect them.

**Dry run:** Use [`REVIEW-DRY-RUN.md`](REVIEW-DRY-RUN.md) (two reviewers, disagreement column) before treating labels as stable.

## Workflow

1. Capture **real** or **realistic** payloads from runtime (redact secrets).  
2. Label with **primary** `reason_code`; use `additional_reason_codes` when needed.  
3. Fill **`evidence`** with what the judgment relied on.  
4. When stable, concatenate to `train.jsonl` (one object per line) for tooling.

## First Batch Review Checklist (Tehuti Sentinel v1)

Tight review ritual after the first messy batch lands — forces signal, not vibes.

### 1. Disagreement map

- Where did reviewers assign different `decision` or `reason_code`?
- Are disagreements due to unclear policy, weak schema, or missing context?

### 2. Reason code fit

- Did any case feel **forced** into a `reason_code`?
- Do you see recurring patterns **not** captured by current codes?

### 3. Conditional vs escalate drift

- Are **`conditional`** cases actually machine-checkable?
- Are some **`conditional`** cases really **`escalate`** in disguise?

### 4. Evidence integrity

- Can a **second reviewer** understand and verify the decision from `evidence.source_ref`?
- Are references **stable and specific** enough for audit?

### 5. Classifier vs enforcement boundary

- Do `label.decision` and `outcome.final_action` **diverge**?
- If yes, is the reason clear (rule-engine override, policy gate, missing authority)?

---

This checklist turns human disagreement into structured signal, tests whether the schema matches reality, and keeps Tehuti Sentinel in the **classifier** role — not pseudo-sovereignty. Stats from this pass are dissertation-grade operationalization evidence.

## Validate

```bash
python3 -c "
import json, jsonschema
from pathlib import Path
s = Path('maat-ecosystem/skeleton/schemas/tehuti_sentinel_case.schema.json')
schema = json.loads(s.read_text())
for p in Path('guard_cases').glob('*.json'):
    jsonschema.validate(json.loads(p.read_text()), schema)
    print('OK', p)
"
```

(Run from lab root `~/.n8n`.)
