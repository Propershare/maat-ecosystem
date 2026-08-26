# MEMORY.md — curated workspace memory

Distilled from ongoing Maat / Tehuti Lab discussions (see also `memory/YYYY-MM-DD.md`).

**Framework (layers, Tranche 1 `maat_core` locator):** `docs/MAAT-FRAMEWORK-REPORT.md`  
**Next tranche (tasks + enforcer):** `docs/MAAT-CHECKPOINT-NEXT-TRANCHE.md`, `scripts/enforce-maat-contracts.py`  
**Agent datasets + FB narrative (essay):** `docs/MAAT-AGENT-DATASETS-AND-PUBLIC-NARRATIVE.md`  
**Scout / Analyst / Archivist (structured Archivist):** `docs/SCOUT-ANALYST-ARCHIVIST.md`, `AGENTS.md` multi-agent section, `gemma4-toolshim/swarm/expert_config.py`

## Maat ecosystem vs OpenClaw

- **Maat ecosystem** = Discovery (`8010`), organ MCPs (e.g. Tehuti Core `8014`, Maat Memory `8022`), Postgres via `PGVECTOR_DB_URL`, soul under `maat-ecosystem/soul/`. Not inside the OpenClaw GitHub repo.
- **OpenClaw** = personal assistant runtime (gateway, channels, models). Connects to the ecosystem by **calling those HTTP/OpenAPI endpoints** once configured — **not** pre-wired in default `openclaw.json`.
- **Connect docs:** `docs/GITMAAT-CONNECT.md`, `docs/MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md` (checkpoint doc, not "stop building"), `CLAWD-MCP-ACCESS.md` for LAN-exposed MCPs from another PC.

## Operators vs agents

- **Repo clone** is for whoever **runs and upgrades** the body, not for "every agent." Clients need **host + MCP URLs** (+ auth); they do not get automatic LAN discovery from `git clone` alone.
- **`PGVECTOR_DB_URL`:** required for **organ servers** that talk to gitMaat/Postgres; **not** the main way chat clients "connect" (they use `8014` / `8022` tools).

## Learning and heartbeat

- **Learning** = persisted **tool calls** to gitMaat / memory organs (tasks, learnings, decisions), same DB for all aligned clients.
- **Heartbeat:** organ **`/health`** (liveness) vs **periodic gitMaat/task checks** in agent workflows (attention); both matter, different jobs.

## MaatBench

- **Benchmark / contract harness** under `maat-ecosystem/maatbench/`, not a Discovery-listed organ. LLM Ollama eval is a **separate script** in `scripts/` — not automatic "bench talks to live `8014`."

## Tehuti Guard and setup UX

- **Tehuti Guard** = policy / rings / validation — **separate** from zero-touch install and **credential lifecycle**.
- **Intended evolution:** local **key issue + rotation**, trust-on-LAN, **non-dev** "place it and trust" setup — treat today's manual steps as **debt**, not final design.

## Florida Trust Law RAG (fl-trust-law)

- **Status:** Test payload → Active (RAG query available as of 2026-05-07)
- **Corpus:** 2462 chunks from 39 source files (949KB) covering FL Statutes Ch. 731-736, FL Court Rules, 30+ case law opinions
- **Index:** FAISS cosine-similarity (768-dim, `nomic-embed-text` via Ollama)
- **Query:** `python3 scripts/query_rag.py "query" --top-k 5` or via Tehuti Core MCP `query_florida_trust_law` tool
- **Scope drift detection:** blocks non-Florida/non-trust queries with RBL flag
- **Legal advice warning:** built into scope check
- **No n8n workflow** (per user constraint)
- **Gateway:** `fl-trust-law` registered in gateway registry, tools allowlisted
- **Tehuti Core:** `query_florida_trust_law` tool added to MCP server
- **Not yet:** gitMaat integration for persistent memory, OpenClaw preset, Tehuti Guard 3-ring governance, promotion to active domain

## Principle

- **Maat Ecosystem** should be an **evolving system**: truth in status and docs, ordered spine, memory that compounds, Guard/bench as feedback - **Maat in behavior**, not only in naming.
