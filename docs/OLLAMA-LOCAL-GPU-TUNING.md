# Ollama local GPU policy (Tehuti Lab)

**Host class:** Single consumer GPU (e.g. 12 GB VRAM). **Goal:** Keep **small local models** as much as possible on the **GPU**; let preprocessing, orchestration, and non-inference stacks use **CPU**.

## What went wrong before

Setting **`OLLAMA_CONTEXT_LENGTH` very high** (e.g. `64000`) at the **systemd service** level increases **KV cache** reservation. On a 12 GB card, that competes with **weights** and **compute graphs**. Ollama then **offloads more layers to CPU**, which shows up as a **CPU/GPU split** in `ollama ps` and feels like “Ollama is on CPU.”

**Rule:** Default **daemon** context should be **moderate**. Use **larger `num_ctx` only per request** (API/OpenClaw) when a single job truly needs it—not as a global default for every load.

## Current policy (from 2026-04-07)

| Knob | Recommendation | Why |
|------|----------------|-----|
| `OLLAMA_CONTEXT_LENGTH` | **`8192`** or **`16384`** at service level | Enough for agents + tools; frees VRAM for **full GPU** on 4–9B class models. |
| `OLLAMA_NUM_PARALLEL` | **`1`** on a dev workstation | Each parallel slot costs VRAM; `1` = one job can use the card fully. |
| `OLLAMA_HOST` | `0.0.0.0` or `127.0.0.1` | Unchanged; LAN vs local only. |
| `OLLAMA_GPU_OVERHEAD` | Optional; default or **512MiB–1GiB** if desktop GPU sharing | Reserves VRAM for display/other apps; **lower** = more for model, **higher** = fewer OOM surprises. |
| Model choice | **`gemma4:e2b` / `maat-compact`** for volume; **`gemma4:e4b`** when quality wins | Smaller quant fits fully on GPU more often. |
| Huge context | **Per-request** `options.num_ctx` / OpenCode path | Only when needed; not the systemd default. |

**OpenClaw / UI context:** You can still **display** a large **catalog** `contextWindow` for a model; that is **marketing/schema**. **Effective** context loaded in Ollama should follow this doc unless you measure VRAM and intentionally raise the service default.

## systemd drop-in (example)

**Typo trap:** `OLLAMA_NUM_PARALLEL` must be spelled with **`OLLAMA_`** — `OOLAMA_NUM_PARALLEL` is ignored by Ollama.

Do not run a second `ollama serve` in your shell while `ollama.service` is active.

```bash
sudo systemctl edit ollama
```

Example override:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_CONTEXT_LENGTH=16384"
Environment="OLLAMA_NUM_PARALLEL=1"
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Adjust `OLLAMA_CONTEXT_LENGTH` down to **8192** if `ollama ps` still shows heavy CPU share on your main chat model.

## Verify

```bash
ollama ps
nvidia-smi
```

## Regression bundle (Tehuti Lab)

From monorepo root:

```bash
bash scripts/run-tehuti-local-tests.sh
```

Covers Ollama tags, **gemma4:e2b** + **gemma4:e4b** chat + tool calls, and **MaatBench** `contract_integrity` (schema tier; no `maat_core` required).

During generation, **GPU util / memory** should rise; `ollama ps` **GPU** share should dominate for small models once context is sane.

## gitMaat

Log this policy change after you apply the override:

```bash
cd /home/suspect/.n8n
python3 scripts/log-gitmaat-ollama-gpu-policy.py
```

(Edit the script rationale line if your host differs.)

## References

- Ollama environment variables: [Environment variables](https://github.com/ollama/ollama/blob/main/envconfig/config.go) (upstream; names may evolve—confirm on your installed version).
- Workspace override template: [ollama-override-temp.conf](../ollama-override-temp.conf) (keep aligned with this doc).
