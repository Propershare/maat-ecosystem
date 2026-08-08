# MAAT Lab Control Plane

**Status:** Specification — defines how the lab stops **environment drift**, **install fragility**, and **unclear sacred boundaries** by unifying **protection**, **enrollment**, **repair**, and **mutation classification**. It complements [`MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) (immune doctrine), [`MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md) (initiation envelopes, identity, prompt containment), and [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) (product boundaries).

**Problem statement:** The failure mode is not “missing a feature” — it is **mixed layers** (sacred vs managed vs volatile), **too many mutable surfaces**, and **unbounded install/update flows**. Accidental deletion (e.g. gateway binaries or configs treated like ordinary packages) is a **symptom** of that mixing.

**Direction:** **Python-first MCP organs** and service glue; **TypeScript** where it already dominates (`maat-runtime`, coding-agent, TUI/UI, client hooks). One **control plane** owns install, repair, profile expansion, and enforcement — not ad hoc scripts per machine.

---

## 1. Language bias (lab-appropriate)

| Surface | Bias | Rationale |
|---------|------|-----------|
| **Shared organs** — Maat Memory MCP, Tehuti Guard service, MAAT Sentinel service, Forge worker | **Python** | Aligns with `maatlangchain/`, gitMaat, schedulers, adapters, job loops, fast service glue |
| **User/runtime client** — coding agent, TUI, web, Pi fork | **TypeScript** | Existing `maat-runtime/` investment, extension hooks, UI |
| **Control plane CLI** — `maat setup`, `maat doctor`, `maat repair`, `maat enroll` | **Python** (recommended) | Same process model as MCP workers; single venv/tooling story |

Existing MCP layout in-tree: [`maat-ecosystem/mcp-servers/`](../maat-ecosystem/mcp-servers/) (Ka discovery, Tehuti Core, etc.; lab root `mcp-servers` is a symlink) — extend/evolve here rather than scattering new transports.

---

## 2. Four layers (stop environment leaks)

Every path and artifact is classified **before** any installer or agent acts.

| Layer | What belongs | Mutation rule |
|-------|----------------|-----------------|
| **1 — Sacred** | Constitutional docs, core schemas, Guard doctrine, policy semantics, immune doctrine, memory **schema** contracts, gateway **critical** config, MCP **registry manifests** that define organs | **Deny** unless **human-approved amendment** (change control). Prefer **read-only mounts** where possible; **outside** ordinary installer default write targets. |
| **2 — Managed** | Runtime packages, adapters, app packs, toolkits, extensions, worker modules | **Allow** only through **guarded** installers (staging → verify → activate). |
| **3 — Volatile** | Caches, temp files, logs, build artifacts, model downloads, queue scratch, session scratch | **Allow** rebuild/delete anytime. |
| **4 — User** | Preferences, local profiles, app toggles, quiet hours, notification settings, selected models, **declared** MCP endpoint lists | **Allow** with **validation** (schema + Guard where required). |

**Rule:** Installers and agents **must not** treat sacred paths as managed or volatile.

---

## 3. Gateway and protected services

The **gateway** (and peers: Guard, Sentinel, central memory endpoints) must **not** be ordinary “npm install” casualties.

**Gateway protection rules (normative intent):**

- Gateway **binary/service path** is not writable by unprivileged installers.
- Installs go to **staging** first; **activation** is explicit (symlink, systemd switch, or versioned dir).
- **Rollback** is always possible (previous version retained).
- **Config and secrets** are separated from binaries (`/etc/maat`, `~/.maat`, secrets dir — not mixed into `node_modules`).
- **Uninstall** scripts cannot remove protected paths or stop protected units without policy.
- **Drift detection:** control plane compares running state to **manifest** (see §8).

---

## 4. Lab filesystem skeleton (server example)

One **standard layout** per machine class reduces “where did that go?” failures.

```text
/opt/maat/
├── sacred/           # constitutional docs, schemas, guarded configs (read-only where possible)
├── services/         # memory, guard, sentinel, gateway, tehuti MCP processes
├── runtime/          # maat-runtime / client installs
└── forge/              # forge worker installs

/var/lib/maat/          # durable state (db files if local, queues, identity)
/var/log/maat/          # logs
/etc/maat/              # machine-level config

/home/<user>/.maat/
├── config/             # profile + local overrides
├── apps/               # user-installed packs/toolkits
├── cache/              # safe to delete
└── logs/               # optional user-scoped logs
```

**Workstations** may keep most of this under `~/.maat/` **if** sacred/shared policy still makes **one** canonical place for “what is protected” visible to `maat doctor` (symlinks or documented bind mounts).

---

## 5. Control plane commands

Single entrypoints; **no** giant human-only doc as the primary interface.

**Implementation (this repo):** Python package [`maat-control-plane/`](../maat-control-plane/) — **`maat doctor`** is the machine truth reader (human + `--json`); `setup` / `enroll` / full `repair` remain staged. Install: `pip install -e ./maat-control-plane`.

| Command | Purpose |
|---------|---------|
| **`maat setup`** | Inspect machine (GPU/CPU/RAM/disk), detect Ollama/Postgres/Redis/Node/Python, detect existing MAAT services, detect sacred paths and **conflicts**, emit a **proposed plan** → **operator or agent approval** → apply. |
| **`maat doctor`** | Health + integrity: sacred files intact? gateway present? services reachable? configs valid? memory DB reachable? Sentinel/Guard signals? runtime/forge paths healthy? |
| **`maat repair`** | **Safe** repair: restore missing files from **manifest**, fix symlinks, validate protected paths — **never** overwrite sacred without explicit approval; emit **repair report** JSON. |
| **`maat enroll`** | New machine: assign **machine identity**, register with Sentinel (conceptually), configure **network MCP endpoints**, install **only** roles needed, pull **standard lab profile**. |

These compose the **MAAT Lab Control Plane** — thin orchestration over organs, not a replacement for [`maat-ecosystem/`](../maat-ecosystem/) law.

---

## 6. User intent: `maat profile`

One file expresses **intent**; agents expand to internal configs.

```yaml
machine_role: workstation
user_role: operator
runtime_enabled: true
forge_enabled: true
memory_remote: true
guard_remote: true
sentinel_remote: true
models:
  local:
    - gemma4:e2b
  remote:
    - openclaw
apps:
  - ev-scout
  - business-assistant
quiet_hours:
  enabled: true
  start: "22:00"
```

**Flow:** human sets profile → **agent or tooling expands** → **Guard / Sentinel validate** where applicable → **installer applies** through managed layer only.

---

## 7. Agent enforcement algorithm (machine-side)

Every **requested mutation** runs through this pipeline (mirrors immune doctrine at **ops** layer).

1. **Classify target** — sacred | managed | volatile | user.
2. **Evaluate action** — read | install | update | remove | replace | repair | promote | configure.
3. **Enforce rule** — sacred → deny unless human-approved amendment; managed → guarded installer only; volatile → allow; user → allow with validation.
4. **Emit event** — who, where, what, why, result, severity (same spirit as [`MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) immune events).
5. **Remember outcome** — Maat Memory stores installs, failures, drift, recurring repair lessons (Archivist / gitMaat discipline).

Runtime **TypeScript** hooks in `maat-runtime` remain the **in-session** boundary; the control plane is the **machine-level** boundary.

---

## 8. Protected machine manifest (per host)

Every enrolled machine should carry a small manifest (path e.g. `/etc/maat/machine.yaml` or `~/.maat/config/machine.yaml`):

```yaml
machine_id: workstation-01
role: workstation
sacred_paths:
  - /opt/maat/sacred
protected_services:
  - gateway
  - guard
  - sentinel
managed_services:
  - maat-runtime
  - maat-forge
remote_services:
  - maat-memory
  - tehuti
```

**Installers and agents must obey this** when resolving “can I delete/replace X?”.

---

## 9. Safe package policy (normative)

No install script may, without **explicit human-approved amendment**:

- Delete or replace the **gateway** in protected locations.
- Overwrite **sacred** docs or **constitutional** schemas.
- Remove **protected** services or disable **Guard/Sentinel** monitoring paths.
- Point **immune** or **audit** logging at volatile-only storage without operator consent.

---

## 10. Server vs workstation vs network

| Location | Typical roles |
|----------|----------------|
| **Server** | Maat Memory, Tehuti Guard, MAAT Sentinel, central DBs, central reasoning APIs, heavy Forge workers |
| **Workstation** | `maat-runtime`, local toolkit execution, optional lightweight Forge, local experts, UI/operator flows |
| **Network** | MCP and HTTP service boundaries — Ka discovery [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md), organ ports per `maat-ecosystem/MANIFEST.ka` / live manifest |

---

## 11. Build order (concrete)

**A.** Python MCP services (prioritize): maat-memory MCP surface, Tehuti Guard service, MAAT Sentinel service; Forge worker later.

**B.** One lab installer bundle: `setup` / `doctor` / `repair` / `enroll` (Python CLI).

**C.** Protected manifest + profile schema versioning.

**D.** Package policy checks in CI or `maat doctor` (lint install scripts against forbidden paths).

---

## 12. Relation to existing work

| Artifact | Link |
|----------|------|
| Control plane CLI (Python skeleton) | [`maat-control-plane/README.md`](../maat-control-plane/README.md) |
| Immune runtime hooks (TS) | [`maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md`](../maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md) |
| Forge skeleton | [`maat-forge/README.md`](../maat-forge/README.md) |
| MCP servers | [`maat-ecosystem/mcp-servers/`](../maat-ecosystem/mcp-servers/) |
| gitMaat | [`maatlangchain/maat_memory/`](../maatlangchain/maat_memory/) |

---

## See also

- [`docs/MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md)
- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md)
- [`docs/MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)
- [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)
- [`docs/WORKSPACE-KA-MAP.md`](WORKSPACE-KA-MAP.md)
