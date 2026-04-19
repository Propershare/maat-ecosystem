# Tehuti Guard — which repo is which (npm vs lab)

There are **two different products** that share similar names. This doc prevents the wrong `npm install` or `pip install` story.

## 1) `Propershare/tehuti-guard` on GitHub (npm MCP — **standalone repo**)

| | |
|--|--|
| **What** | MCP **security proxy** (fork lineage from ContextGuard): wraps stdio MCP servers, prompt-injection / path / rate limits. |
| **Install** | `npm install -g tehuti-guard` (when published) — see **upstream repo README**, not this monorepo. |
| **Repo** | https://github.com/Propershare/tehuti-guard |
| **In this lab** | The **npm MCP** product is still developed from a **separate clone** of that repo. The lab tree under **`tehuti-guard/`** in **maat-ecosystem** is **not** that npm package — it holds the Python decision API + private TS helpers (see §2 and **Canonical layout** below). |

Use this when you want **Claude / Open WebUI / MCP client** → **wraps** your MCP server command.

---

## 2) This workspace: `tehuti-guard/` at lab root (HTTP decision API + lab helpers)

| Path | What | Publish |
|------|------|---------|
| **`tehuti-guard/guard/`** | **Tehuti Guard v1** — Python HTTP **`POST /decision`** on **:8013**, consumes Sentinel `unified_view`. Package name **`tehuti-guard-api`** in `pyproject.toml`. | **PyPI-style:** `pip install -e ./guard` (local) or build sdist/wheel from `guard/` per `guard/README.md`. |
| **`tehuti-guard/`** (root `package.json`) | **Private** TypeScript helpers (LDAP / three-ring tests). **Not** the npm MCP proxy. | **Do not** publish as `tehuti-guard` on npm — that name is reserved for the GitHub repo. |

**Canonical operator doc for the Python API:** [`tehuti-guard/guard/README.md`](../tehuti-guard/guard/README.md).

### Canonical layout (monorepo vs standalone MCP repo)

**Decision (Option A):** The directory **`tehuti-guard/`** at the **maat-ecosystem / lab root** is **versioned in this monorepo**. It is **not** a nested git checkout of `Propershare/tehuti-guard`. That keeps the Python **`POST /decision`** surface and lab helpers in one place with [`scripts/guard_adapter_e2e_demo.py`](../scripts/guard_adapter_e2e_demo.py) and operator docs.

**Standalone repo** https://github.com/Propershare/tehuti-guard remains the intended home for the **publishable npm MCP proxy** — work there in a **dedicated clone** when shipping that product.

**Backup:** Before removing the nested `.git`, a snapshot was stored under `backups/tehuti-guard-pre-monorepo-*` (bundle + tree tarball + patches). Retain until you no longer need rollback.

---

## 3) Port map (lab)

| Port | Service |
|------|---------|
| **8013** | Tehuti Guard v1 HTTP (Python) — `tehuti-guard-serve` |
| **4242** | maat-sentinel (feeds Guard) |

Discovery lists **`organs.policy`** on **`GET :8010/manifest`** — see [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md).

---

## 4) Publishing checklist

### npm (MCP proxy product)

1. Work in a **clone** of https://github.com/Propershare/tehuti-guard. The **`tehuti-guard/`** tree **inside maat-ecosystem** is the **lab** layout (Python API + helpers), not a substitute for the npm package source — use a separate clone for MCP releases.
2. Follow that repo’s **`package.json`**, `pnpm`/npm scripts, and **GitHub Actions** if any.
3. `npm login` → `npm publish` (or org-scoped publish per `package.json`).

### Python (decision API)

1. `cd tehuti-guard/guard`
2. `pip install build && python -m build`
3. Upload to **PyPI** (or private index) as **`tehuti-guard-api`** — see `pyproject.toml` `[project] name`.

---

## 5) External audit claims vs this workspace

Some third-party audits conflate **GitHub `Propershare/tehuti-guard`** (npm MCP proxy) with **`tehuti-guard/`** here. Quick facts for **this monorepo**:

| Claim | This workspace |
|-------|----------------|
| **`npm test` uses Jest but Jest is missing** | **False for lab root:** [`tehuti-guard/package.json`](../tehuti-guard/package.json) uses **`vitest run`** and lists **`vitest`** in `devDependencies`. Verify the **standalone npm repo** separately if auditing that product. |
| **Package / monorepo naming** | Lab monorepo **`maat-runtime/`** may still show upstream **`pi-monorepo`** in `package.json` until migration — see [`maat-runtime/docs/RENAME-MAP.md`](../maat-runtime/docs/RENAME-MAP.md) if present, or root `maat-runtime/README.md`. |

## See also

- MAAT Audit — Tehuti Guard repo structure repair — [`MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md`](MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md)
- [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) — product names
- [`GITHUB-REPO-MAP.md`](GITHUB-REPO-MAP.md) — federation
