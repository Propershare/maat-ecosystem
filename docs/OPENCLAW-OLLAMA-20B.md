# OpenClaw + Ollama: Using gpt-oss:20b

## Why the 20B model "doesn't respond"

- **gpt-oss:20b** runs on CPU (~12.8 GiB RAM). It can take **minutes** to produce the first token and often hits **Ollama’s 5‑minute request timeout**, so you see no reply or errors.
- The default OpenClaw model was switched to **qwen3:latest** so chat stays responsive.

## If you want to use 20B as default again

1. **Raise Ollama’s timeout** (run once):
   ```bash
   sudo bash /home/suspect/.n8n/scripts/ollama-increase-timeout.sh
   ```
   This sets `OLLAMA_REQUEST_TIMEOUT=900` and `OLLAMA_KEEP_ALIVE=24h`.

2. **Set 20B as primary** in `~/.openclaw/openclaw.json`:
   ```json
   "agents": {
     "defaults": {
       "model": { "primary": "ollama/gpt-oss:20b" },
       "timeoutSeconds": 900
     }
   }
   ```

3. **Restart OpenClaw**:
   ```bash
   systemctl --user restart openclaw-gateway.service
   ```

Expect the first reply to take several minutes when using 20B on CPU.

## Using 20B only sometimes

Keep the default as a faster model (e.g. qwen3:latest). In chat, switch to 20B only when you need it (e.g. via the model selector in the Control UI, or your client’s model parameter).
