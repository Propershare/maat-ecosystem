# OpenClaw + Ollama (gpt-oss:20b) — Speed optimizations

## What was changed in config

In `~/.openclaw/openclaw.json` for `ollama/gpt-oss:20b`:

| Setting        | Before  | After   | Why |
|----------------|---------|---------|-----|
| `contextWindow`| 131072  | 32768   | Smaller context = less work per request, faster first token. |
| `maxTokens`    | 16384   | 4096    | Shorter max reply = faster single turn; still plenty for most replies. |

Restart the OpenClaw gateway after any config change.

---

## 1. Ollama service (keep model loaded, more threads)

So the model stays in memory and doesn’t reload every time, and (on CPU) uses more cores:

```bash
sudo systemctl edit ollama
```

Add under `[Service]`:

```ini
[Service]
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_NUM_THREAD=16"
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

- `OLLAMA_KEEP_ALIVE=24h` — keeps `gpt-oss:20b` loaded for 24h after last use.
- `OLLAMA_NUM_THREAD=16` — use up to 16 CPU threads (you have 24 cores); tune down if the system gets sluggish.

---

## 2. GPU (fix driver mismatch for big speedup)

You had: `Failed to initialize NVML: Driver/library version mismatch`. Until that’s fixed, Ollama may be using CPU only, which is slow for a 20B model.

- Reboot after a driver upgrade, or
- Reinstall the NVIDIA driver to match the loaded kernel module (see your distro’s docs).
- Then confirm: `nvidia-smi` and that Ollama uses the GPU (check logs: `journalctl -u ollama -f`).

---

## 3. Optional: smaller context if 32k is still slow

If it’s still too slow, you can lower context further in `~/.openclaw/openclaw.json` under `models.providers.ollama.models` for `gpt-oss:20b`:

- `contextWindow`: try `16384` or `8192`
- `maxTokens`: keep at `4096` or set to `2048`

Restart the gateway after changes.

---

## 4. Optional: try a smaller/faster model for testing

For quicker replies during setup or testing, you can switch the default model to something smaller, e.g.:

```json
"model": { "primary": "ollama/llama3.2:3b" }
```

Then switch back to `ollama/gpt-oss:20b` when you want full quality.

---

## Summary

- Config: **context 32k, max tokens 4k** (already applied).
- Ollama: **keep-alive + num threads** (edit service as above).
- GPU: **fix driver mismatch** for best speed.
- Restart **gateway** after config changes, **ollama** after env changes.
