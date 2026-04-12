# MAAT product map (Tehuti Lab)

Single source of truth for **which repo is which**. Names are easy to confuse; this table is the canonical split.

| Product | Role | Primary path (this workspace) | GitHub / notes |
|--------|------|-------------------------------|----------------|
| **maat-ecosystem** | Ka-body platform: law, organs, `MANIFEST.ka`, bench, site | `maat-ecosystem/` | In-repo; not a separate GitHub product by default |
| **maat-runtime** | User-facing **TypeScript** runtime: coding agent CLI, TUI, web-ui, Slack bot, pods (Pi upstream fork). MCP **client** behavior, toolkits, sellable runtime surface. | `maat-runtime/` | [`Propershare/Maat-runtime`](https://github.com/Propershare/Maat-runtime) |
| **maat-framework** | Single-machine **Python** “batteries included” stack: `maat` CLI, adapt / learn / guard / agent loop; Ollama + Postgres + MCP assumptions | `maat-framework/` | Often cloned from `tehuti-lab/maat-framework` pattern; local copy in tree |
| **maat_core** (underscore) | **Python path locator only** (Tranche 1): resolves paths to `maat-ecosystem/skeleton/schemas`, soul, maatbench contracts. **Not** the TS runtime. | `maat_core/` | Monorepo-local module; not published |
| **MaatLangChain** | Spine: agents, RAG, **`maat_memory/`** (gitMaat) | `maatlangchain/` | Coordination + PostgreSQL memory |
| **maat-forge** (skeleton) | Autonomous local worker: schedules, job loops, bounded experiments, reports to gitMaat — **not** a substitute for `maat-runtime` | `maat-forge/` (lab root) — see [`MAAT-FORGE.md`](MAAT-FORGE.md) | First job: `jobs/first-bounded-loop.mjs` |
| **maat-control-plane** | Python **`maat`** CLI — **`doctor`** implemented (manifest/profile, paths, gateway, stack, DB, MCP ports, safety); `setup` / `enroll` / repair TBD | [`maat-control-plane/`](../maat-control-plane/) — [`MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md) | `pip install -e ./maat-control-plane` |

## Default ports (lab network identity)

Use these as the **conventional** internal/LAN ports so operators and agents share one mental map (not random services). Ka discovery (**8010**) and full MCP organ matrix: [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md), live `/manifest`.

| Port | Service |
|------|---------|
| **4242** | **maat-sentinel** HTTP API (live awareness, `GET /status/<machine_id>`, etc.) |
| **8013** | **Tehuti Guard v1** decision API (`POST /decision`) — [`tehuti-guard/guard/`](../tehuti-guard/guard/) |
| **8014** | Tehuti Core (brain / policy surface) |
| **8022** | Maat Memory MCP |

**Sentinel override:** `MAAT_SENTINEL_PORT` or `maat-sentinel serve --port` (never hard-lock a port in docs only).

**Guard v1 override:** `TEHUTI_GUARD_PORT` or `tehuti-guard-serve --port` (default **8013**).

## Related naming (do not mix)

- **“MAAT Core” (constitutional layer)** → truth in `maat-ecosystem/skeleton/`, `soul/`, contracts — **not** the same as the **`maat-runtime`** folder name.
- **Legacy path `maat-ecosystem/.../maat-core/schemas`** in some runners and docs refers to an **old on-disk layout** for schemas; canonical schemas live under **`maat-ecosystem/skeleton/schemas/`**. That legacy string is **not** the Git repo `maat-runtime`.
- **MCP organ labels** (e.g. Tehuti Core on **8014**) may appear as `maat-core` in older configs; the **service** is Tehuti Core / brain — see [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md) and Ka discovery **8010**.

## See also

- [`docs/MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md) — **truth / order / balance** checklist (canonical tree, entry path, wire vocabulary, open runtime + user test)  
- [`docs/INITIATION.md`](INITIATION.md) — **Ma’at initiation**: plain five questions, no product names at entry; internal translation for builders  
- [`docs/SETUP-WITH-AGENT.md`](SETUP-WITH-AGENT.md) — **technical setup**: prompts for the agent, ordered links  
- [`docs/SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md) — **operator map** (what talks to what)  
- [`docs/ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) — **endpoints**, decision vocabulary, BYO  
- [`docs/FIRST-RUN.md`](FIRST-RUN.md) — **bootstrap** Guard + Sentinel  
- [`docs/GITHUB-REPO-MAP.md`](GITHUB-REPO-MAP.md) — **GitHub federation**: repo list, public/private guidance, dependency diagram, publish prep
- [`docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](MAAT-LIGHTWEIGHT-INTELLIGENCE.md) — **token-efficient** MAAT: middleware not giant prompts, retrieval-first memory, tiered models
- [`docs/MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md) — **zero-trust** initiation, identity stack, prompt containment, dual containment
- [`docs/MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md) — lab **control plane** (Python MCP bias, four layers, `maat setup`/`doctor`/`repair`/`enroll`, profiles, gateway protection)
- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) — distributed **MAAT Immune System** (Guard, Sentinel, Memory, Bench, Forge) + evolution boundaries
- [`docs/WORKSPACE-KA-MAP.md`](WORKSPACE-KA-MAP.md) — organs ↔ folders
- [`docs/MAAT-FRAMEWORK-REPORT.md`](MAAT-FRAMEWORK-REPORT.md) — five-layer architecture
- [`docs/TEHUTI-LAB-TREE.md`](TEHUTI-LAB-TREE.md) — visual tree of `~/.n8n`.
