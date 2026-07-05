# MAAT Workspace Audit — `/mnt/data_drive`

**Audit date:** 2026-07-04  
**Scope:** Research evidence, constitutional architecture, runtime/guard productization, workspace truth/order, coordination health  
**Auditor:** Cursor agent (`cursor_staydangerous`)  
**Method:** Read-only inspection of repos, frozen artifacts, Guard v2 MVP, gitMaat, and existing audit docs

---

## Executive Verdict

This workspace is in a **strong research state** and an **early productization state**, but not yet in a **fully governed operational state**.

The locked thesis is real and evidenced:

> **Training can improve the model. Prompting can improve the draft. The compiler governs the record.**

| Plane | Score | Summary |
|-------|-------|---------|
| **Research integrity** | High | MaatBench 0.3.2 frozen; dissertation arc clean; gates closed |
| **Runtime truth/order** | Partial | Guard v2 MVP built locally; not fully shipped or wired |
| **Workspace balance** | At risk | Parallel trees, naming collisions, unpushed drift |

**Overall:** The compiler thesis is proven. The Guard v2 slice exists. The workspace still needs canonical unification, git truth, and one live enforcement path before it can claim operational Ma'at.

---

## 1. Truth — What Is Actually Real

| Layer | Canonical truth | Status |
|-------|-----------------|--------|
| Research evidence | `/mnt/ai_models/maatbench` v0.3.2 + `Tehuti-Dataset/training/` freezes | **Strong** |
| Constitutional doctrine | `MAATBENCH_032_TECHNICAL_REPORT.md`, `MAAT_DISSERTATION_OUTLINE.md` | **Strong** |
| Ka-body platform | `maat-ecosystem/` per `MAAT-PRODUCT-MAP.md` | **Canonical, locally drifted** |
| Covenant compiler runtime | `/mnt/ai_models/maatbench/maatbench/covenant_compiler.py` | **Real** |
| Guard v2 enforcement | `maat-ecosystem/tehuti-guard/guard/` + `POST /compile-decision` | **Built locally, not fully shipped** |
| gitMaat coordination | `/home/suspect/.n8n/maatlangchain/maat_memory/` | **Import OK; DB unavailable on audit host** |
| TS coding CLI | `/mnt/data_drive/Maat-runtime/` | **Real repo, different product** |

### Critical truth gaps

**1. Two MaatBench trees**

- **Authoritative:** `/mnt/ai_models/maatbench` — has `covenant_compiler`, `record_modes`, v0.3.2
- **Ecosystem copy:** `maat-ecosystem/maatbench/` — lacks `covenant_compiler` and `record_modes`
- Guard v2 adapter resolves to the lab path first (`covenant_adapter.py`)

**2. Two "Maat Runtime" meanings**

- `Maat-runtime/` = upstream TS coding-agent monorepo fork
- "MAAT Runtime" in research docs = constitutional compiler + covenant record generator
- These are **not the same product**

---

## 2. Order — Is the Workspace Governed?

### Ordered well

- Frozen phase manifest with explicit training gates (`MAATBENCH_032_PHASE_FREEZE.json`)
- Clear research sequence: formation → compiler → freeze → dissertation → cross-model design → readiness review
- Guard product disambiguation in `TEHUTI-GUARD-PRODUCTS.md` and `MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md`
- Entry paths: `README.md`, `INITIATION.md`, `FIRST-RUN.md`, `MAAT-AUDIT-ACTION-PLAN.md`

### Out of order

| Issue | Evidence |
|-------|----------|
| Large unpushed Guard v2 work | `maat-ecosystem` working tree has Guard v2 MVP + broad local edits |
| Tehuti-Dataset not versioned | `/mnt/data_drive/Tehuti-Dataset` is not a git repo |
| Parallel legacy trees | Root-level duplicates vs `maat-ecosystem/` |
| Cross-model execution gate open | Readiness freeze: `execution_status: not_run` |
| Initiation user test pending | `MAAT-AUDIT-ACTION-PLAN.md` §4, §7 |

---

## 3. Balance — Are Competing Paths Controlled?

### Locked (good)

- No DPO, no Pass 6D, no broad SFT, no Pass 7B
- No model promotion from compiler-enforced success alone
- Model vs system governance distinction preserved
- Fable 5 treated as supporting evidence, not dissertation dependency

### Imbalanced (risk)

| Risk | Why it matters |
|------|----------------|
| Research vs product drift | Frozen research in `Tehuti-Dataset/training/`; Guard v2 uncommitted |
| Lab proof vs production proof | Demo exists; MCP/npm Guard and live surfaces not on `/compile-decision` |
| Two Guard products | Python lab API vs npm MCP proxy can diverge on wire contract |
| Two runtime names | Constitutional runtime concept vs TS CLI repo |
| Two workspace roots | `/mnt/data_drive` vs `/home/suspect/.n8n/` |

---

## 4. Justice — Are Claims Supported by Evidence?

### Claims that hold

| Claim | Evidence |
|-------|----------|
| Model alone fails integrated covenant validity | Pass 6C 0%; 0.3.1 raw 0%; Pass 7A raw 1.96%; prompted eval flat |
| Compiler-enforced governance works | 0.3.2: 88.84% enforced validity; 0% unsafe allow |
| Stronger models still need compiler | Fable 5 smoke: raw 0%; compiler_enforced 93.75% |
| System governance eligible; model promotion false | Frozen across phase freeze + dissertation outline |

### Claims ahead of evidence

| Claim | Gap |
|-------|-----|
| "MAAT Runtime passes MaatBench" | Compiler + Guard adapter local; not packaged or deployed |
| "Tehuti Guard v2 is built" | MVP in working tree; npm MCP side untouched |
| "Cross-model eval supports thesis" | Fable 5 smoke only (16 cases), not full 251-case eval |
| "gitMaat coordinates the workspace" | Import OK; PostgreSQL down on audit host |

---

## 5. Self-Reflection

Existing audits are strong and honest:

- `MAAT-AUDIT-ACTION-PLAN.md`
- `MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md`
- `Maat-runtime/Maat-AUDIT.md`
- Frozen manifests with SHA-256

Missing closure, not diagnosis: Guard v2 unpushed, MaatBench not unified in ecosystem copy, initiation user test not recorded.

---

## Layer Status Matrix

| Layer | Maturity | Notes |
|-------|----------|-------|
| MaatBench research | Frozen / review-eligible | 0.3.2 evidence package complete |
| Dissertation packaging | In progress | Outline + technical report ready |
| Cross-model eval | Design frozen, execution blocked | Smoke only for Fable 5 |
| Covenant compiler | Production-grade in lab | `/mnt/ai_models/maatbench` |
| Tehuti Guard v2 | MVP built locally | `/compile-decision`, adapter, tests, demo |
| Tehuti Guard MCP (npm) | v1 scaffolding | Not yet constitutional |
| Maat-runtime (TS CLI) | Dev mirror | Not constitutional runtime |
| gitMaat | Partially healthy | Code OK; DB down on audit host |
| End-to-end product loop | Reference only | Demo scripts, not live surfaces |

---

## Guard v2 MVP — Specific Audit

**Built:**

- `tehuti-guard/guard/tehuti_guard/covenant_adapter.py`
- `tehuti_guard/rules.py` — `evaluate_compiler_with_rules()`
- `tehuti_guard/server.py` — `POST /compile-decision`
- `tehuti_guard/memory_sink.py` — governance logging
- `tehuti-guard/guard/tests/test_compile_decision.py`
- `scripts/maat_runtime_guard_v2_demo.py`

**Limitations:**

- Depends on `/mnt/ai_models/maatbench` hard path
- Not portable outside lab layout
- npm MCP Guard not integrated
- Production surfaces not wired

**Verdict:** Valid vertical slice. Not yet a product.

---

## Fable 5 Smoke — Constitutional Evidence

From `Tehuti-Dataset/training/fable5_desktop_capture/fable5_smoke_score_report.json`:

| Metric | Result |
|--------|--------|
| Raw integrated validity | 0.0% |
| Compiler-enforced integrated validity | 93.75% |
| Raw unsafe allow | 0.0% |
| Average repairs per case | 1.625 |
| Human review required | 7 / 16 |

Supports dissertation thesis at smoke scale. Not full cross-model evaluation.

---

## Top 10 Risks (Ranked)

1. Unpushed Guard v2 MVP
2. MaatBench canonical split (ecosystem copy lacks compiler modules)
3. Maat-runtime naming collision
4. Tehuti-Dataset unversioned
5. gitMaat DB down on audit host
6. Guard v2 lab-path coupling
7. npm MCP Guard not on v2 doctrine
8. Cross-model eval incomplete
9. Legacy parallel trees
10. Demo ≠ production

---

## Recommended Actions

### P0 — Truth and closure

1. Commit and push Guard v2 MVP in `maat-ecosystem` (Guard-related files only)
2. Declare one canonical MaatBench home
3. Clarify in docs: "MAAT Runtime (constitutional compiler)" vs "Maat-runtime (TS CLI fork)"
4. Restore PostgreSQL / gitMaat on coordination-primary host

### P1 — Product proof

5. Wire one real surface to `POST /compile-decision`
6. Package MaatBench dependency for Guard v2 portability
7. Update cross-model readiness review with Fable 5 smoke results

### P2 — Research continuity (after above)

8. Run full cross-model eval only if readiness gates pass and user greenlights
9. Continue dissertation writing from frozen artifacts — no new training
10. Run initiation user test per `MAAT-AUDIT-ACTION-PLAN.md`

---

## Locked State (Do Not Violate)

- No Pack L
- No Pass 7B
- No DPO
- No broad SFT
- No model promotion from compiler-enforced success alone
- System governance: eligible for review
- Model promotion: false

---

## Related

- [`MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md)
- [`MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md`](MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md)
- [`TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md`](TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md)
- [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)
- `Tehuti-Dataset/training/MAATBENCH_032_PHASE_FREEZE.json`
- `Maat-runtime/docs/MAATBENCH-CONSTITUTIONAL-RUNTIME.md`
