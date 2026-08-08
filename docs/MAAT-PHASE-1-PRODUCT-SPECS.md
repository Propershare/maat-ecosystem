# MAAT Phase 1 — Product specs (Teach · Govern · Verify)

**Status:** Active build plan (2026-07-13)  
**Supersedes:** ad-hoc product brainstorming only — does not replace [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) (repo roles) or [`REPLIT-MAAT-SITE-BRIEF.md`](REPLIT-MAAT-SITE-BRIEF.md) (public site scope).

**Thesis:** The foundation exists. Phase 1 ships **three thin products** on live lab APIs — not a new marketing site.

```
BlackLabRats Classroom  →  teaches
Tehuti Guard              →  governs
MaatBench                 →  verifies
```

Hermes / OpenClaw distributes later. Ka Education Backend coordinates institution data.

---

## Phase 1 scope (build now)

| # | Product | MVP | Repo / surface |
|---|---------|-----|----------------|
| 1 | **MaatBench interactive report** | Run declared suites → tier-labeled score → export JSON + PDF/HTML | `maat-ecosystem/maatbench/` + BFF route |
| 2 | **Tehuti Guard policy simulator** | Natural-language scenario → structured action → `/decision` + `/explain` | `tehuti-guard/guard/` + site or BFF |
| 3 | **BlackLabRats lesson builder** | Form → draft lesson pack → Guard review queue → no auto-publish | `ka-education-backend/` + BLR content scripts |

**Explicitly not Phase 1:** provenance graph, roundtable classroom, certification badges, public “submit any API” bench, operator console (Phase 2).

---

## Product 1 — MaatBench interactive report

### User story

> As an operator or visitor, I run a **declared verification tier** against the lab (or a named profile), see per-category pass/fail with evidence, and download a signed report.

### MVP inputs

| Field | Example |
|-------|---------|
| Target profile | `lab_spine` \| `guard_only` \| `memory_only` \| `full_minus_behavior` |
| Machine id | `staydangerous` |
| Optional git SHA | auto from env |

### MVP outputs

| Artifact | Format |
|----------|--------|
| MAAT Score | `72/100` with **tier label** (never naked “100%”) |
| Category table | 7 guarantee columns + gateway/lab_spine when run |
| Evidence | Link to MaatBench Evidence Record fields |
| Export | JSON (existing) + HTML/PDF report |

### What already exists

| Piece | Path |
|-------|------|
| Runners + contracts | `maat-ecosystem/maatbench/runners/`, `contracts/` |
| Scorer | `maat-ecosystem/maatbench/scorers/scorer.py` |
| Text + JSON reporter | `maat-ecosystem/maatbench/reports/reporter.py` |
| Evidence record schema | `maat-ecosystem/maatbench/evidence/SCHEMA.md`, `evidence/record.py` |
| Published snapshot (site) | `docs/.../appendices/maatbench-report-2026-06-20.json` |
| North-star API spec | `docs/MAATBENCH-v2.md` (`POST /run`, `GET /suites`) |
| Lab bench workflow | `docs/LAB-BENCH-WORKFLOW.md`, `scripts/run-lab-bench-workflow.sh` |

### What to build (MVP gap)

1. **BFF endpoint** (Express on `:3008` in `ka-education` repo, or `ka-education-backend`):
   - `POST /api/maatbench/run` → spawn `python3 -m maatbench.run --category …` with timeout + tier manifest
   - `GET /api/maatbench/report/:run_id` → JSON + HTML
2. **Tier manifest** JSON — which categories count toward displayed score (per `maat-ecosystem/maatbench/README.md` public labeling rule).
3. **Report template** — extend `reporter.py` with HTML export; map to Evidence Record (`report_hash`, `git_commit`, `limitations`).
4. **UI panel** — replace static `bench-snapshot.json` panel with “Run lab tier” + “View last report” (snapshot remains as fallback).

### Non-goals (v1)

- Third-party “submit your API URL” fuzzing
- Paid certification badges
- `behavior_balance` on public surface without live model disclosure

### Success criteria

- Every public score shows **tier + ISO date + git SHA**
- Report matches CLI output byte-for-byte on category counts
- Failed category shows test name + remediation hint

---

## Product 2 — Tehuti Guard policy simulator

### User story

> As a teacher, admin, or builder, I describe a proposed AI action in plain language. The system shows **Allow / Review / Quarantine / Escalate / Deny**, which rules fired, and what evidence or approval is missing.

### Example

**Input:** “An education agent wants to email a student’s progress report to an outside organization.”

**Output:**

```json
{
  "decision": "deny",
  "severity": "high",
  "matched_rules": ["student_data_export_requires_authorization"],
  "reason": "…",
  "explanation_id": "sha256:…",
  "policy_version": "1"
}
```

Plus human-readable **explain** block from `POST /explain`.

### What already exists

| Piece | Path |
|-------|------|
| Decision API | `tehuti-guard/guard/` — `:8013` |
| Endpoints | `POST /decision`, `POST /explain`, `POST /compile-decision`, `GET /rules` |
| Wire contract | `docs/TEHUTI-GUARD-WIRE-CONTRACT.md` |
| Action kinds | `read`, `write`, `execute`, `deploy`, `delete`, `memory_write`, … |
| E2E demo | `scripts/guard_adapter_e2e_demo.py` |
| Ka backend Guard hook | `ka-education-backend/src/guards/constitution.ts` (constitution gate, not scenario UI) |

### What to build (MVP gap)

1. **Scenario → envelope mapper** (BFF or small Python module):
   - User text + optional fields (actor role, risk, resource class)
   - LLM or rule-based template fills `machine_id`, `actor`, `action` per wire contract
2. **Simulator UI** — form + result card:
   - Decision badge (color per `docs/REPLIT-MAAT-SITE-BRIEF.md` palette)
   - `matched_rules` list from `GET /rules` descriptions
   - “Why blocked” from `/explain`
3. **Preset scenarios** — education, memory write, deploy, canon read (three-ring)
4. **Optional:** log to `maat_governance_events` when `TEHUTI_GUARD_MEMORY=1`

### API flow

```
Browser → BFF POST /api/guard/simulate
       → map scenario to envelope
       → POST http://127.0.0.1:8013/decision
       → POST http://127.0.0.1:8013/explain (if explain-only fields needed)
       → return unified JSON to UI
```

### Non-goals (v1)

- Visual policy-builder (Product 4 in roadmap)
- Policy editing in UI

### Success criteria

- Non-technical user gets answer in &lt; 3 clicks
- Same envelope works from CLI demo and UI
- Sentinel down → `review` with clear “fail-safe” copy (not shown as bug)

---

## Product 3 — BlackLabRats lesson builder

### User story

> As a teacher or researcher, I enter topic, level, objectives, and **required sources**. The system generates a **draft** lesson pack (outline, discussion questions, source list). Claims are flagged for review. Nothing publishes without approval.

### MVP form fields

| Field | Required |
|-------|----------|
| Lesson topic | yes |
| Student level | yes |
| Learning objectives | yes |
| Required sources | yes (URLs or corpus ids) |
| Key terms | optional |
| Assessment type | optional |

### MVP outputs (draft only)

- Lesson outline (markdown)
- Instructor notes
- Discussion questions
- Source list with confidence labels
- Optional: link to BLR media slot (PiP reel placeholder — pipeline exists in ComfyUI scripts)

### What already exists

| Piece | Path |
|-------|------|
| Ka education API | `ka-education-backend/` — curriculum, cohorts, faculty, progression |
| UKMT pipeline canon | `ka-education-backend/docs/canon/UKMT_EDUCATION_PIPELINE.md` |
| Constitution gate | `ka-education-backend/src/guards/constitution.ts` |
| Prisma models | `ka-education-backend/prisma/schema.prisma` |
| BLR video PiP pipeline | `comfyui/scripts/blr_pip_lib.py`, `build_blr_pip_education_reel.py` |
| BLR character sheet | `comfyui/input/blacklabrats_blr_mouse_stylesheet.png` |
| Public site brief (no UKMT portal on maatecosystem.com) | `docs/MAAT-ECOSYSTEM-SITE-DIRECTION.md` |

### What to build (MVP gap)

1. **`LessonDraft` model** (Prisma) — topic, objectives, sources, status: `draft` \| `guard_review` \| `approved` \| `published`
2. **`POST /api/classroom/lessons/draft`** — create draft (no publish)
3. **Generator step** — LLM via Tehuti Core `:8014` or configured provider; output structured JSON
4. **Claim tagging** — each factual sentence → `{claim, source_id?, confidence, needs_review}`
5. **Guard pass** — high-risk patterns (export student data, unverified history as fact) → `POST /decision` with `memory_write` / education kinds
6. **gitMaat log** — `log_decision` / `log_change` for draft creation and approval
7. **UI** — simple wizard on site or admin route (BlackLabRats section, not main maatecosystem hero)

### Governed publish rule (Maat-aligned)

```
Form → Draft → Auto claim scan → Guard flags → Human approves → Publish
```

No step skips Guard on `published` transition.

### Non-goals (v1)

- AI roundtable (Product 8)
- Kmt math interactive lab (Product 10)
- Auto-post to YouTube

### Success criteria

- Every published lesson has approver id + timestamp in DB
- Unsourced claims stay marked `needs_review` in export
- One end-to-end demo lesson (Sankofa / Maat theme) ships with optional PiP clip

---

## Implementation order (8–10 weeks)

| Week | Deliverable |
|------|-------------|
| 1–2 | Guard simulator BFF + UI presets (fastest wow) |
| 2–4 | MaatBench BFF run + HTML report + tier manifest |
| 4–6 | Lesson draft API + Prisma + Guard on publish |
| 6–8 | Lesson builder UI + one canonical demo lesson |
| 8+ | Hermes routing rules (Classroom vs Guard vs Bench) — Phase 2 |

---

## Repo map (where code goes)

| Layer | Repo / path | Phase 1 role |
|-------|-------------|--------------|
| Public UI | `github.com/Propershare/ka-education` (Vite, `:3008`) | Simulator + Bench panel + Lesson wizard routes |
| BFF / API | `ka-education-backend/` | `/api/guard/*`, `/api/maatbench/*`, `/api/classroom/lessons/*` |
| Policy engine | `tehuti-guard/guard/` | Unchanged — HTTP `:8013` |
| Verification | `maat-ecosystem/maatbench/` | CLI today; thin HTTP wrapper in BFF |
| Memory | `maatlangchain/maat_memory/` | Audit logs for lesson + bench runs |
| BLR media | `comfyui/scripts/blr_pip_*.py` | Optional reel per lesson topic |
| Site brief | `docs/REPLIT-MAAT-SITE-BRIEF.md` | Product-only public surface |

---

## Phase 2 backlog (from 18-product map)

| Priority | Product |
|----------|---------|
| High | Memory explorer (read-only gitMaat UI) |
| High | Operator console (Guard decisions, pending reviews) |
| Medium | Policy builder (no-code rules → Guard catalog) |
| Medium | Hermes scholar routing |
| Research | Provenance graph, chronology explorer, claim checker, roundtable |

---

## Canonical tagline (product suite)

**Teach the knowledge. Govern the action. Verify the system.**

- **BlackLabRats Classroom** teaches  
- **Tehuti Guard + Maat Memory** govern  
- **MaatBench** verifies  
- **Hermes Gateway** distributes (Phase 2)  
- **Ka Education Backend** coordinates the institution  

---

## See also

- [`MAATBENCH-v2.md`](MAATBENCH-v2.md) — sequencing law before public bench scale
- [`MAAT-ECOSYSTEM-SITE-DIRECTION.md`](MAAT-ECOSYSTEM-SITE-DIRECTION.md) — maatecosystem.com vs UKMT lineage
- [`TEHUTI-GUARD-WIRE-CONTRACT.md`](TEHUTI-GUARD-WIRE-CONTRACT.md) — simulator envelope shape
- [`comfyui/scripts/blr_pip_lib.py`](../comfyui/scripts/blr_pip_lib.py) — mastered BLR transparent PiP media pipeline
