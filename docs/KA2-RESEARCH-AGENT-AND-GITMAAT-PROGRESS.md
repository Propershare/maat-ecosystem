# KA2 research agent + ecosystem progress (architecture note)

**Purpose:** One place that says **where** a KA2-grounded research capability lives, **how** it uses web/codebase/local models, **how** we track goals **without** a second task product (e.g. self-hosted Paperclip), and **what** to borrow from Paperclip-style discipline.

**Audience:** Builders wiring OpenClaw, MaatLangChain, gitMaat, and UKMT scholarship.

---

## 1. Layers (nothing new required in a separate repo)

| Layer | Role | Anchors in this workspace |
|--------|------|---------------------------|
| **Method** | KA2 workflow, dialectical engine, Maat scorecard, forbidden patterns | [`data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md), [`ka2_agent_config.json`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_config.json) |
| **Triad** | Scout finds → Analyst decides → Archivist persists | [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md) — PhD-style work = **Analyst** judgment + **Archivist** `maat.archivist_record.v1` JSON with `sources[]` |
| **Execution** | Long-running agent loop, channels, cron | **OpenClaw** (`openclaw/`) gateway + workspace; local models via your existing provider config |
| **Tools** | Web + repo + optional browser | **MCP** organs (discovery **8010**, Tehuti Core **8014**, memory **8022**, filesystem per manifest); Tehuti Guard on high-risk writes (**8013**) |
| **Scholarship store** | UKMT/RBG text vs canon | [`docs/TEHUTI-KNOWLEDGE-RAG-MAAT-AUDIT.md`](TEHUTI-KNOWLEDGE-RAG-MAAT-AUDIT.md) |

**Named profile (to implement in config):** e.g. `ka2_research` — system prompt = KA2 header + constraints from `ka2_agent_system_prompt.md`; tool allowlist = web fetch/search + codebase + memory + whatever your gateway exposes.

### OpenClaw preset (implemented in-repo)

| Artifact | Path |
|----------|------|
| Workspace (KA2 `SOUL`, lab `AGENTS`, `lab/` → repo root) | [`openclaw/presets/ka2-research-workspace/`](../openclaw/presets/ka2-research-workspace/) |
| `agents.list[]` fragment (JSON5) | [`openclaw/presets/ka2-research/openclaw.agents.ka2-research.json5`](../openclaw/presets/ka2-research/openclaw.agents.ka2-research.json5) |
| Merge instructions | [`openclaw/presets/ka2-research/README.md`](../openclaw/presets/ka2-research/README.md) |

Merge the fragment into `~/.openclaw/openclaw.json`, set **`model`** to your Ollama ids, **route** a channel to agent id **`ka2-research`**, restart the gateway. File tools read the monorepo under **`lab/`** inside that workspace.

---

## 2. What the research agent does (capability contract)

1. **Study codebase** — cite paths and line ranges; prefer Scout-style pointers over prose-only claims.
2. **Study theories / web** — same; URLs in `sources`.
3. **Test with local models** — bounded runs (scripts, maatbench, or agent tool); record **model id**, **prompt hash or summary**, **result** in Archivist payload or gitMaat `log_learning`.
4. **Document** — long-form: Markdown under a agreed folder (e.g. `docs/research/` or `memory/` by policy) **or** structured JSON first + optional essay; always **KA2 output sections** (header, mode of appropriation, dialectical findings, Maat scorecard) when the task is research-grade.

---

## 3. Progress and goals (single source of truth)

**Authoritative task and coordination store:** **gitMaat** (`maatlangchain/maat_memory/`) — `get_tasks`, `log_task`, `log_decision`, `log_learning`, `log_change` as in `.cursorrules` / [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md).

**Human-readable goals:** [`docs/MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md), connectivity freeze, product map — refreshed on a **cadence** (weekly human pass or OpenClaw cron) that **reads gitMaat + these docs** and writes **one** short progress artifact (markdown or Archivist JSON row): *goal → status → evidence → next step*.

**Rule:** Do not maintain a parallel issue tracker in Git unless it **mirrors** gitMaat or is explicitly disposable; avoid two truths.

---

## 4. Paperclip-style discipline without Paperclip the product

[Paperclip](https://github.com/paperclip-ai) (see Cursor skill `paperclip`) provides **heartbeats**, **inbox**, **checkout**, **blocked + comments**, **run IDs** on mutations.

**Map into Maat:**

| Paperclip | Maat / lab |
|-----------|------------|
| Heartbeat / wake | OpenClaw **cron** or **heartbeat** job that queries gitMaat |
| Inbox | `get_tasks(..., status="pending|in_progress")` |
| Checkout / ownership | Task fields: agent id, status, updated_at; convention: only one `in_progress` owner per task |
| Done / blocked | `log_task` / `log_decision` with explicit rationale |
| Trace | Session / correlation ids + Archivist `sources` |

Use Paperclip **as a reference for process**, not as a required dependency, unless you deliberately adopt the hosted API.

---

## 5. Lab lexicon (informal)

| Phrase | Meaning |
|--------|---------|
| **ase'** | “I agree in full” (operator shorthand; not a product term). |

---

## 6. Minimal implementation checklist

- [x] **OpenClaw preset** — [`openclaw/presets/ka2-research/`](../openclaw/presets/ka2-research/) + [`ka2-research-workspace/`](../openclaw/presets/ka2-research-workspace/) (merge `openclaw.agents.ka2-research.json5` into `agents.list`).
- [ ] **Profile** — Cursor sessions: load KA2 prompt from `data/tehuti/.../ka2_agent_system_prompt.md` when doing research-grade work.
- [ ] **Output path** — directory + naming for research essays; Archivist schema for machine-ingestible runs.
- [ ] **gitMaat** — research milestones as tasks; close with evidence links.
- [ ] **Cadence** — calendar or cron: “query tasks → rollup progress → log to gitMaat.”
- [ ] **Storage** — run [`scripts/lab-storage-audit.sh`](../scripts/lab-storage-audit.sh); document sizes / backup per [`LAB-STORAGE-AND-BACKUP.md`](LAB-STORAGE-AND-BACKUP.md).
- [ ] **Guard** — confirm Tehuti Guard rules for web write / shell before widening tool scope.

---

## See also

- [`AGENT-LAB-ENTRY.md`](AGENT-LAB-ENTRY.md) — index of spine + KA2 files.
- [`AGENTS.md`](../AGENTS.md) — session ritual and Git safety.
- [`docs/PUSH-SAFETY.md`](PUSH-SAFETY.md) — do not commit personal research notes by mistake.
