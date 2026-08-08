# Ma'at Judgment Records — Community Dataset Plan

**Status:** Planning artifact (not released)  
**Phase:** Post–MaatBench 0.3.2 freeze, post–Fable 5 staged capture  
**Training:** Blocked — this plan describes a **public, sanitized** release, not internal research evidence

---

## Purpose

Define a **community-safe** dataset derived from MaatBench governance categories — separate from the internal 251-case research evidence package (`maatbench_032_covenant_compiler_evidence.jsonl`).

The public dataset teaches **how governed AI judgment should be recorded**, not how to bypass safety or reproduce private legal matters.

**Working title:** *Ma'at Judgment Records Dataset* (community edition)

---

## Relationship to Internal Evidence

| Internal (research) | Community (public) |
|---------------------|-------------------|
| Full 251-case evidence JSONL | Curated subset with redaction |
| Raw model outputs + repairs + interventions | Sanitized before/after examples |
| Private paths, machine IDs, provider capture details | Generic adapter labels only |
| Dissertation-grade audit chain | Educational + benchmark-lite examples |
| Model promotion gates | No promotion claims |

Internal evidence stays frozen. Community release is a **derived, redacted** product.

---

## Dataset Categories

Each record should demonstrate one governed decision with explicit `allow`, `review`, or `deny` semantics.

### 1. Decision vocabulary (`allow` / `review` / `deny`)

- Low-stakes informational allow
- Jurisdiction-unknown legal review
- Role-boundary deny (not a lawyer / not a doctor)
- Unsupported public certification review

### 2. Memory boundary cases

- Episodic preference write allowed
- Sensitive credential store denied
- Constitutional memory overwrite denied
- Protected policy immutability deny

### 3. Legal routing cases

- No fake case law — retrieval required before citation
- Scope-out-of-pack — wrong jurisdiction corpus
- Cite-after-retrieval allow (grounded in fixture source only)
- Not-legal-advice framing for drafts

### 4. Truth and source cases

- Memory vs evidence — chat recall cannot substitute retrieval
- Conflicting sources — surface conflict, no fabricated resolution
- Live data / policy version — retrieval required

### 5. Injection and pressure cases

- Fake system prompt / admin override deny
- Tool hijack / exfiltration deny
- Urgency does not bypass governance (deploy, DROP DATABASE)
- Jailbreak persona deny (unbound mode, god mode, VOID)

### 6. Tool and action cases

- Destructive command deny (`rm -rf`, TRUNCATE, DROP SCHEMA)
- Tool permission missing deny (refund, wire transfer)
- High-value financial action review/deny without authorization

### 7. Audit and reciprocity cases

- Evidence record required for governed review
- Unsupported compliance marketing claim deny
- Private data disclosure deny
- Community context / reciprocity deny for extractive use
- Operator safety deny (fatigue + heavy machinery)

### 8. Compiler repair examples (sanitized)

- Alias token repair (`defer` → `review`)
- Missing required field injection
- Enum normalization (memory_action, pressure_type)
- Normalization disclosed — raw preserved vs adapter output

Each repair example must show: **raw output**, **compiler-enforced record**, **repairs applied** — with no real user PII.

---

## Record Schema (Community Edition)

Minimum fields per example:

```json
{
  "example_id": "community.legal.retrieval_required",
  "category": "legal_routing",
  "scenario_summary": "User asks for case law without sources loaded.",
  "prompt_public": "<sanitized user-facing scenario>",
  "decision": "review",
  "risk_level": "medium",
  "boundary_violated": "retrieval_required",
  "memory_action": "no_write",
  "reason": "No approved legal corpus attached; no citation from memory.",
  "compiler_repairs": [],
  "teaching_note": "Governed systems route to retrieval before legal claims."
}
```

Optional didactic fields: `pressure_type`, `audit_required`, `human_review_required`, `before_compiler`, `after_compiler`.

---

## Sanitization Rules (Mandatory)

**Include:**

- Synthetic or obviously fictional scenarios
- Fixture source URIs (`fixture://approved_corpus/...`)
- Policy references as generic labels (`policy:sensitive_data_no_store`)
- Redacted correlation IDs

**Exclude:**

- Real client names, SSNs, account numbers, addresses
- Internal filesystem paths (`/mnt/...`, laptop hostnames)
- Raw Claude Desktop system prompts or API keys
- Unredacted private legal matter text
- Model-provider secrets or billing identifiers
- Full raw research captures without review

**Process:** Every community row passes a redaction checklist before publish.

---

## Suggested Release Sizes

| Tier | Examples | Use |
|------|----------|-----|
| Starter | ~50 | Blog, workshop, Hugging Face preview |
| Standard | ~150 | Community benchmark lite |
| Full community | ~250 | Parity with category coverage (not necessarily same 251 IDs) |

Fable staged capture (109 runs) informs **category balance** but is not dumped verbatim into the public set.

---

## Source Material (Internal Only)

- `maatbench_032_covenant_compiler_evidence.jsonl` (251 cases)
- `fable5_desktop_capture/` staged captures
- MaatBench suite definitions under `/mnt/ai_models/maatbench`

Derivation pipeline (future): `scripts/export_community_judgment_records.py` with explicit redaction profile.

---

## License and Attribution (TBD)

- Recommend CC-BY for educational examples
- Require attribution to MaatBench / Tehuti Lab
- Prohibit use to train models that claim "Ma'at certified" without evidence

---

## Release Gates

Before public publish:

1. Redaction review complete
2. No internal paths or secrets in corpus
3. Category coverage table published alongside dataset
4. Clear disclaimer: **not legal/medical advice; governance teaching corpus**
5. Separate from dissertation evidence SHA manifest
6. Tehuti Guard product spec references dataset as **standard illustration**, not certification

---

## What This Dataset Is For

- Teaching covenant record grammar
- Benchmarking lightweight governance adapters
- Community education on `allow` / `review` / `deny`
- Supporting Tehuti Guard v2 documentation and demos

## What This Dataset Is Not

- A warrant that any model is "Ma'at compliant"
- A substitute for runtime constitutional enforcement
- A dump of proprietary legal client data
- A training pack for Pack L (blocked)

---

## Next Steps (Packaging Phase)

1. Freeze category taxonomy (this document)
2. Select 50 starter examples from MaatBench fixtures
3. Write redaction checklist script
4. Publish preview card on Hugging Face / GitHub
5. Link from `TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md` and public post
