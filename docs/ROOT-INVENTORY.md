# Workspace root inventory (non-destructive audit)

**Purpose:** Reduce “bleeding repos” confusion at `~/.n8n` without deleting the spine. This file classifies **top-level** entries so operators know what is **core Maat**, **product**, **infrastructure**, or **archive**.

**Truth on disk:** run periodically:

```bash
ls -1 ~/.n8n | sort | wc -l
ls -1 ~/.n8n | sort
```

**Curated narrative:** [`docs/TEHUTI-LAB-TREE.md`](TEHUTI-LAB-TREE.md) (ASCII + Mermaid) — update that file when large moves happen. **Canonical tree + stack:** [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md).

## Classification

| Class | Meaning | Examples |
|-------|---------|----------|
| **Spine** | Keep; agents and MCP depend on these | `maat-ecosystem/` (includes **`maat-ecosystem/mcp-servers/`** — runnable MCP tree; root `mcp-servers` is a symlink), `maatlangchain/`, `docs/`, `systemd-services/` |
| **Duplicate apps tree** | Know the difference | Root **`maat-apps/`** vs **`maat-ecosystem/hands/apps/`** — see [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md) §4 |
| **Product** | Named sellable or user-facing surfaces | `maat-runtime/` (GitHub `Propershare/Maat-runtime`), `maat-framework/`, `openclaw/`, `tehuti-lab-webui/` |
| **Locator / small lib** | Tiny helpers | `maat_core/` (Python schema paths) |
| **Data / vectors** | Large or machine-local | `chroma_db_maat/`, `.maat_memory/`, `models/`, `fine-tuned-models/` |
| **Archive / quarantine** | Keep but don’t confuse with active products | `backups/`, `_quarantine/`, `*.rar`, `staydangerous/` (symlink), `.reorg-backup-*` |
| **Experiments** | Demos and one-offs | `langgraph-agent-demo/`, `gemma4-toolshim/`, `training/` |

## Pivot rules (reminder)

From [`docs/WORKSPACE-KA-MAP.md`](WORKSPACE-KA-MAP.md):

1. New Maat-facing features default under **`maat-ecosystem/`** (correct organ) or the mapped Ka paths — not ad hoc new top-level folders without a product decision.
2. Logs and editor debris → `logs/` or `_quarantine/`.
3. Long-form strategy → `docs/`.
4. Secrets stay out of git.

## Product name map

See **[`docs/MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)** — especially **`maat-runtime/`** vs **`maat_core/`**.
