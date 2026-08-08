# Tehuti Lab — Maat Ecosystem Proposal & Audit

**Role:** Head development proposal  
**Audience:** Junior engineers and future maintainers  
**Workspace:** Tehuti Lab monorepo (historically rooted at `~/.n8n`; see §9 for naming)  
**Date context:** Written for rollout planning as of 2026 Q2  

**Revision (2026-04-07):** Canonical **Ka-body** `maat-ecosystem/` was synced from `~/maat-ecosystem` into this monorepo (see `maat-ecosystem/LAB-WORKSPACE.md`). Root log noise moved under `logs/`; stray editor files under `_quarantine/`. Full workspace-to-Ka mapping: `docs/WORKSPACE-KA-MAP.md`.

This document is a **single onboarding spine**: what exists today, how it fits together, how to run and test it, and how we converge on a **Maat-native distribution** (OpenClaw fork + Pi engine + gitMaat governance).

---

## 1. Executive summary

Tehuti Lab is building **Maat-aligned agent infrastructure**: local-first models, coordinated memory (gitMaat), optional policy gates (TehutiGuard), and operational glue (OpenClaw gateway, MCP, n8n, WebUI).

**Strategic decision (approved direction):**

- **Fork OpenClaw** (MIT), **rebrand** as the Maat distribution’s gateway/shell, **merge upstream** regularly.
- Treat **Pi** (`@mariozechner/pi-coding-agent`, `pi-ai`) as the **engine** we depend on, not something we rewrite.
- Implement **Maat-specific behavior** via **extensions, tools, config presets**, and **gitMaat hooks**—not by forking Pi.

**What this proposal adds for juniors:**

- A **map of the repo** (audit).
- A **runbook**: prerequisites, smoke tests, deployment tiers.
- A **phased plan** so ecosystem work is incremental and testable.

---

## 2. Principles (non-negotiable)

| Principle | Meaning in practice |
|-----------|---------------------|
| **Truth** | Config and docs describe what actually runs; no “paper integrations.” |
| **Balance** | Cloud APIs when needed; local Ollama as default for high-volume agents. |
| **Order** | Tasks and coordination live in **gitMaat** (DB), not scattered `.md` checklists. |
| **Justice** | Respect licenses (OpenClaw/Pi MIT); attribute upstream. |
| **Sankofa** | Log learnings and failures to gitMaat so we do not repeat them. |

**Law for agents (from `.cursorrules`):** before substantive work, **query gitMaat** for pending tasks and recent history when the database is available.

---

## 3. Architecture: three layers

```text
┌─────────────────────────────────────────────────────────────┐
│  Maat layer (yours)                                         │
│  gitMaat · TehutiGuard · expert configs · Gemma tooling     │
│  extensions/skills · policy · naming · defaults           │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  Distribution shell (fork OpenClaw → Maat branded)           │
│  gateway · channels · sessions · ~/.openclaw config         │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  Pi engine (upstream npm packages)                          │
│  agent session · model registry · tools baseline            │
└─────────────────────────────────────────────────────────────┘
```

**Local inference today:** Ollama on the worker host (e.g. `gemma4:e4b`, `gemma4:e2b`, `gemma4:26b`). OpenClaw speaks **OpenAI-compatible** APIs to Ollama when configured under `models.providers.ollama`.

**Tool-call bridge:** `gemma4-toolshim/` provides an optional HTTP shim (e.g. port `11435`) that normalizes Gemma-style `<thinking>` into OpenAI `tool_calls` and collects **training JSONL** for future fine-tunes.

---

## 4. Complete workspace audit (what lives under this root)

Below is a **catalog** of major trees observed in Tehuti Lab. Treat this as the **inventory** a junior uses before adding a new project (avoid duplicate “yet another agent folder” without updating this doc).

**Ka layout:** The **canonical nine-organ body** (MANIFEST-driven) is `maat-ecosystem/`. The **rest of the monorepo** is mapped to the same metaphor in `docs/WORKSPACE-KA-MAP.md` so you know where to file new work without creating one-off top-level folders.

### 4.1 `maat-ecosystem/` — Ka body (canonical product tree)

Synced into this repo as the **MAAT Ecosystem** implementation (blood, brain, hands, ka, memory, senses, skeleton, soul, voice), plus bench and CLI stubs.

| Path (under `maat-ecosystem/`) | Organ | Purpose |
|------------------------------|--------|---------|
| `MANIFEST.ka` | DNA | Machine-readable organ map; **read first**. |
| `soul/` | Soul | Identity, constitution, policy (`constitution.md`, `sacred.md`, `policy.py`, …). |
| `brain/` | Brain | Reasoning, model adapters, learning (`config.yaml`, `reasoning/`, `models/`). |
| `memory/` | Memory | Episodic / semantic / patterns / task memory subsystem code. |
| `hands/` | Hands | Tools, skills, MCP, **apps** (`hands/apps/researcher/` includes `AGENTS.md` for the researcher role). |
| `senses/` | Senses | Events, triggers (`events.py`, `EVENTS.md`). |
| `voice/` | Voice | Output / templates / UI-facing assets. |
| `ka/` | Ka | Health, healing, pain, pulse (`pulse.yaml`, `evolve.yaml`, …). |
| `skeleton/` | Skeleton | JSON Schemas (`schemas/*.schema.json`), portability notes. |
| `blood/` | Blood | Inter-organ bus, packs, shared event definitions. |
| `maatbench/` | Doctor | Contract tests and runners for the body. |
| `maat-cli/` | CLI | Thin CLI entry (`maat-cli/maat`). |
| `docs/` | Docs | Architecture papers and audits inside the body. |
| `LAB-WORKSPACE.md` | — | How this tree relates to the former `~/maat-ecosystem` clone. |

### 4.2 Core Maat & LangChain product (monorepo, beside the Ka body)

| Path | Purpose |
|------|---------|
| `maatlangchain/` | RAG, agents, APIs; **contains `maat_memory/` (gitMaat)** — coordination DB, tasks, logging. |
| `maat-framework/` | Lighter Maat agent/config conventions (Python). |
| `maatcode/` | Placeholder / future MaatCode (OpenCode-style) work; align with `docs/MAATCODE-FORK-STRATEGY.md`. |

### 4.3 Gateway & desktop agent OS

| Path | Purpose |
|------|---------|
| `openclaw/` | Full **OpenClaw** tree: gateway, extensions, UI packages, channel integrations. This is the primary **fork candidate** for the Maat distribution. |
| `claw-code/` | Related OpenClaw / claw tooling experiments (verify before relying in prod). |

**Runtime config (not in repo):** `~/.openclaw/openclaw.json` — models, `agents.defaults.model.primary`, channel tokens, gateway bind/port.

### 4.4 Local models & tuning

| Path | Purpose |
|------|---------|
| `gemma4-toolshim/` | Shim proxy, training capture (`captures.jsonl`), `generate_training.py`, `finetune.py` (Unsloth/Gemma-3 lineage until Gemma 4 in HF). |
| `ollama-nuggets/` | Model management notes/scripts. |
| `fine-tuned-models/` | Output artifacts for local models. |
| `training/` | Training-related assets (verify structure per project). |

### 4.5 MCP & automation

| Path | Purpose |
|------|---------|
| `mcp-servers/` | MCP servers (typical port band **8011–8019** per workspace rules). |
| `n8n-mcp/` | n8n-facing MCP integration, deploy helpers, docs. |
| `n8n-workflows/` | Exported or shared workflows. |
| `nodes/` | Custom n8n nodes (if present). |

### 4.6 Policy, search, identity

| Path | Purpose |
|------|---------|
| `tehuti-guard/` | TypeScript policy / governance enforcement. |
| `tehuti-search/` | Search services aligned with lab needs. |
| `tehuti-config/` | Centralized config/secrets layout (do **not** commit secrets). |
| `tehuti-ldap/` | Directory integration (lab-specific). |

### 4.7 Web UI & chat frontends

| Path | Purpose |
|------|---------|
| `tehuti-lab-webui/` | Tehuti Lab WebUI fork (Open WebUI lineage). |
| `open-webui/` | Alternate/stock Open WebUI tree if used. |
| `tehuti-lab-webui-venv/` | Python venv for WebUI. |

### 4.8 Demos, RAG experiments, analysis

| Path | Purpose |
|------|---------|
| `hermes-agent/` | Agent experiments. |
| `langgraph-agent-demo/` | LangGraph demo. |
| `weknora-analysis/` | Weknora-related analysis / stack (multi-language monorepo). |
| `rag-video-workflow.json`, `social-media-content-generator-ollama.json` | Example automation bundles at root. |

### 4.9 Infra, scripts, observability

| Path | Purpose |
|------|---------|
| `systemd-services/` | Service unit templates or drops for lab hosts. |
| `scripts/` | Shared automation. |
| `hooks/` | Git or agent hooks. |
| `monitoring/`, `stats/`, `logs/` | Operational data (often gitignored partially). |
| `reverse-proxy/`, `fix-n8n-502.sh`, `KILL-DOCKER-PROXY-5678.sh` | Reliability / reverse proxy fixes. |

### 4.10 Knowledge & agent continuity (files)

| Path | Purpose |
|------|---------|
| `memory-bank/` | **Human-readable** system docs and patterns (context, not task DB). |
| `memory/` | Daily agent notes (`YYYY-MM-DD.md`) per `AGENTS.md`. |
| `AGENTS.md`, `SOUL.md`, `USER.md`, `HEARTBEAT.md` | Workspace persona and session rules for coding agents. |
| `skills/` | Cursor/agent skills (portable playbooks). |
| `docs/` | Lab docs including this proposal. |

### 4.11 Legacy / binary / caution zones

| Path | Notes |
|------|--------|
| `binaryData/`, `cache/` | Runtime noise; usually do not version. |
| `logs/` | Hygiene target for `crash.journal`, `n8nEventLog*.log`, host `.log` files (many patterns gitignored). |
| `_quarantine/` | Stray editor saves / ambiguous files during pivot; review and delete or relocate. |
| `staydangerous/`, `monetization/`, `from/` | Review purpose before treating as canonical. |
| Large archives (e.g. `maatbench.rar`) | Binary; document purpose or move to `backups/`. |

---

## 5. What we already proved in this root (evidence-based)

These are **concrete capabilities** validated in this environment (adjust if your host differs):

- **GPU + Ollama:** NVIDIA driver and Ollama models (e.g. `gemma4:e2b`, `gemma4:e4b`, `gemma4:26b`) present; native **`tool_calls`** observed for Gemma 4 on Ollama in tests.
- **OpenClaw + Ollama:** `openclaw models list` can show **local models as default** when `agents.defaults.model.primary` is `ollama/gemma4:e4b` (avoid accidental cloud defaults).
- **Gemma tool shim:** `gemma4-toolshim/shim.py` health + OpenAI-format completions + capture pipeline; local regression script `test_gemma4_e2b_local.py`.
- **Expert routing seed:** `gemma4-toolshim/swarm/expert_config.py` — pattern for multiple experts (RAG, code, ops) and model assignment.

---

## 6. Integration map (how things talk)

| Concern | Typical interface | Notes |
|---------|-------------------|--------|
| **Agents** | OpenClaw gateway | Binds LAN/loopback; token auth in config. |
| **LLM** | Ollama `:11434` | OpenAI-compatible path from OpenClaw provider config. |
| **Optional shim** | `:11435` (or custom) | For clients that need shimmed `tool_calls` + captures. |
| **MCP** | HTTP/SSE on 801x | Expose file, shell, gitMaat tools to agents. |
| **gitMaat** | PostgreSQL + `maat_memory` | Query-first task source for Maat Law. |
| **Web chat** | Tehuti Lab WebUI | Separate process from OpenClaw; align model endpoints if needed. |
| **Workflows** | n8n + n8n-mcp | Automation and human-in-the-loop glue. |

**Junior rule:** draw this table on a whiteboard for your machine with **actual ports** from `openclaw.json`, systemd units, and `ss -tlnp`.

---

## 7. Roadmap — phases a junior can execute

### Phase 0 — Read & safety (day 1)

1. Read root `AGENTS.md`, `maat-ecosystem/MANIFEST.ka`, and `docs/WORKSPACE-KA-MAP.md`, then this proposal.
2. Never commit **tokens** from `~/.openclaw/openclaw.json` or `tehuti-config/secrets/`.
3. Record your machine’s **ports** and **service names** in a private runbook (not necessarily in git).

### Phase 1 — Local smoke (day 1–2)

**Prerequisites:** Node 22+ (for OpenClaw dev), Python 3.11+ (MaatLangChain), Ollama, PostgreSQL if testing gitMaat.

| Step | Command / action | Pass criterion |
|------|------------------|----------------|
| Ollama | `ollama list` | Expected models pulled. |
| OpenClaw models | `openclaw models list` | Primary model is **local** if that is the policy. |
| Gemma regression | `cd gemma4-toolshim && python3 test_gemma4_e2b_local.py` | All OK lines. |
| Gateway | start gateway per your install (app or CLI) | Control UI reachable; health/metrics if documented. |

### Phase 2 — Maat memory connectivity (week 1)

1. Configure `PGVECTOR_DB_URL` / DB URL per `maatlangchain` docs.
2. From Python, run the **minimal gitMaat query** in `.cursorrules` (or project README) to list pending tasks.
3. Log one **test decision** or **learning** to prove write path.

### Phase 3 — Fork “Maat OpenClaw” (week 1–2)

1. Create org repo: e.g. `tehuti/maat-openclaw` (name TBD).
2. Push mirror of `openclaw/`, add **upstream** remote to `https://github.com/openclaw/openclaw`.
3. **Rebrand** user-facing strings and default models; **retain MIT** + copyright notice.
4. Document merge cadence: e.g. **biweekly upstream merge**.

### Phase 4 — First Maat extension (week 2–3)

Deliver one vertical slice:

- **Tool:** `maat_query_tasks` / `maat_log_learning` (thin wrapper over `maat_memory` HTTP or DB).
- **Hook:** after risky tool execution, optional **TehutiGuard** check stub (even “allow all” with logging first).

### Phase 5 — Deploy tiers (week 3+)

| Tier | Goal |
|------|------|
| **Dev** | Single workstation; LAN gateway; Ollama local. |
| **Staging** | Second host; same configs; snapshot DB. |
| **Prod** | Hardened tokens; systemd for gateway + MCP; backups; **no paid model fallbacks** unless explicit. |

---

## 8. Testing & deployment checklist (printable)

**Before any deploy:**

- [ ] `openclaw doctor` (or project equivalent) clean
- [ ] Default model = agreed local (`ollama/gemma4:e4b` or policy)
- [ ] Paid providers only **opt-in** per session if cost-sensitive
- [ ] MCP health spot-check
- [ ] gitMaat read/write smoke test
- [ ] Rollback note: previous `openclaw.json` backup

**After deploy:**

- [ ] Log a **deployment entry** to gitMaat (what changed, version, host)
- [ ] Update **memory-bank** only for durable architectural facts (optional)

---

## 9. Workspace naming & pivot hygiene (`~/.n8n`)

The directory name reflects **historical n8n usage**, not the full Maat ecosystem.

**Current pivot rules:**

- **Logical product root:** `maat-ecosystem/` (Ka body) + `docs/` (strategy/runbooks). See `docs/WORKSPACE-KA-MAP.md` before adding new top-level directories.
- **Root cleanup:** operational logs belong under `logs/`; ambiguous one-off files under `_quarantine/` until classified.
- **Long term:** Rename workspace to e.g. `~/tehuti-lab` with a **migration checklist** (grep `/home/.../.n8n`, systemd, OpenClaw workspace paths). Until then, `~/maat-ecosystem` may still exist as an older clone—prefer the copy inside this repo (see `maat-ecosystem/LAB-WORKSPACE.md`).

---

## 10. Glossary

| Term | Meaning |
|------|---------|
| **Maat** | Governance principles (truth, balance, order, justice, reflection). |
| **gitMaat / Maat Memory** | PostgreSQL-backed coordination in `maatlangchain/maat_memory/`. |
| **Tehuti Lab** | This workspace and its operators. |
| **OpenClaw** | Gateway + channel agent distribution (MIT). |
| **Pi** | Minimal coding agent engine OpenClaw builds on. |
| **MCP** | Model Context Protocol tool servers. |
| **Shim** | HTTP adapter for tool-call normalization (Gemma). |

---

## 11. References inside this repo

- `maat-ecosystem/MANIFEST.ka` — Ka organ map (read first for the body)  
- `maat-ecosystem/README.md` — ecosystem overview and organ layout  
- `maat-ecosystem/LAB-WORKSPACE.md` — monorepo vs `~/maat-ecosystem`  
- `docs/WORKSPACE-KA-MAP.md` — nine-organ map of the **whole** lab tree  
- `docs/MAATCODE-FORK-STRATEGY.md` — long-term MaatCode direction  
- `docs/GITMAAT-CONNECT.md` / `docs/GITMAAT-AGENTS-ACCESS.md` — gitMaat connectivity  
- `gemma4-toolshim/README.md` — shim, training pipeline, systemd example  
- `openclaw/docs/providers/ollama.md` — OpenClaw Ollama setup (mirror: [docs.openclaw.ai](https://docs.openclaw.ai/providers/ollama))  
- `.cursorrules` — Maat Law for agents in this workspace  

---

## 12. Maintainer note

This file is the **onboarding hub**. When you add a new major directory or change default inference policy:

1. Update **§4 Audit** and **§5 Evidence**.
2. Log the decision to **gitMaat**.
3. Optionally add one paragraph to `memory-bank/systemPatterns.md` if it is a recurring deployment pattern.

**End of proposal.**
