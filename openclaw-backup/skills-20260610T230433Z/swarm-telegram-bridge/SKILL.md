---
name: swarm-telegram-bridge
description: Route Telegram (or any HTTP client) through gemma4-toolshim swarm — router.route_message(), gitMaat memory_search via maat_bridge (mcpo :8022), RAG maat_knowledge, Ollama reply. Use when wiring Telegram to the swarm bridge or debugging MAAT_MEMORY_MCP / bridge / webhook.
---

# Swarm ↔ Telegram bridge

## What it is

- **Code:** `gemma4-toolshim/swarm/bridge_service.py` (FastAPI).
- **Router:** `router.route_message()` from the same folder.
- **gitMaat HTTP:** `maat_bridge.py` → mcpo on **8022** (`POST /memory_search`, etc.), not legacy `8018` generic memory.
- **RAG:** `MaatRAG` over `maat_knowledge` when the routed expert is `rag-expert` or tool names suggest RAG.

## Run the bridge

From workspace root:

```bash
chmod +x scripts/start_swarm_telegram_bridge.sh
./scripts/start_swarm_telegram_bridge.sh
```

Defaults: `127.0.0.1:18080`. Override with `SWARM_BRIDGE_HOST`, `SWARM_BRIDGE_PORT`.

## Required environment

| Variable | Purpose |
|----------|---------|
| `MAAT_MEMORY_MCP_API_KEY` or `MCPO_API_KEY` | Bearer for mcpo on **8022** (same key as the running `uvx mcpo --api-key ...` for Maat Memory). |
| `PGVECTOR_DB_URL` | RAG (optional if you only want routing + Ollama without vector chunks). |
| `TELEGRAM_BOT_TOKEN` | Only for `/telegram/webhook` (sending replies via Bot API). |

Optional: `MAAT_MEMORY_MCP_BASE` (default `http://127.0.0.1:8022`), `TELEGRAM_WEBHOOK_SECRET` (must match Telegram `secret_token` when set).

## Point Telegram at the bridge

1. **Stop giving this token to OpenClaw** if OpenClaw was handling the same bot: in `~/.openclaw/openclaw.json` set `channels.telegram.enabled` to `false` or remove `botToken` for that account so only one service owns the bot.
2. Expose HTTPS URL to `https://<host>/telegram/webhook` (reverse proxy, tunnel, or LAN with Telegram test hooks is not supported — production webhooks require HTTPS).
3. Register the webhook:

```bash
curl -sS "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://<your-host>/telegram/webhook" \
  -d "secret_token=<same as TELEGRAM_WEBHOOK_SECRET>"
```

4. Start the bridge with `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and mcpo API key in the environment (e.g. systemd `Environment=` lines, not committed files).

## Smoke test (no Telegram)

```bash
curl -sS http://127.0.0.1:18080/health
curl -sS http://127.0.0.1:18080/invoke \
  -H 'Content-Type: application/json' \
  -d '{"message":"search the knowledge base for auth"}'
```

## OpenClaw-only alternative

If the bot stays on **OpenClaw** Gateway, you do not use this webhook path; instead configure the gateway agent with tools/skills that call **`http://127.0.0.1:18080/invoke`** (same JSON) from an allowed exec or HTTP tool policy. This skill documents the **dedicated bridge** path when Telegram should hit swarm routing directly.
