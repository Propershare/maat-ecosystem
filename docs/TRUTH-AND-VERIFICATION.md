# Truth and verification — locked alignment

**Purpose:** No ambiguity: where **truth** is produced vs where **MaatBench** sits.

---

## 1. Clean separation (non-negotiable)

| Layer | Source |
|--------|--------|
| **Ground truth** | `guard_cases/` + **human judgment** + **disagreement analysis** |
| **Verification / repeatability** | MaatBench (and scripts) — **does not create truth** |

**MaatBench** verifies, repeats, and measures **against** labeled truth. It is a **verification organ**, not a source of knowledge.

---

## 2. Pipeline (final form)

### Phase 1 — Truth construction

- Create `guard_cases/`, label decisions, run [first-batch checklist](../guard_cases/README.md), refine schema when reality breaks it.

**Output:** trusted labeled dataset.

### Phase 2 — Evaluation (local or scripted)

- Run classifier (Gemma or other) → compare to labels → measure accuracy, false allows/denies, escalation quality.

**Output:** performance signal.

### Phase 3 — MaatBench integration

- `contract_integrity` (schema validation), then repeatable suites, logged results, regression tracking.

**Output:** institutionalized verification.

### Phase 4 — Defensible claim

You can say: the system is **governed**, **evaluated**, and **monitored** under a **repeatable** verification framework — *after* Phases 1–2 exist.

---

## 3. Principle (reuse everywhere)

- **Tehuti Sentinel** → defines **judgment** (office + classifier role).
- **Guard cases** → define **truth** (labels + evidence).
- **MaatBench** → verifies **consistency under repetition**.

---

## 4. What a rigorous reviewer asks

| Question | Answer |
|----------|--------|
| Where does ground truth come from? | `guard_cases/` + review |
| How do you know it works? | Eval metrics |
| Can you reproduce results? | MaatBench and/or scripts |
| What happens when it fails? | Disagreement log + iteration |

---

## 5. When MaatBench matters most

- **Now:** optional but useful for **schema / contract** checks.
- **After publish / external scrutiny:** **repeatability** and **regression** become critical — MaatBench (or equivalent CI) is the **public proof engine**.

---

## 6. Current stage (honest)

| Item | Status |
|------|--------|
| Architecture, schema, naming | Done |
| Data (`guard_cases`) | Starting |
| Evals | Not yet |
| MaatBench integration beyond contracts | Future |

**Next move:** first messy batch + checklist + document disagreements + simple eval (even before full MaatBench). **Not** bench expansion alone, training, or wide publication first.

---

## 7. Ma’at mapping (one line each)

| Principle | Here |
|-----------|------|
| **Truth** | Labeled guard cases |
| **Order** | Schema + structured review |
| **Balance** | Conditional vs escalate discipline |
| **Justice** | Lineage / elder review when ready |
| **Accountability** | Eval metrics + logs **(+ MaatBench for repeatability)** |
| **Reciprocity** | Iteration from failure |

**MaatBench sits under accountability and verification — not under truth.**

---

## Canonical line (frozen)

Do not weaken or over-complicate this:

> **You do not get truth through MaatBench.** You get it through **cases + review + eval**; MaatBench **proves it repeatedly**.

---

## Dissertation (methodology — one sentence)

This work distinguishes **truth construction** (human-labeled constitutional cases), **evaluation** (model alignment to that ground truth), and **verification** (repeatable checks via a benchmark framework)—i.e. epistemology, methodology, and infrastructure are not conflated.

---

## Related

- [`guard_cases/README.md`](../guard_cases/README.md) — checklist  
- [`docs/TEHUTI-SENTINEL-JUDGMENTS.md`](TEHUTI-SENTINEL-JUDGMENTS.md) — Sentinel office + schema  
- [`docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) — Sentinel vs Guard adapters (operational boundary)  
- [`docs/SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md) — operator connection map  
- [`docs/ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) — wire vocabulary + HTTP tables  
- [`docs/FIRST-RUN.md`](FIRST-RUN.md) — bootstrap Guard + Sentinel  
- [`docs/MAATBENCH-v2.md`](MAATBENCH-v2.md) — verification organ  

---

*Locked: evidence first, then verification machinery; MaatBench proves consistency, not wisdom.*
