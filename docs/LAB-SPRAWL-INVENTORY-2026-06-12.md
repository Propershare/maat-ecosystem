# Tehuti Lab Sprawl Inventory - 2026-06-12

Purpose: turn the "mess" feeling into an operator map. This is not a deletion plan. It is an evidence-based inventory of what is active, what is canonical, what overlaps, and what can later be archived after confirmation.

## Summary

The lab is not conceptually confused. The sprawl is operational:

- Multiple user-facing agent gateways are active at the same time.
- The workspace root mixes canonical source, active runtime state, backups, old clones, model/data corpora, and generated artifacts.
- Some names overlap (`maat-core`, `maat_core`, Tehuti Core, Maat Memory, MaatLangChain, Maat Runtime).
- Several old or duplicate OpenClaw trees are still present after update/repair work.
- The core spine is real and working: OpenClaw, Ka discovery/MCP organs, gitMaat, Raku/FiveM, Hermes, n8n, nginx, Ollama brokers.

## Active Runtime Surfaces

| Surface | Status / Evidence | Role | Canonical Source / Config | Notes |
|---|---:|---|---|---|
| OpenClaw gateway | Running on `:18790`; `/health` returns 200 | Primary lab gateway, Telegram, tools, workspace agent surface | Source `openclaw/`; config `~/.openclaw/openclaw.json`; unit `~/.config/systemd/user/openclaw-gateway.service` | Updated to `2026.6.2`; service description still says old version but env label is `2026.6.2`. Current model config is `ollama-cloud/minimax-m3:cloud` with Anthropic/OpenAI fallbacks. |
| Raku Discord bot | `raku-bot.service`; process `staydangerous-fivem-skill/discord_bot.py` | StayDangerousRP Discord bot, FiveM admin/lore/content slash commands | Source `staydangerous-fivem-skill/`; config `staydangerous-fivem-skill/.env`; identity `BOT_IDENTITY.md` | This is the real Discord bot. It is not the OpenClaw Discord skill. |
| Raku companion runtime | `app.py` on `127.0.0.1:8765`, health 200 | In-game/NPC AI companion brain for FiveM | Source `raku-companion-runtime/` | Recent gitMaat work added NPC lore, voice archetypes, STT flow. |
| Raku STT | `raku-stt.service`, `127.0.0.1:8766`, health 200 | Speech-to-text for AI companion | Source `raku-companion-runtime/stt_server.py` | CPU `small.en` currently per unit. |
| Raku TTS | `raku-tts.service`, `127.0.0.1:8767`, health 200 | Text-to-speech for AI companion | Source `raku-companion-runtime/tts_server.py` | Active companion voice service. |
| Hermes gateway | `hermes-datadrive-gateway.service` | Separate Hermes messaging gateway, WhatsApp bridge | Installed under `~/.hermes/hermes-agent`; home `/mnt/data_drive/hermes` | Separate from OpenClaw. Its active scope should be kept distinct. |
| Hermes dashboard | `hermes-dashboard.service`, configured for `127.0.0.1:9119` | Hermes TUI/dashboard | `~/.config/systemd/user/hermes-dashboard.service` | Depends on Hermes gateway. |
| Hermes Ollama | `hermes-ollama.service`, configured `127.0.0.1:11435` | Separate local Ollama for Hermes | `/home/suspect/.local/ollama-0.30.6/bin/ollama` | Keep separate from OpenClaw's `11434` broker. |
| Ollama broker | Listener on `*:11434` | Ollama client/broker for cloud/local models | `/home/suspect/.local/ollama-0.20.0/bin/ollama serve` | OpenClaw model provider uses `127.0.0.1:11434/v1`; `minimax-m3:cloud` is cloud-backed. |
| Ka discovery | Running on `:8010`, health 200 | Manifest/body discovery | `maat-ecosystem/mcp-servers/ka-discovery/` via root symlink `mcp-servers/` | Canonical spine discovery service. |
| Tehuti Core MCP/HTTP | Running on `:8014`, docs 200 | Brain/core coordination surface | `maat-ecosystem/mcp-servers/tehuti-core/` | Wrapped by `mcpo`. |
| Filesystem MCP | Running on `:8016` | Filesystem tool surface for lab root | `@modelcontextprotocol/server-filesystem /home/suspect/.n8n` | Exposes broad lab root; treat as high trust. |
| Postgres MCP | Running on `:8017` | DB tool surface | `@modelcontextprotocol/server-postgres` | Observed URL points at `jarvis`, while gitMaat uses `maat_memory`; verify before relying on it. |
| Pipeline MCP/API | Running on `:8020` | MaatLangChain pipeline/RAG | `maat-ecosystem/mcp-servers/maatlangchain-pipeline/` | Active. |
| Maat Memory MCP | Running on `:8022`, docs 200 | gitMaat/Maat Memory tool surface | `maat-ecosystem/mcp-servers/maat-memory/` | Canonical memory MCP. |
| n8n | Running on `:5678` | Workflow automation | global n8n install + workspace data | Active, separate from OpenClaw. |
| FiveM server / txAdmin | Ports `30120` and `40120` listening | StayDangerousRP server and txAdmin | Server tree symlink `staydangerous -> /mnt/ai_backup/staydangerous1` | Sacred production surface. Do not "clean" without backup and explicit operator decision. |
| nginx | Master + workers running | Local web serving/reverse proxy | `/etc/nginx` plus served static roots | `maatecosystem.com` local hosting work exists; Replit may supersede domain path. |

## Canonical Ownership Map

| Thing | Canonical Path | Owner Role | Notes |
|---|---|---|---|
| Lab root / operator workspace | `/home/suspect/.n8n` | Tehuti Lab workspace | One large workspace, not one clean package. Cursor and OpenClaw should point here. |
| Ka reference body | `maat-ecosystem/` | Canonical Maat/Ka body | Contains `MANIFEST.ka`, organ folders, `site/`, `maatbench/`, `mcp-servers/`. |
| MCP spine | `maat-ecosystem/mcp-servers/` | Canonical MCP server code | Root `mcp-servers/` is a symlink here. Do not break it. |
| gitMaat / Maat Memory Python | `maatlangchain/maat_memory/` | Coordination database layer | Uses Postgres `maat_memory` via `PGVECTOR_DB_URL`. |
| OpenClaw gateway | `openclaw/` | Primary operator gateway | Current live build. Custom skills/presets copied into this tree. |
| Raku bot / FiveM Discord | `staydangerous-fivem-skill/` | Discord + FiveM ops bot | Standalone Python bot. Not the OpenClaw Discord skill. |
| FiveM server tree | `/mnt/ai_backup/staydangerous1` via `staydangerous` symlink | Production game server | Treat as production, not workspace cruft. |
| Raku companion runtime | `raku-companion-runtime/` | In-game AI NPC runtime | Active via systemd and recent gitMaat work. |
| Hermes agent source | `hermes-agent/` and `~/.hermes/hermes-agent` | Separate Hermes product/runtime | Repo source under lab root; active service uses home/venv plus `/mnt/data_drive/hermes`. |
| Tehuti Guard | `tehuti-guard/guard/` | Policy API | Lab Python API on `:8013` when active; separate from npm MCP product. |
| Maat Runtime | `maat-runtime/` | TS coding-agent runtime | Separate GitHub product `Propershare/Maat-runtime`. |
| Maat Control Plane | `maat-control-plane/` | `maat doctor` CLI | Setup/enroll/repair still partial per docs. |

## Known Duplication / Drift

| Area | Evidence | Risk | Recommendation |
|---|---|---|---|
| OpenClaw old trees | `openclaw-old-20260610T232242Z` (~3.8G), `openclaw-backup/`, current `openclaw/` | Confusion over which copy is live; disk cost | Keep old tree until gateway stable for a few days, then archive/compress or remove only after explicit approval. |
| OpenClaw integration tree | `openclaw-integration/` (~2.2G), remote also `openclaw/openclaw`, behind upstream | Duplicate of current OpenClaw unless it has unique experiments | Decide whether it is an experiment, migration source, or archive candidate. |
| Large old backups | `.reorg-backup-20251217-222805` (~21G), `tehuti-lab-webui-venv.backup.*` (~17.5G combined) | Major disk use; stale Python envs | Move to external/archive storage or delete after a manifest confirms no unique source files inside. |
| Workflow apps | Docs already flag `maat-apps/` vs `maat-ecosystem/hands/apps/` | Agents may edit the wrong app copy | Treat `maat-ecosystem/hands/apps/` as canonical for new body apps; migrate root `maat-apps/` when touched. |
| Model brokers | Ollama on `11434`, Hermes Ollama on `11435`, Raku runtime points at `11434` | Local/cloud model confusion | Document model ownership: OpenClaw uses Ollama Cloud via `11434`; Hermes owns `11435`; Raku companion may use local `11434` model for NPCs. |
| Discord surfaces | Raku Discord bot active; OpenClaw Discord skill exists but needs setup; Hermes supports Discord generally | Repeated mistaken attempts to configure the wrong Discord path | Canonical Discord/FiveM bot is Raku. Leave OpenClaw Discord disabled unless deliberately migrating channels. |
| Maat naming | `maat-ecosystem`, `maat-runtime`, `maat_core`, `maat-core`, Tehuti Core, Maat Memory | Easy to confuse code repo, service, schema module, and memory DB | Keep `docs/MAAT-PRODUCT-MAP.md` as the naming authority; update stale labels when touched. |
| Root Git scope | Git root is `/home/suspect/.n8n` with remote `Propershare/maat-ecosystem`; many unrelated untracked trees live inside | Push-safety risk: accidental secrets/data/stale backups | Before commits, always run staged-file safety checks and avoid broad `git add .`. |

## Recommended Boundaries

1. **OpenClaw owns Telegram and lab operator commands.**
   - Workspace: `/home/suspect/.n8n`
   - Channel: Telegram
   - Model: cloud Ollama provider with subscription fallbacks
   - Tools: lab root, gitMaat/MCP, FiveM skill if called from operator context

2. **Raku owns Discord + StayDangerousRP public/community operations.**
   - Source: `staydangerous-fivem-skill/`
   - Channel: Discord slash commands
   - Reach: FiveM txAdmin, server logs, lore/content
   - Boundary: do not replace this with OpenClaw Discord unless migration is explicit.

3. **Raku companion owns in-game NPC interaction.**
   - Source: `raku-companion-runtime/`
   - Ports: `8765`, `8766`, `8767`
   - Reach: FiveM resource `sd-ai-companion`, lore/personality data

4. **Hermes owns WhatsApp / Hermes-specific experiments.**
   - Home: `/mnt/data_drive/hermes`
   - Gateway: `hermes-datadrive-gateway.service`
   - Boundary: do not blur with OpenClaw unless intentionally migrating.

5. **maat-ecosystem owns the Ka reference body and MCP spine.**
   - Do not scatter new organ code into root unless docs say it is a sibling product.
   - `mcp-servers/` root symlink is compatibility only.

## Cleanup Order

No deletes should happen until an archive manifest exists. Suggested order:

1. **Write an archive manifest first.**
   - List path, size, reason, last modified, whether it has secrets, rollback value.
   - Start with `openclaw-old-*`, `.reorg-backup-*`, `tehuti-lab-webui-venv.backup.*`.

2. **Tag active vs inactive in docs.**
   - Update the canonical tree docs with a short "Active runtime surfaces" table.
   - Add "do not use" notes to duplicate areas if they remain.

3. **Stabilize OpenClaw config truth.**
   - Confirm current `~/.openclaw/openclaw.json` stays on `ollama-cloud/minimax-m3:cloud`.
   - Confirm service description line is not misleading (`Description=OpenClaw Gateway (v2026.2.3)` is stale even though env label is `2026.6.2`).

4. **Decide fate of `openclaw-integration/`.**
   - If no unique code, archive it.
   - If it is a staging branch, document that.

5. **Consolidate app manifests only when touched.**
   - Do not do a mass migration of `maat-apps/` yet.
   - Use `maat-ecosystem/hands/apps/` as canonical going forward.

6. **Keep FiveM sacred.**
   - `/mnt/ai_backup/staydangerous1` is production.
   - Any cleanup or edit there requires explicit operator intent and backups.

## Runtime Gaps (2026-06-12 process pass)

Also active but easy to miss:

- `ka-education-backend` under `/mnt/data_drive/hermes/` (`.env` reports `API_PORT=3007`)
- ComfyUI MCP on `:8019` (outside lab root)
- Memory KV MCP on `:8018` (not gitMaat)
- `maat-sentinel` swarm daemon (`gemma4-toolshim/swarm/sentinel_daemon.py`)

Not observed running in the same pass (have service/docs, no matching process):

- Tehuti Guard `:8013`
- MAAT Gateway HTTP `:8040`

Watch items:

- Hermes WhatsApp bridge binds `:3001`; Ka education backend default is also `3001` in some docs - confirm no port collision in practice.
- Postgres MCP `:8017` observed against `jarvis` DB, not `maat_memory`.
- Multiple `mcpo` wrappers and API keys visible in process args - treat as secrets-in-process, not for logs/chat.
- Raku companion runtime model in the live process may differ from the systemd unit default - verify before changing either.

## Immediate Action Items

- Create `docs/LAB-ARCHIVE-MANIFEST.md` before removing anything.
- Fix stale OpenClaw service description when convenient.
- Add a short note in `docs/LAB-CANONICAL-TREE-AND-STACK.md`: "Raku is canonical Discord/FiveM bot; OpenClaw Discord skill is not configured."
- Decide whether `openclaw-integration/` is still needed.
- Decide whether old backups can move to external/archive storage.
- Verify Postgres MCP `:8017` target DB and Hermes `:3001` vs Ka education port ownership.

## Do Not Touch Without Explicit Approval

- `/mnt/ai_backup/staydangerous1`
- `staydangerous-fivem-skill/.env`
- `~/.openclaw/openclaw.json`
- `.env` / `PGVECTOR_DB_URL`
- Postgres data / gitMaat DB
- n8n workflows and credentials
- root `.git` history / broad `git add .`

