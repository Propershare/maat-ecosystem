# Lab canonical tree & tech stack (GitHub / operator truth)

**Purpose:** One place that matches **disk layout**, **symlinks**, **runtime stack**, and **known duplicates** so docs, READMEs, and GitHub descriptions stay aligned. **Update this file** when you move major folders.

**Related:** [`TEHUTI-LAB-TREE.md`](TEHUTI-LAB-TREE.md) (visual + ASCII), [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) (product names), [`GITHUB-REPO-MAP.md`](GITHUB-REPO-MAP.md) (federation), [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md) (ports, DB).

---

## 1. What this lab is

| Layer | Description |
|-------|-------------|
| **Workspace** | `~/.n8n` (Tehuti Lab monorepo) — products side by side, shared `docs/`, not one installable binary. |
| **Ka-body (canonical)** | `maat-ecosystem/` — `MANIFEST.ka`, organs (`soul/`, `brain/`, `memory/`, `hands/`, …), `site/`, `maatbench/`, **`mcp-servers/`** (runnable MCP spine). |
| **Memory / coordination** | PostgreSQL **`maat_memory`** via **`PGVECTOR_DB_URL`**; Python code in **`maatlangchain/maat_memory/`** (gitMaat). |
| **Agent surfaces** | **Cursor** (IDE), **OpenClaw** (`openclaw/` — gateway, Telegram, tools), optional **Tehuti Lab WebUI** / Open WebUI. |
| **Policy (Guard)** | **Tehuti Guard (Python decision API, lab)** HTTP **8013** — code at **`tehuti-guard/guard/`** (lab root **sibling** of `maat-ecosystem/`, **not** inside `mcp-servers/`). Listed in **`MANIFEST.ka`** and live **`GET :8010/manifest`** as organ **`policy`**. |

### 1.1 Disk vs runtime (Guard vs Ka-body)

```mermaid
flowchart TB
  subgraph disk["On disk — lab root ~/.n8n"]
    ME[maat-ecosystem]
    ML[maatlangchain]
    OC[openclaw]
    TG_SRC[tehuti-guard]
    MCP[maat-ecosystem/mcp-servers]
  end

  subgraph run["Runtime — ports"]
    P8010[8010 Ka discovery]
    P8013[8013 Tehuti Guard HTTP]
    P8014[8014 Tehuti Core (brain service)]
    P8022[8022 Maat Memory MCP]
    PG[(Postgres gitMaat)]
    GW[OpenClaw ~18790]
  end

  ME --> P8010
  MCP --> P8010
  MCP --> P8014
  MCP --> P8022
  TG_SRC --> P8013
  ML --> PG
  OC --> GW
```

---

## 2. Filesystem — canonical layout (high level)

**Rule:** **`maat-ecosystem/`** holds the **body map + MCP server code** for this lab’s Ka spine. **Sibling folders** at the repo root are **separate products** (their own release stories) — see [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md).

```
~/.n8n/  (lab root)
├── maat-ecosystem/          ← Canonical Ka-body + mcp-servers/ (see below)
├── mcp-servers/             ← SYMLINK → maat-ecosystem/mcp-servers/
├── maatlangchain/            ← gitMaat, RAG, agents
├── maat-runtime/             ← TS coding-agent runtime (separate GitHub product)
├── maat_core/                ← `maat_core` (Python module): schema/path locator (not `maat-runtime`, not Tehuti Core service)
├── maat-framework/           ← Python “batteries included” stack
├── maat-apps/                ← Workflow app manifests (duplicate of hands/apps — see §4)
├── openclaw/                 ← Gateway, Telegram, skills (mcporter); primary operator channel — not n8n
├── tehuti-guard/             ← Tehuti Guard (Python decision API, lab) HTTP :8013 — NOT under maat-ecosystem/ (policy enforcement)
├── maat-control-plane/       ← maat doctor CLI
├── docs/                     ← Operator & architecture docs (this file)
├── scripts/                  ← lab-runtime-check.sh, starters
├── systemd-services/         ← unit files (paths often use …/mcp-servers/…)
├── AGENTS.md, README.md, .cursorrules
└── …                         ← n8n, training, models, experiments (see TEHUTI-LAB-TREE)
```

### 2.1 Inside `maat-ecosystem/` (body + MCP)

```
maat-ecosystem/
├── MANIFEST.ka
├── mcp-servers/              ← Canonical home: Ka discovery :8010, Tehuti Core :8014, Maat Memory :8022, …
├── soul/, brain/, memory/, hands/, …
├── hands/
│   ├── apps/                 ← Ka workflow apps (operator, receptionist, …) — preferred location for *body* apps
│   └── mcps/                 ← Client adapters (Python), not the daemon tree
├── skeleton/schemas/
├── site/
└── docs/
```

---

## 3. Tech stack (runtime)

| Layer | Technology | Notes |
|-------|------------|--------|
| **DB** | **PostgreSQL** (`maat_memory`, port **5432** typical) | `PGVECTOR_DB_URL` in `.env`; not the same as **8017 Postgres MCP** (tool surface). |
| **MCP / HTTP organs** | **Python** (FastMCP, aiohttp), **mcpo**/uvx for HTTP wrappers | Code under **`maat-ecosystem/mcp-servers/`**; discovery **8010**. |
| **gitMaat** | **Python** + **psycopg2** / SQLAlchemy per `maatlangchain` | Same DB as Maat Memory MCP when configured. |
| **RAG / agents** | **MaatLangChain**, LangChain, optional **Chroma** | `maatlangchain/` |
| **Gateway** | **OpenClaw** (Node), default **18790** | `~/.openclaw/openclaw.json`; workspace = lab root. |
| **IDE agents** | **Cursor** + MCP config | Bearer to organ URLs from **8010/manifest**. |
| **Automation** | **n8n** (optional), workflows under `n8n-workflows/` | |
| **Models** | **Ollama** (typical **11434**), model dirs under `models/` / `ollama-nuggets/` | |
| **Policy** | **Tehuti Guard (Python decision API, lab)**, **8013** | `tehuti-guard/guard/` |
| **Awareness** | **maat-sentinel**, **4242** | Optional; feeds Guard. |

**Verify spine:** [`scripts/lab-runtime-check.sh`](../scripts/lab-runtime-check.sh) — [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md).

---

## 4. Workflow apps: `maat-apps/` vs `hands/apps/` (duplication)

| Path | Role |
|------|------|
| **`maat-ecosystem/hands/apps/`** | **Preferred** for Ka-body workflow bundles (operator, receptionist, researcher, teacher) — matches **Hands** organ in `MANIFEST.ka`. |
| **`maat-apps/`** (lab root) | **Duplicate / historical** manifests and policies; some `hands/apps/*/manifest.json` still reference `maat-apps/...` paths. **Consolidation TBD** — do not add new apps in two places without updating the other. |

**Operator rule:** Treat **`hands/apps/`** as canonical for **new** body-aligned work; migrate **`maat-apps/`** when you touch those files.

---

## 5. Symlinks (do not break)

| Path | Target |
|------|--------|
| `mcp-servers/` (lab root) | `maat-ecosystem/mcp-servers/` |

Systemd and scripts use **`/home/suspect/.n8n/mcp-servers/...`** — resolves correctly via symlink.

---

## 6. GitHub narrative (short)

- **Umbrella / doctrine / Ka-body:** `maat-ecosystem/` (+ docs in `docs/`).
- **Sellable TS runtime:** `maat-runtime/` → separate repo [`Propershare/Maat-runtime`](https://github.com/Propershare/Maat-runtime).
- **Memory spine:** `maatlangchain/` (gitMaat) until split per [`GITHUB-REPO-MAP.md`](GITHUB-REPO-MAP.md).
- **This monorepo** is a **lab workspace**, not a single shipped product — see [`GITHUB-REPO-MAP.md`](GITHUB-REPO-MAP.md) *Lab workspace vs GitHub*.

---

**Last updated:** 2026-04-13 — Tehuti Guard **8013** in `MANIFEST.ka` + Ka discovery manifest (`policy` organ); OpenClaw as primary channel note; disk vs runtime diagram; `maat-apps` vs `hands/apps` note.
