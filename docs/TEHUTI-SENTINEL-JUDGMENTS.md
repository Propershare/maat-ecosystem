# Tehuti Sentinel — runtime judgment cases

**Office (stable):** **Tehuti Sentinel** — runtime constitutional overseer (watcher / boundary / escalation trigger).  
**Implementation (replaceable):** e.g. Gemma e2b classifier today; another small model or verifier tomorrow.  
**Do not** name the office after the model: *“We use a Gemma-based implementation of Tehuti Sentinel”* is correct; *“Gemma Guard is our doctrine”* is not.

**Schema:** [`../maat-ecosystem/skeleton/schemas/tehuti_sentinel_case.schema.json`](../maat-ecosystem/skeleton/schemas/tehuti_sentinel_case.schema.json) (`$id`: `maat:tehuti_sentinel_case:v1`)

**Example:** [`../maat-ecosystem/skeleton/schemas/examples/tehuti_sentinel_case_001.example.json`](../maat-ecosystem/skeleton/schemas/examples/tehuti_sentinel_case_001.example.json)

Legacy filename **`GEMMA-GUARD-TASK.md`** is retired; use this document.

---

## What this contract does

1. **Stabilizes the task** — bounded outputs, explicit `surface`, Ma’at-linked justification.  
2. **Reduces drift** — schema changes are visible; v1 is a start, not scripture.  
3. **Bridges theory ↔ engineering** — dissertation can cite structured cases with surfaces, decisions, reason codes, provenance.

---

## Naming map (concise)

| Concept | Name | Notes |
|---------|------|--------|
| Runtime overseer office | **Tehuti Sentinel** | Stable across model swaps |
| Implementation | Gemma (e2b), etc. | Replaceable |
| Pre-execution choke point (subcomponent) | **Maat Gate** (optional) | One gate among many surfaces |
| Retrospective memory / learning | **Sankofa** | Not the live runtime watcher |
| Frontier capability | Mythos-class | Stress + telemetry, not naming |

---

## Coverage over count

Spread hand-labeled cases across **surfaces** — early target distribution (adjust to reality):

| Surface | Target (starter) |
|---------|-------------------|
| `tool_call` | 10 |
| `memory_write` | 10 |
| `retrieval` | 10 |
| `shell_execution` | 10 |
| `scope_drift` | 5 |
| `escalation` | 5 |

**50 files** as separate JSON under [`guard_cases/`](../guard_cases/) for easy review; merge to JSONL when stable.

---

## Schema notes (v1.1)

- **`evidence`** — `source_type`, `source_ref`, `notes` so labels stay **auditable** (what was relied on).  
- **`label.additional_reason_codes`** — optional, when multiple reasons apply.  
- **`outcome.final_action`** — room for **classifier vs rule engine** divergence (document in `outcome.notes` until a future schema splits layers explicitly).

---

## Pressure path — what to watch as real cases land

### 1. Wire vs label vocabulary (keep this sharp)

**Tehuti Guard v1 wire** (`POST /decision`) returns **only:** `allow` | `deny` | `review` | `quarantine` | `escalate` — see [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) §1.

**In this document / guard_cases labels:** the word **“conditional”** is an **explanation-only** teaching term — *proceed only if gates pass*. It is **not** a returned API value. Map human labels to wire terms: **conditional** ≈ **`review`** or **`quarantine`** depending on severity; never invent a fifth wire string in adapters.

| Label / doctrine term | Typical meaning | Wire (Guard v1) |
|----------------------|-----------------|-----------------|
| **escalate** | Human or higher authority required | `escalate` |
| **conditional** (doctrine) | Gates must pass before proceed | **`review`** or **`quarantine`** (not `conditional`) |

If reviewers disagree, note why in `outcome.notes` until schema v2 clarifies.

### 2. Multi-reason is normal

Do not force false simplicity. Real cases may stack **scope violation + insufficient provenance + excessive authority** (and more). Use **`additional_reason_codes`**; do not collapse to one code when two apply.

### 3. Evidence quality = label quality

The `evidence` field only helps if reviewers **use it** with discipline:

- Is **`source_ref`** stable enough to audit later (id, path, event ref)?
- Could a **second reviewer** reconstruct why the label was chosen?
- If not, fix the case before it enters training gold.

### 4. Rebalance after the first batch

The 10/10/10/10/5/5 mix is a **starter**. After batch one, **shift counts toward where failure and reviewer disagreement cluster** (e.g. shell + memory if that is where the mess is).

### 5. Next truth test

**Fill `guard_cases/` with messy real examples** and see **where v1 schema breaks**. That breakage teaches more than another week of naming.

---

## Order of work

1. Schema + examples (here).  
2. **Real** cases under `guard_cases/`.  
3. JSONL + eval (per surface + confusion matrix).  
4. Then adapter / tuning — not before.

---

## Dissertation (one sentence)

Runtime constitutional governance is operationalized as structured judgment cases with explicit surfaces, decision classes, reason codes, Ma’at-linked justifications, evidence pointers, and auditable context — enabling measurement, not only persuasion.

**Formal variant (office vs implementation):**  
The Tehuti Sentinel is a **constitutional runtime oversight role**, instantiated through a **replaceable** small-model classifier and **constrained** by rule-based enforcement — so the office survives model swaps.

---

## Related

- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) — **Sentinel vs Guard adapters** (authority boundary)  
- [`TRUTH-AND-VERIFICATION.md`](TRUTH-AND-VERIFICATION.md) — **truth vs MaatBench** (ground truth → eval → bench)  
- `maat-runtime` — `maat-immune` deterministic gate  
- `MAATBENCH-v2.md` — verification organ  
- `Maat-Constitutional-Infrastructure-Dissertation/SCRIBE-PROTOCOL.md` — manuscript layers  
