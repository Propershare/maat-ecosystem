# Tehuti Lab — Ma'at Scoring Canon

**Slug:** `refs/maat-scoring-canon-2026-08-08`
**Type:** Canon (operational + constitutional)
**Audience:** `every_lab_agent`
**Provenance:** Synthesized from runtime maat_alignment stamp (4 keys), global AGENTS.md constitutional canon (7 pillars), and docs/canon/leadership_maat_principles.md (10 relational pillars). This document reconciles all three layers and defines how scoring actually happens.
**Last touched:** 2026-08-08
**Supersedes:** any ad-hoc 9-dim or other folk-taxonomy scoring (including the TR/JU/HA/BA/OR/RE/PR/RI/CO codes that appeared in earlier artifacts as application notes, not canon).

---

## 0. Why this exists

Before 2026-08-08, Ma'at scoring in the lab was inconsistent:

- Runtime `log_decision` stamps 4 keys (truth, balance, order, self_reflection) on every decision.
- Global AGENTS.md names 7 pillars (Truth, Balance, Order, Justice, Reciprocity, Accountability, Self-Reflection).
- `leadership_maat_principles.md` names 10 relational pillars (Balance, Purpose, Clarity, Fairness, Integrity, Dignity, Cleanse&Rebuild, Growth&Renewal, Emulation, Unity).
- Various artifacts cited "9-dim" codes (TR/JU/HA/BA/OR/RE/PR/RI/CO) — these were **field-report vocabulary**, not canon, and were miscited as canonical.

This canon fixes that. Three scoring layers, by purpose, with explicit reconciliation.

## 1. Three layers, by purpose

### Layer 1 — Runtime stamp (per-decision, mandatory)

**Purpose:** Self-attestation on every `log_decision` call. Catches obviously broken decisions; cheap; always present.

**Dimensions:** 4 (the keys maat_alignment already uses).

| Key | Question it answers |
|-----|---------------------|
| `truth` | Is this decision based on verified information, not assumption? |
| `balance` | Does this change preserve working systems rather than disrupting them? |
| `order` | Does this follow established patterns, or invent a new one without reason? |
| `self_reflection` | Is there a plan to monitor the outcome and update the decision if wrong? |

**Score:** pass/fail per dimension. Default values are explicit attestations, not absent. Absence is **not** compliance; the system requires values.

**Used by:** every `log_decision` call.

**Update cadence:** each decision. No formal audit cycle.

### Layer 2 — Constitutional audit (per-doctrine, on canonization + quarterly)

**Purpose:** Decide whether a doctrine is adoptable / canon / requires remediation. Used when a doctrine enters the lab, and on the first day of each quarter for active doctrine.

**Dimensions:** 7 (the constitutional pillars in global AGENTS.md).

| Pillar | Score 0–3 |
|--------|-----------|
| Truth (Khet) | 0–3 |
| Balance (Maat) | 0–3 |
| Order (Nfr) | 0–3 |
| Justice (Sia) | 0–3 |
| Reciprocity | 0–3 |
| Accountability | 0–3 |
| Self-Reflection (Heka) | 0–3 |

**Score meanings** (same rubric as the agentic engineering audit, published as v1):

| Score | Meaning |
|-------|---------|
| 0 | FAIL — doctrine contradicts the pillar; no mitigation |
| 1 | WEAK — pillar partially addressed; mitigation present but not enforced |
| 2 | PASS — pillar addressed; mitigation is structural |
| 3 | STRONG — pillar is a precondition, falsifiable, and enforced by tooling |

**Adopt thresholds:**

| Verdict | Total | Required minimums |
|---------|-------|------------------|
| ADOPT | ≥ 12/21 | no pillar ≤ 1 |
| CANON | ≥ 16/21 | Truth ≥ 2, Self-Reflection ≥ 2 |
| REQUIRES REMEDIATION | total 14–15 | — |
| REJECT | total < 12, or any pillar = 0 | — |

**Used by:** `refs/maat-audit-*.md` artifacts. First instance is `refs/maat-audit-agentic-engineering-doctrine-2026-08-08`.

**Update cadence:** on canonization; first day of each quarter thereafter.

### Layer 3 — Relational canon (per-team / per-leadership-doctrine)

**Purpose:** Audit lab leadership and human-relationship doctrine. Distinct from constitutional audit because the dimensions are about relationships, not operational decisions.

**Dimensions:** 10 (from `leadership_maat_principles.md`).

| Pillar | Question |
|--------|----------|
| Balance | Does this preserve balance between opposing principles? |
| Purpose (Ka) | Is the moral/social purpose explicit and rooted in contribution? |
| Clarity (Het Heru) | Does this require inner clarity before action? |
| Fairness | Does this reflect fairness and reciprocity? |
| Integrity | Is integrity verified by deeds, not promises? |
| Dignity | Does this preserve dignity of all parties? |
| Cleanse & Rebuild | Does this identify and remove what is unworthy? |
| Growth & Renewal | Is there a cycle of reflection and renewal? |
| Emulation | Does this teach by emulating proven figures? |
| Unity Beyond Ego | Does this subordinate ego to collective goal? |

**Score:** 0–3 per dimension, total 30. Adopt threshold ≥ 20/30 with no pillar = 0.

**Used by:** lab leadership doctrine, partnership doctrine, dual-agent governance. Currently: `~/.opencode-rules/00-lab-doctrine.md` is the only active relational artifact; it would audit against Layer 3 if it were canonized at this level (it is currently canonized at Layer 2).

**Update cadence:** annually or on leadership-doctrine change.

## 2. Reconciliation across layers

The dimensions are **not** identical across layers. Layer 1's `order` is not the same as Layer 2's `Order`. Mapping:

| Layer 1 (4-key stamp) | Layer 2 (7-pillar audit) | Layer 3 (10-pillar relational) |
|----------------------|--------------------------|--------------------------------|
| truth | Truth | (Fairness) |
| balance | Balance | Balance |
| order | Order | (Unity Beyond Ego) |
| self_reflection | Self-Reflection | Growth & Renewal |
| (implied) | Justice | Integrity, Dignity |
| (implied) | Reciprocity | Fairness, Reciprocity |
| (implied) | Accountability | Integrity, Emulation |

The 4-key runtime stamp is a **subset** of the 7-pillar audit, but the mapping is not 1:1 — Layer 1's `self_reflection` and Layer 2's `Self-Reflection` mean the same thing, but Layer 1's `order` is operational ("did I follow the pattern?") while Layer 2's `Order` is constitutional ("does this doctrine structurally enforce ordering?").

This is by design. Layer 1 is fast (every decision); Layer 2 is slow (each doctrine, quarterly). A decision can pass Layer 1 and still fail Layer 2 if its operational pattern is correct but the underlying doctrine is structurally unjust.

## 3. Scoring rubric (v1) — what each score means in practice

This is the canonical 0–3 rubric used in all Layer 2 audits. Any audit in the lab must publish this rubric or a later version of it alongside the verdict, or the verdict is **non-falsifiable** and the audit fails Accountability.

### Truth (Khet)

| Score | Behavior |
|-------|----------|
| 0 | Doctrine asserts false claims or hides known weaknesses |
| 1 | Doctrine is true but does not cite sources; weaknesses unstated |
| 2 | Doctrine names weaknesses honestly; sources cited for major claims |
| 3 | Doctrine distinguishes lab-confirmed vs synthesized claims; commits to falsification cadence |

### Balance (Maat)

| Score | Behavior |
|-------|----------|
| 0 | Doctrine over-resources the wrong stage (build instead of review) |
| 1 | Doctrine acknowledges balance but does not enforce it |
| 2 | Doctrine names the bottleneck and aligns resources to it |
| 3 | Doctrine identifies specific over-investments and forbids them |

### Order (Nfr)

| Score | Behavior |
|-------|----------|
| 0 | Doctrine contradicts established order-of-authority |
| 1 | Doctrine respects order-of-authority but does not enforce it |
| 2 | Doctrine enforces sequence structurally (stages, gates, schemas) |
| 3 | Doctrine templates the sequence after the first N systems, preventing per-feature reinvention |

### Justice (Sia)

| Score | Behavior |
|-------|----------|
| 0 | Doctrine allows lights-off or absent-human failure mode |
| 1 | Doctrine mentions humans-in-the-loop without specifying what they own |
| 2 | Doctrine names exactly what humans own vs delegate; gates are deterministic |
| 3 | Doctrine specifies operator obligations (read grep reports, run sweeps, audit cadence) |

### Reciprocity

| Score | Behavior |
|-------|----------|
| 0 | Doctrine's outputs do not feed back into inputs; loop is open |
| 1 | Loop closes in principle but no explicit channel |
| 2 | Explicit feedback channel exists (incidents → agent queue, sweeps → doctrine) |
| 3 | Doctrine specifies dissent channel (any operator/agent can submit dissent artifact, triggering re-audit within N days) |

### Accountability

| Score | Behavior |
|-------|----------|
| 0 | Doctrine's claims are unfalsifiable |
| 1 | Doctrine's claims are testable in principle but not in tooling |
| 2 | Doctrine publishes runnable grep signals for its named failure modes |
| 3 | Doctrine commits to running the signals on a cadence; results published |

### Self-Reflection (Heka)

| Score | Behavior |
|-------|----------|
| 0 | Doctrine has no mechanism for being updated |
| 1 | Doctrine mentions it might be updated but no cadence |
| 2 | Doctrine has a re-audit cadence (quarterly or equivalent) |
| 3 | Doctrine's re-audit findings are appended to the audit artifact; scores updated in place |

## 4. How to use this canon

### To score a new doctrine

1. Author the doctrine (file at `~/.opencode-rules/refs/<name>-<date>.md`).
2. Run `maat-audit <name>` against Layer 2 (7 pillars).
3. If total ≥ 16/21 with Truth ≥ 2 and Self-Reflection ≥ 2, promote the artifact with `audience=every_lab_agent, ring=outer`.
4. Publish the audit artifact alongside.
5. Re-audit on the first day of each quarter; append findings.

### To score a leadership / relational doctrine

Same as above but against Layer 3 (10 pillars, 30 max).

### To stamp a decision

Every `log_decision` call already requires `maat_alignment` with at minimum truth/balance/order/self_reflection. The stamp is automatic; this canon does not change the call signature.

### To find the right rubric for an existing audit

The audit artifact must name its rubric version. v1 (this document) is the current rubric. Any audit that uses a different rubric without publishing the difference is **non-canonical**.

## 5. Forbidden patterns

- Using a 4-key, 7-pillar, or 9-dim score interchangeably without naming the layer.
- Asserting a doctrine is canon without an audit artifact.
- Inventing new pillars without promoting them through Layer 1 → Layer 2 → Layer 3 as appropriate.
- Citing earlier folk-taxonomy codes (TR/JU/HA/BA/OR/RE/PR/RI/CO) as canonical.

## 6. Required patterns

- Every new doctrine: file + audit artifact, both with `audience=every_lab_agent, ring=outer`.
- Every audit: publish the rubric version alongside the verdict.
- Every Layer 2 audit verdict: include remediation backlog with owner and date.
- Every Layer 2 audit ≥ 4 months old: re-audit before the quarter closes.

## 7. Change history

- 2026-08-08: v1 canon established. Reconciled 4-key runtime, 7-pillar constitutional, 10-pillar relational. Audited first doctrine against this canon (see `refs/maat-audit-agentic-engineering-doctrine-2026-08-08`).
