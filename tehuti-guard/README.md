# `tehuti-guard/` in Tehuti Lab (this monorepo)

**This folder is not the same as the standalone npm package** at [github.com/Propershare/tehuti-guard](https://github.com/Propershare/tehuti-guard) (MCP security proxy / ContextGuard fork).

## What lives here

| Part | Role |
|------|------|
| **`guard/`** | **Tehuti Guard v1** — Python HTTP API (`POST /decision`, `GET /health`) on **:**`8013`. PyPI name **`tehuti-guard-api`** in `guard/pyproject.toml`. **This is the policy service** referenced in `MANIFEST.ka` and Ka discovery `organs.policy`. |
| **Root `package.json`** | **Private** lab package **`@tehuti-lab/guard-ldap-helpers`** — TypeScript helpers / tests. **Do not** publish as `tehuti-guard` on npm (that name belongs to the GitHub MCP product). |

## Docs

- **Python API (operators):** [`guard/README.md`](guard/README.md)
- **Which product is which (npm vs PyPI):** [`docs/TEHUTI-GUARD-PRODUCTS.md`](../docs/TEHUTI-GUARD-PRODUCTS.md)

## npm (MCP proxy) — where to publish

To publish or develop the **MCP wrapper** (`tehuti-guard` CLI for `stdio` MCP), use the **GitHub repo clone**, not this folder’s root `package.json`.
