# Agent lab entry (index)

**Purpose:** One page that points agents at **runtime**, **Maat coordination**, **UKMT KA2** sources, **scholarship vs canon / RAG** policy, and **human-facing** interaction docs—without duplicating long prose elsewhere.

**Dual lens:** Understanding how the model behaves belongs together with understanding **how humans meet it** (trust, cognitive load, initiation). Neither replaces the other.

---

## First session

- **[`AGENTS.md`](../AGENTS.md)** — lab root contract; **Every Session** (read `SOUL.md`, `USER.md`, `memory/YYYY-MM-DD.md`, and `MEMORY.md` in main session per that file).
- **Long-form continuity:** [`MEMORY.md`](../MEMORY.md), [`memory/`](../memory/) daily notes.

---

## Git / push safety

- **[`PUSH-SAFETY.md`](PUSH-SAFETY.md)** — what stays local vs public; **[`scripts/git-push-safety-check.sh`](../scripts/git-push-safety-check.sh)** before commit/push.

## Storage and backup

- **[`LAB-STORAGE-AND-BACKUP.md`](LAB-STORAGE-AND-BACKUP.md)** — disk cost of local memory (Postgres, corpora, models, venvs), best practices, backup tiers.
- **[`scripts/lab-storage-audit.sh`](../scripts/lab-storage-audit.sh)** — read-only `du` / `df` snapshot (use `FULL=1` for huge dirs).

---

## Runtime spine

- **[`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md)** — what “connected” means (OpenClaw, Cursor MCP, Ka discovery, gitMaat DB).
- **[`MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md`](MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md)** — frozen spine narrative and ports.
- **[`scripts/lab-runtime-check.sh`](../scripts/lab-runtime-check.sh)** — PASS/FAIL checks (8010, 8014, 8022, optional gateway, Postgres).

---

## Coordination (Maat)

- **`.cursorrules`** (workspace root) — query gitMaat first when the DB is available; Ka discovery, agent IDs.
- **[`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)** — Postgres / `PGVECTOR_DB_URL`, LAN vs localhost, MCP memory.

---

## UKMT / KA2

**Operational prompts (authoritative for KA2 research behavior):**

- [`data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md)
- [`data/tehuti/ukmt-rbg-dataset/ka2_agent_config.json`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_config.json)

**Lineage / Ka Architecture (attribution, ecosystem narrative):**

- [`maat-ecosystem/README.md`](../maat-ecosystem/README.md) — includes KA2 attribution (University of KMT).
- [`maat-ecosystem/docs/ka-architecture-paper.md`](../maat-ecosystem/docs/ka-architecture-paper.md) — deeper spec and methodology context.

**Research agent + goals (one-page architecture):** [`KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md`](KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md) — KA2 + Scout/Analyst/Archivist + gitMaat as task source of truth; Paperclip-style discipline without a second product repo.

**OpenClaw KA2 preset:** merge [`openclaw/presets/ka2-research/openclaw.agents.ka2-research.json5`](../openclaw/presets/ka2-research/openclaw.agents.ka2-research.json5) — see [`openclaw/presets/ka2-research/README.md`](../openclaw/presets/ka2-research/README.md).

---

## Scholarship vs canon / RAG

- **[`TEHUTI-KNOWLEDGE-RAG-MAAT-AUDIT.md`](TEHUTI-KNOWLEDGE-RAG-MAAT-AUDIT.md)** — rings, separation before one vector “blob,” Guard ingest posture, prerequisites to scaling RAG.
- **[`data/tehuti/README.txt`](../data/tehuti/README.txt)** — on-disk layout of Tehuti data trees.

---

## Humans and the model

- **[`INITIATION.md`](INITIATION.md)** — Ma’at-first entry: plain language, no product jargon at the door; five human questions.
- **[`SETUP-WITH-AGENT.md`](SETUP-WITH-AGENT.md)** — installer-style technical setup, copy-paste prompts, ordered links when the human already wants stack names.
- **[`SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md)** — roles when splitting work across agents (find vs decide vs persist).

---

## Long-form lab map

- **[`TEHUTI-LAB-MAAT-ECOSYSTEM-PROPOSAL.md`](TEHUTI-LAB-MAAT-ECOSYSTEM-PROPOSAL.md)** — single onboarding spine for the repo: audit, runbook, phased convergence (juniors / maintainers).
