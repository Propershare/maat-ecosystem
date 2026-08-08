# KA2 Research — OpenClaw agent preset (Tehuti Lab)

This folder ships a **merge-ready `agents.list[]` fragment** and a **small workspace** so the gateway can run a **UKMT KA2**-aligned research agent with **web + coding** tools.

## Workspace layout (`ka2-research-workspace/`)

| File / link | Purpose |
|-------------|---------|
| `SOUL.md` | Symlink → `data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md` (canonical KA2 prompt) |
| `AGENTS.md` | Symlink → lab root `AGENTS.md` |
| `lab/` | Symlink → lab repo root — **use `lab/` paths** when reading the monorepo with file tools |
| `TOOLS.md` | Tool and output discipline for this profile |
| `HEARTBEAT.md` | gitMaat-oriented heartbeat |

## Merge into `~/.openclaw/openclaw.json`

1. Back up your config.
2. Add **one object** from [`openclaw.agents.ka2-research.json5`](openclaw.agents.ka2-research.json5) into `agents.list` (keep your existing `main` or other agents).
3. Set **`model.primary`** (and fallbacks) to Ollama models you actually run (example shows `ollama/...` — adjust).
4. **Route** a channel to `ka2-research` via your existing `bindings` / routing rules (Telegram, etc.) — see OpenClaw [configuration](https://github.com/openclaw/openclaw) docs for your version.
5. Restart the gateway.

Paths in this repo use the absolute lab root **`/home/suspect/.n8n`** — change if your clone lives elsewhere.

## Test after merge

1. **`openclaw agents list`** — you should see **`main` (default)** and **`ka2-research`** with the KA2 workspace path.
2. **Restart the gateway** so it reloads `~/.openclaw/openclaw.json`.
3. **Control UI** (`http://127.0.0.1:18790` or your gateway port) — pick agent **`ka2-research`** and send a message (WebChat / connected channel).
4. **Telegram** still routes to **`main`** unless you add a top-level **`bindings`** entry (see OpenClaw **`docs/gateway/configuration.md`** § multi-agent routing) mapping your **`peer`** to **`ka2-research`**.

**Sub-agents (`sessions_spawn`):** To let **`main`** and **`ka2-research`** spawn each other (or pass `agentId` on `sessions_spawn`), each needs **`subagents.allowAgents`** (e.g. `["*", "main", "ka2-research"]`). The **`main`** entry must include this too—not only the KA2 fragment. Optional: **`agents.defaults.subagents.maxConcurrent`** (e.g. `8`). Restart the gateway after edits.

## See also

- [`docs/KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md`](../../../docs/KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md)
