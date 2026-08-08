# Two `maat-ecosystem` paths on this machine (read this once)

## What exists on disk

| Path | Role |
|------|------|
| **`/home/suspect/.n8n/maat-ecosystem/`** | **Tehuti Lab monorepo** — includes **`mcp-servers/`**, Ka organs, `MANIFEST.ka`, docs aligned with `docs/LAB-CANONICAL-TREE-AND-STACK.md`. **This is the workspace Cursor/OpenClaw use** when the lab root is `~/.n8n`. |
| **`/home/suspect/maat-ecosystem/`** | **Separate directory** (own `.git`). **Does not contain `mcp-servers/`** in this layout — it is **not** the same tree as the lab copy. `MANIFEST.ka` can **diverge** from the `.n8n` copy. |

They are **different inodes** — not a symlink. You are **not** crazy; there really are two trees.

Both may point at the **same GitHub remote** (`Propershare/maat-ecosystem`) but they are **two working copies** — commits, branches, and **uncommitted edits** can diverge.

## Are we “doing double work”?

**Only if you edit both** or pull one repo into the other path without a merge strategy. One path should be **canonical** for changes; the other should be **read-only archive**, **symlink**, or **deleted** after migration.

## Canonical source of truth (lab operator)

Per root **`AGENTS.md`**: the **lab root is `~/.n8n`**. Treat **`/home/suspect/.n8n/maat-ecosystem/`** as the **live** Ka-body for this machine unless you explicitly decide otherwise.

## What to do next (pick one policy)

1. **Stop maintaining `~/maat-ecosystem`** — use only `~/.n8n/maat-ecosystem`; back up then remove or rename `~/maat-ecosystem` if nothing unique lives there.
2. **Replace with symlink** — `~/maat-ecosystem` → `~/.n8n/maat-ecosystem` — **only if** you do not need two separate git remotes/histories.
3. **Keep two on purpose** — e.g. `~/maat-ecosystem` tracks **public GitHub** minimal umbrella and `~/.n8n` is **full lab** — then **document** which repo gets pushes and never copy-edit the same files in both.

## `mcp-servers` symlink (lab root)

Under **`~/.n8n`**, `mcp-servers` → **`maat-ecosystem/mcp-servers`** (relative). That resolves to **`~/.n8n/maat-ecosystem/mcp-servers`**. There is **no** `mcp-servers` under **`~/maat-ecosystem`** on this host — do not point tools at `~/maat-ecosystem/mcp-servers` expecting MCP code.

## See also

- [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md)
