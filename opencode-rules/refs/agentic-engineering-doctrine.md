# Agentic Engineering Doctrine — Tehuti Lab Synthesis

**Slug:** `refs/agentic-engineering-doctrine-2026-08-08`
**Author:** Imhotep / Tehuti Lab
**Type:** Synthesis + applied doctrine (internal canon)
**Audience:** `every_lab_agent`
**Provenance:** Synthesized from external practitioner experience, validated against Tehuti Lab constitutional pillars (Truth · Balance · Order · Justice · Reciprocity · Accountability · Self-Reflection). Ma'at audit score and remediation notes: see sibling artifact `refs/maat-audit-agentic-engineering-doctrine-2026-08-08`.
**Supersedes:** none
**Last touched:** 2026-08-08

> **Note on provenance.** This doctrine is a Tehuti Lab synthesis derived from
> field reports about agentic engineering failures. It is **canonized for the lab**,
> not attributed to any external author. Where the lab's empirical experience
> diverges from the synthesized framework, the lab view wins.

---

## 0. Doctrine statement

**The bottleneck of an agentic software factory is review, not build.**
Optimizing any non-review stage of the factory — agent orchestration, context
windows, multi-agent routing, prompt engineering, model selection — does not
improve total throughput until review is solved. Discipline is the precondition
for scale; hype is not.

## 1. The factory loop (current state)

Inputs → Triage → Agent build → Agent self-review → **Human review (the bottleneck)**
→ Merge → Deploy → Monitor → Feedback → Inputs.

Two substitutions versus the pre-agentic loop:

- **Build:** person-days → minutes/hours.
- **Review:** unchanged — still hours/days, still human.

Implications:

- Do not staff build like a scarce resource. Staff **review** like one.
- A pull request wakes you up at 3 AM, not an alert.
- Incidents, complaints, feature requests route **into** the agent queue,
  not around it.

## 2. The lights-off failure mode (doctrine: forbidden)

A fully autonomous factory — agents build everything, agents review plans,
humans review only the to-do list — is **forbidden doctrine** in this lab.

Reason: when review is delegated entirely to models, debugging becomes
exponentially harder because nobody understands the logic. The cost function
of bad architecture is measured in weeks and months; model benchmarks reward
"tests pass" in seconds. There is no oracle for maintainability in the
training loop.

**The lab position:** humans own the logic. Agents own the typing. The split
is by design and is enforced by:

- UPL Guard (legal organ) — deterministic gate, not probabilistic review.
- Ma'at Audit scoring — deterministic constitutional check on every
  agent-generated artifact.
- The order-of-authority in `~/.opencode-rules/00-lab-doctrine.md` —
  gitMaat → TehutiGuard → MaatBench → project AGENTS.md.

## 3. The 4-stage program design system (doctrine: required for new systems)

Every new agentic system in this lab must pass through these four stages
**before** agents are allowed to write implementation code. Stages are
sequential; skipping Stage 3 is the canonical failure pattern.

### Stage 1 — Product (no code)

- What user problem are we solving? How do we measure success?
- Write the user-facing description **first**. HTML mockup if helpful.
- If success is not measurable, the system is not ready to build.

### Stage 2 — System architecture

- Endpoints, services, tables, query outlines.
- High-level design that a reviewer would want to see **before** any code.
- This is the "PR description" stage.

### Stage 3 — Program design (the stage most people skip)

- File placement. Call stack. Types and method signatures.
- **No implementation yet.** Only shapes.
- Define what the tests will look like.
- Cross-machine variant: when the system spans Tailscale nodes, the
  slice is the smallest one that crosses the deployment boundary —
  not the smallest one that runs on a single box.

Stage 3 is where lab intuition earns its keep. Tokens are cheap here;
expensive decisions are made here. Skip it and you pay ten times
later.

### Stage 4 — Vertical slices

- Build end-to-end first with stubs and mocks.
- Test at each step before extending.
- Add logic, then business cases, then error handling — in that order.
- Cheaper to resteer early when the code is small.

**Why we templated Stages 1–3:** the lab runs multiple agentic systems. After
the first three, Stages 1–3 should be templated per system class
(legal, trading, RAG, etc.), not re-invented per feature. The template is the
program-design artifact; the implementation is downstream.

## 4. Context engineering (doctrine: own your window)

Three rules for every context the lab puts in front of a model:

1. **No wrong information.** Anything incorrect degrades everything.
2. **No missing information.** The model cannot use what it does not have.
3. **As small as possible** within (1) and (2).

Delivery priority for context:

- **Files in the repo / on the filesystem** (deterministic, model-native).
- **Hooks** that inject deterministically at session start (cheap CPU, not inference).
- **MCP tools** for live data.
- **System-prompt instructions about how to fetch** (last resort — burns
  attention tokens while the model is reasoning).

The lab's `~/.opencode-rules/` directory is the canonical example of rule
(1) — doctrine lives in files, loaded deterministically by the opencode
`instructions:` field, not as ad-hoc system-prompt text.

## 5. The dumb zone (doctrine: monitor empirically)

At roughly 50–60% of context window capacity, model performance degrades.
The exact threshold is **model-specific**; the lab does not treat it as
folklore. When a new model joins the fleet, run a context-load sweep
(10k / 50k / 100k / 150k) on a representative task and **measure** where
quality collapses. Record the result in `~/.opencode-rules/refs/` and link
from the model card.

Remediation:

- Compact into a structured doc, start a fresh session.
- Do not "push the zone" hoping the next model handles it.

## 6. Bottleneck discipline (doctrine: hold your nose)

From the lab order-of-authority (`~/.opencode-rules/00-lab-doctrine.md`):
gitMaat → TehutiGuard → MaatBench → project AGENTS.md. **Optimize in that
order.** Optimizing a non-bottleneck step does not improve throughput; it
adds WIP pileups.

Forbidden patterns (these are signals you are optimizing a non-bottleneck):

- Building new agent orchestration layers when review is the actual bottleneck.
- Adding MCPs when UPL Guard already gates the surface.
- Designing new audit dimensions when TehutiGuard already covers them.
- "Token-maxing" — running the largest model on the smallest task.

The lab is a research lab, not a startup chasing product-market fit. The
success criterion is **time-to-evidence**, not time-to-feature. Build the
smallest thing that lets you record the receipt.

## 7. Concrete applications (lab doctrine, not examples)

> **Provenance note:** Each subsection below names which claims are
> **lab-confirmed** (have receipts in `~/.opencode-rules/` or `maat_memory`)
> versus **synthesized** (derived from the framework but not yet tested in
> the lab). Synthesized claims are not weakened — they are flagged so the
> operator can prioritize them for falsification.

### 7.1 Legal organ (MAAT, Jarvis mode)

| Claim | Status |
|-------|--------|
| UPL Guard is a deterministic gate; new MCPs weaken the surface | **Lab-confirmed** — UPL Guard is documented in `~/.n8n/maat-ecosystem/voice/governance_audit.py` |
| Bottleneck has shifted from drafting to attorney review | **Lab-confirmed** — observed across legal matters handled by the system |
| Optimize attorney review tooling before drafting | **Synthesized** — derived from the bottleneck doctrine; not yet measured end-to-end |

Doctrine:

- Stage 3 templates already exist: UPL Guard schema, Ma'at Audit
  dimensions, matter data model. **Do not add new MCPs to the legal surface.**
  Each new MCP is a new context-engineering surface and a new path for
  the failure modes in §2. The right direction is fewer surfaces, deeper
  governance.
- The bottleneck has already shifted to **attorney review throughput**.
  Optimizing drafting speed is optimizing a non-bottleneck. Optimize the
  attorney review tool (highlighting, citation pinning, comment threading)
  before optimizing drafting.

### 7.2 Trading organ (Alpaca options)

| Claim | Status |
|-------|--------|
| 533-config exhaustive search was the correct application of Stage 1 | **Lab-confirmed** — search artifact is in `maat_memory`; the null result was accepted, no further configs added |
| Empty catch blocks in risk code will pass backtests and fail in production | **Synthesized** — derived from the slop pattern in §3 + financial-engineering literature; falsifiable via grep against the trading repo |

Doctrine:

- The exhaustive 533-config search was a Stage-1 measurable-output
  application: defined the metric, searched exhaustively, accepted the
  null result. **That is the correct behavior.** Do not let anyone
  "improve" it by adding more configs; the bottleneck after a null
  result is the signal hypothesis, not the search.
- Stage 3 for risk management: every code path that touches order
  execution must have a deterministic test that survives backtest
  conditions. No empty catch blocks. No `as any`. No `try { ... } catch { return undefined }`.
  These patterns will pass backtests and detonate in a real drawdown.

### 7.3 Information organ (RAG build, current focus)

| Claim | Status |
|-------|--------|
| Run Stage 3 before any agent writes ingestion code | **Lab-confirmed** — current repo state shows no `doc/ADR/` for the RAG pipeline |
| Cross-machine slice must include OCR + Postgres + Ollama + retrieval | **Synthesized** — derived from the lab's actual Tailscale + 3-machine topology in `40-ssh-topology.md` |

Doctrine:

- **Run Stage 3 now**, before any agent writes ingestion code.
  Define the Postgres schema for `ContentPiece`, `Chunk`, `SearchResult`.
  Define the Ollama call signature (model, chunk size, overlap).
  Define what "retrievable" means (test query, expected recall@10).
- Stage 4: one book chapter → OCR → clean text → stored → retrievable
  via semantic search → tested. **Then** add metadata extraction,
  classification, multi-category routing.
- Cross-machine variant: the slice must include OCR service + Postgres
  + Ollama + retrieval, because those are the deployment boundary.
  Don't build "OCR on one machine" as a slice — that's a horizontal
  phase, not a vertical slice.

## 8. What to grep for (signal of the failure mode)

Run these greps against any agent-generated code in the lab. Hits are not
proof of bug; they are proof that the code was written without program
design:

```bash
# Empty / silent catch
grep -rnE "except\s*:\s*$|catch\s*\([^)]*\)\s*\{\s*\}|catch\s*\{\s*\}" .

# Defeated type system
grep -rnE "as\s+unknown\s+as\s+any|:\s*any\b|\bany\[\]" .

# Retry-busy patterns that hide errors
grep -rnE "for\s+.*\bin\s+range\(\s*[0-9]+\s*\):\s*$" .

# Stage-3 evidence: are types/signatures documented *before* implementation?
ls doc/ADR/ doc/types/ 2>/dev/null || echo "no ADR/types dir — Stage 3 was skipped"
```

If the last grep returns nothing, the system was built without program
design. That is a truth failure (§9) regardless of whether tests pass.

## 9. Ma'at constitutional check (summary)

This doctrine is scored against the 7-pillar rubric in
`refs/maat-scoring-canon-2026-08-08` (v1). Scores are not maintained in
this file; they live in the audit artifact and are updated by the §14
re-audit cadence. Verdict progression:

| Verdict | Condition |
|---------|-----------|
| **CANON** | total ≥ 16/21, Truth ≥ 2, Self-Reflection ≥ 2 (current) |
| **ADOPT** | total ≥ 12/21, no pillar = 0 |
| **CANON_SUSPENDED** | re-audit cadence missed or any pillar regressed ≥ 1 score |

Full Ma'at audit artifact (with rubric, remediation history, and change log):
`refs/maat-audit-agentic-engineering-doctrine-2026-08-08`.

---

## 10. What is forbidden

- Going lights-off (no human code review).
- Skipping Stage 3 because "the agent can figure it out."
- Adding review-stage optimization (multi-agent routing, fancier prompts)
  before fixing the actual bottleneck.
- Calling a system "production" without a Stage-3 artifact in `doc/ADR/`
  or equivalent.
- Citing benchmark pass rates as evidence of maintainability.

## 11. What is required

- A Stage-3 artifact (`doc/ADR/` or `doc/types/`) for every new system.
- A vertical slice that crosses the deployment boundary, end-to-end,
  tested before further extension.
- The §8 greps run on every PR, with hits either remediated or explicitly
  justified in the PR description.
- Periodic context-load sweeps for every model in the fleet, results
  recorded in `refs/`.

### 11.5 Operator obligations (Justice)

Doctrine protects humans-on-the-loop only if humans actually do their
part. The operator (Imhotep, or whoever holds the operator seat at the
time) is obligated to:

- **Read the §8 grep report** for each active repo at least once per week.
  Hits without PR-description justification must be remediated or
  explicitly archived with rationale.
- **Run a context-load sweep** for every new model before it joins the
  fleet. Record results in `refs/`.
- **Audit active doctrines** against the Ma'at scoring canon at least
  once per quarter. Findings are appended to the doctrine's audit artifact
  (see §14).
- **Process dissent artifacts** (see §13) within 7 days of submission.
- **Maintain the order of authority** from `00-lab-doctrine.md`. If a
  decision requires breaking the order, the operator must explicitly
  acknowledge the break in `maat_memory` and re-establish the order
  within the same session.

Failure to meet these obligations is itself a Justice failure — the
doctrine's protections are conditional on the operator doing their part.

## 12. Related artifacts

- `refs/horthy-2026-08-08` — original synthesis source (kept for provenance;
  not lab canon)
- `refs/maat-audit-agentic-engineering-doctrine-2026-08-08` — full audit
  and remediation log
- `refs/maat-scoring-canon-2026-08-08` — the rubric this doctrine is
  audited against
- `~/.opencode-rules/00-lab-doctrine.md` — order of authority
- `~/.opencode-rules/40-ssh-topology.md` — cross-machine lab topology

## 13. Dissent channel (Reciprocity)

Any agent or operator who disagrees with this doctrine may submit a
**dissent artifact** to `maat_memory`:

```python
from maat_memory import MaatMemory
m = MaatMemory()
m.log_decision(
    agent='<agent_or_operator>',
    context='Dissent: refs/agentic-engineering-doctrine-2026-08-08 / §<N>',
    decision_made='Dissent filed; doctrine §<N> contradicted by lab evidence',
    rationale='<specific lab evidence or reasoned argument>',
    origin='agent_authored',
)
```

**A dissent artifact triggers a re-audit of the doctrine within 7 days.**
The re-audit may:

- Update the doctrine (§14 procedure),
- Append to the audit artifact with the dissent and the operator's response,
- Or dismiss the dissent with explicit reasoning recorded in the audit.

Dissent without evidence is acknowledged and archived; it does not
automatically invalidate the doctrine. Dissent with evidence is the
canonical mechanism for doctrine evolution.

## 14. Re-audit cadence (Self-Reflection)

This doctrine is re-audited on the **first day of each quarter**
(2026-10-01, 2027-01-01, 2027-04-01, ...). The re-audit:

1. Re-runs the 7-pillar scoring rubric (`refs/maat-scoring-canon-2026-08-08` v1).
2. Updates scores in place in the audit artifact.
3. Appends a `## Change history` entry to the audit with the date and deltas.
4. If any pillar regresses by ≥ 1 score, the doctrine's `CANON` verdict
   is suspended until the regression is remediated. The doctrine remains
   visible but flagged as `CANON_SUSPENDED` in the audit artifact title.

Re-audit is the operator's responsibility (see §11.5). If the operator
cannot perform the re-audit by the cadence date, the doctrine is
demoted from `CANON` to `ADOPT` and a `dissenting_audit_due` learning is
logged to `maat_memory`.
