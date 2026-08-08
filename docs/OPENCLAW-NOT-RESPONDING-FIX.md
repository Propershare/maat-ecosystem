# OpenClaw "not responding" – what was fixed

## Cause

1. **Huge context** – Webchat and some channels were sending **unlimited** conversation history to Ollama. Sessions that had many timeout/retry turns became huge, so the first token took minutes or hit timeouts.
2. **Default model** – Larger models (e.g. 20B on CPU) are too slow; the 3B model was set as default and preloaded.
3. **Heartbeat loop** – A scheduled **heartbeat** runs every 30 min (default). It sends the same prompt (“Read HEARTBEAT.md… reply HEARTBEAT_OK”) and the agent replies “HEARTBEAT_OK”. So you saw **~30 min delay** and the bot **keeping saying the same thing**. Heartbeat is now disabled in config (`agents.defaults.heartbeat.every: ""`).

## Changes made

### Config (`~/.openclaw/openclaw.json`)

- **Default model**: `ollama/llama3.2:3b` (fast, preloaded with `ollama-warmup.sh`).
- **Telegram**: `channels.telegram.dmHistoryLimit: 10` so Telegram DMs only send the last 10 turns to the model.

### Code (needs rebuild to take effect)

In `openclaw/src/agents/pi-embedded-runner/`:

- **`run/attempt.ts`** and **`compact.ts`**: when the channel doesn’t set a history limit, a **default of 20 turns** is used instead of unlimited. So webchat and other sessions no longer send huge prompts.

To get this behavior you must **rebuild OpenClaw** (from the openclaw repo root, using its normal build process) and restart the gateway.

### One-time warmup

After Ollama (or machine) restarts, preload the default model so the first reply is fast:

```bash
bash /home/suspect/.n8n/scripts/ollama-warmup.sh
```

## If it still doesn’t respond

1. **Restart gateway** after config changes:  
   `systemctl --user restart openclaw-gateway.service`
2. **Start a new chat** in the Control UI (if available) so the session has little or no history.
3. **Check logs**:  
   `journalctl --user -u openclaw-gateway.service -f`  
   Look for "embedded run timeout" or errors when you send a message.
4. **Test Ollama directly**:  
   `curl -s -X POST http://127.0.0.1:11434/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"Hi"}],"max_tokens":20}'`  
   If this fails or is slow, the issue is Ollama, not OpenClaw.
