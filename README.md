# Tehuti Lab workspace

**What this is:** A monorepo for Maat-aligned AI infrastructure: constitutional schemas, Guard/Sentinel, agents, MCP, and operator docs. It is a **lab tree**, not a single installable product.

**Public state (be explicit):** This repository currently holds the **canonical documentation** and an **evolving lab workspace** on `main`. Many **runtime organs** (e.g. `tehuti-guard/`, `maat-runtime/`, full MCP stacks) may still be **local or untracked** until they are ready to ship with **stable paths and contracts**. What is pushed today is **doctrine and operator entry** — not the whole machine. **Runtime proof** (e.g. one live `POST /decision` path with joinable `correlation_id`) is the next **evidence-bearing** milestone, not another broad doc-only pass.

**Operator connection loop** (Cursor vs OpenClaw vs `.env` vs MCP — where credentials go, verification, Telegram allowlist): **[`AGENTS.md`](AGENTS.md)** section *Credentials and connection loops*.

**Runtime hookup** (scripts + spine doc): [`docs/RUNTIME-HOOKUP.md`](docs/RUNTIME-HOOKUP.md), [`scripts/lab-runtime-check.sh`](scripts/lab-runtime-check.sh) — when Tehuti Guard (**8013**) is up, the script smoke-tests **`POST /decision`** and **`correlation_id`** echo. **Adapter E2E proof** (envelope → decision → enforce → JSONL log): [`scripts/guard_adapter_e2e_demo.py`](scripts/guard_adapter_e2e_demo.py).

**Terminal agents + memory (default posture):** [`docs/TERMINAL-MEMORY-DEFAULT.md`](docs/TERMINAL-MEMORY-DEFAULT.md) — Memory MCP + gitMaat are **required** for shell-capable agents unless explicitly disabled; see [`AGENTS.md`](AGENTS.md) *Default agent posture*.

**Tehuti Guard (npm vs lab Python API):** [`docs/TEHUTI-GUARD-PRODUCTS.md`](docs/TEHUTI-GUARD-PRODUCTS.md) — disambiguates [Propershare/tehuti-guard](https://github.com/Propershare/tehuti-guard) (MCP proxy) from `tehuti-guard/guard/` (`:8013`).

## One truth (canonical Ka-body)

The **canonical MAAT Ka-body** (organs, `MANIFEST.ka`, soul, skeleton schemas, MaatBench) lives here:

**[`maat-ecosystem/`](maat-ecosystem/)** — start with [`maat-ecosystem/README.md`](maat-ecosystem/README.md) and [`maat-ecosystem/MANIFEST.ka`](maat-ecosystem/MANIFEST.ka). **Ka spine MCP processes** live under [`maat-ecosystem/mcp-servers/`](maat-ecosystem/mcp-servers/) (root `mcp-servers` → symlink).

### Legacy / duplicate layout (read-only intent)

After a Git merge, **root-level** folders such as `maatbench/`, `maat-core/`, `maat-apps/` (standalone-era layout) may still exist beside `maat-ecosystem/`. Treat them as **legacy reference** unless you are explicitly maintaining them. **Do not** start new work there — use **`maat-ecosystem/`** and its subpaths. Details: [`archive/README.md`](archive/README.md).

---

## Where to start (entry paths)

| You are… | Open |
|----------|------|
| **A human** (no jargon) | [`docs/INITIATION.md`](docs/INITIATION.md) |
| **An operator** (first curl / health) | [`docs/FIRST-RUN.md`](docs/FIRST-RUN.md) |
| **Integrating HTTP / decisions** | [`docs/ENDPOINTS-AND-DECISIONS.md`](docs/ENDPOINTS-AND-DECISIONS.md) |
| **Mapping the whole lab** | [`docs/SYSTEM-CONNECTIONS.md`](docs/SYSTEM-CONNECTIONS.md) |
| **Canonical folder tree + tech stack (GitHub)** | [`docs/LAB-CANONICAL-TREE-AND-STACK.md`](docs/LAB-CANONICAL-TREE-AND-STACK.md) |
| **Repo vs product names** | [`docs/MAAT-PRODUCT-MAP.md`](docs/MAAT-PRODUCT-MAP.md) |
| **Git: avoid leaking secrets / personal files** | [`docs/PUSH-SAFETY.md`](docs/PUSH-SAFETY.md) |
| **Disk / backup / cost of local memory** | [`docs/LAB-STORAGE-AND-BACKUP.md`](docs/LAB-STORAGE-AND-BACKUP.md), [`scripts/lab-storage-audit.sh`](scripts/lab-storage-audit.sh) |

**Agent-assisted setup:** [`docs/SETUP-WITH-AGENT.md`](docs/SETUP-WITH-AGENT.md)

**Workspace home for Cursor/OpenClaw:** [`AGENTS.md`](AGENTS.md)

---

## Ma’at audit → action plan

Tracked checklist: [`docs/MAAT-AUDIT-ACTION-PLAN.md`](docs/MAAT-AUDIT-ACTION-PLAN.md)

---

## License

See [`maat-ecosystem/LICENSE`](maat-ecosystem/LICENSE) for ecosystem code; individual packages may declare their own.
