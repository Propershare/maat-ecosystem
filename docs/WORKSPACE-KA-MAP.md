# Tehuti Lab — Workspace Ka map (pivot hygiene)

The **product Ka-body** (organs, `MANIFEST.ka`, bench) lives in:

- **`maat-ecosystem/`** — canonical; read `maat-ecosystem/MANIFEST.ka` and `maat-ecosystem/README.md`.

The **rest of this monorepo** is mapped below to the same nine-organ metaphor so juniors know *where to put new work* and *where to look first*. This is organizational truth, not a requirement to physically rename folders today.

**Product names vs folders:** read [`docs/MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) first — **`maat-runtime/`** (TypeScript Pi fork) is **not** **`maat_core/`** (Python schema locator).

| Ka organ | Role | Primary paths in this workspace |
|----------|------|----------------------------------|
| **Soul** | Identity, law, who we serve | `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `HEARTBEAT.md`, `.cursorrules`, `maat-ecosystem/soul/` |
| **Brain** | Reasoning, models, planning | `openclaw/`, `maatlangchain/`, `maat-framework/`, `maat-runtime/` (TS coding-agent runtime), `hermes-agent/`, `langgraph-agent-demo/`, `maat-ecosystem/brain/` |
| **Memory** | Durable recall, tasks, RAG | `memory-bank/`, `memory/`, `maatlangchain/maat_memory/`, `chroma_db_maat/`, `maat-ecosystem/memory/` |
| **Hands** | Tools, MCP, automation, shims | **`maat-ecosystem/mcp-servers/`** (Ka spine MCPs; lab root `mcp-servers` → symlink), `n8n-mcp/`, `gemma4-toolshim/`, `n8n-workflows/`, `scripts/`, `hooks/`, `maat-ecosystem/hands/` (workflow apps; root `maat-apps/` = duplicate — see [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md)) |
| **Senses** | Inputs, events, webhooks | `n8n-workflows/`, channel configs in `~/.openclaw/openclaw.json`, `maat-ecosystem/senses/` |
| **Voice** | Output, UI, humans | `tehuti-lab-webui/`, `open-webui/`, OpenClaw Control UI, `maat-ecosystem/voice/` |
| **Ka** | Health, healing, pulse | `monitoring/`, `stats/`, `systemd-services/`, fix scripts (`fix-*.sh`), `maat-ecosystem/ka/` |
| **Skeleton** | Schemas, contracts, portability | `openspec/`, `maat-ecosystem/skeleton/`, `maat_core/` (path locator to schemas), provider docs under `openclaw/docs/` |
| **Blood** | Bus, packs, cross-cutting flows | `shared/`, `maat-ecosystem/blood/`, integration JSON at root (prefer moving new assets under `n8n-workflows/` or `docs/` over time) |

## Pivot rules (clean root)

1. **New Maat-facing features** default under `maat-ecosystem/` (correct organ) or the mapped directory above — not ad hoc top-level folders.
2. **Logs and editor debris** → `logs/` or `_quarantine/` (see repo root `_quarantine/README.md`).
3. **Long-form lab strategy** → `docs/` (e.g. `TEHUTI-LAB-MAAT-ECOSYSTEM-PROPOSAL.md`).
4. **Runtime secrets** stay **out of git** (`tehuti-config/secrets/`, `~/.openclaw/credentials/`).

## See also

- `docs/MAAT-PRODUCT-MAP.md` — **canonical** repo/product names (`maat-runtime` vs `maat_core` vs ecosystem)
- `docs/MAAT-IMMUNE-SYSTEM.md` — Guard, Sentinel, Memory, Bench, Forge as the **immune subsystem**
- `docs/MAAT-INITIATION-REPORT.md` — honest problem/solution report, initiation gates, **progress meter**, training evidence checklist (Maat = truth on partial fixes)
- `maat-ecosystem/LAB-WORKSPACE.md` — how this body relates to `~/maat-ecosystem`
- `docs/TEHUTI-LAB-MAAT-ECOSYSTEM-PROPOSAL.md` — full audit and junior runbook
