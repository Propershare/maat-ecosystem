# Lab training pipeline + Gemma 4 (E4B family)

**Purpose:** Single place that says **what pipeline already exists** in Tehuti Lab and **how Gemma 4 / E4B** fits (from current public docs — verify versions before training runs).

---

## 1. What you already have (this repo)

| Asset | Location | Role |
|--------|-----------|------|
| **Gemma4 tool shim + capture + finetune** | `gemma4-toolshim/` | HTTP proxy (**:11435**) so OpenAI-style `tools` work with Gemma via Ollama; **`training_data/captures.jsonl`** for live traces; **`generate_training.py`** synthetic; **`finetune.py`** Unsloth LoRA → GGUF/Ollama path. Expert routing config references **`gemma4:e4b`** in `swarm/expert_config.py`. |
| **MCP tool corpus for SFT** | `training/` | README + **`examples/*.jsonl`** (tool-calling, multi-tool, errors, Maat-flavored); **`schemas/`** (104-tool index); **`mcp-servers/*/openapi.json`** copies — built for Unsloth-style JSONL. |
| **Historical finetunes** | `fine-tuned-models/` | Prior **Llama 3.1 8B** Maat adapters, merged weights, Modelfiles, combined JSONL — proves the lab **has** run LoRA → merge → Ollama before. |
| **Framework sketch** | `maat-framework/` | `maat learn` / docs describe log → LoRA pairs (`docs/learning.md`) — **organize** with the real runners in `gemma4-toolshim` + `training/`. |
| **Initiation / evidence** | `docs/MAAT-INITIATION-REPORT.md` | Calls out synthetic + shim captures + finetune; notes **HF/Unsloth base ID** may lag new Gemma drops — **still the right warning for Gemma 4**. |
| **Ecosystem narrative** | `docs/TEHUTI-LAB-MAAT-ECOSYSTEM-PROPOSAL.md` | Describes shim + training path. |

**Gap (explicit in code):** `gemma4-toolshim/finetune.py` still defaults to **`unsloth/gemma-3-8b-it`** with **`SWAP_FOR_GEMMA4`** comments. Ollama can run **`gemma4:e4b`** for inference today; **training** must wait until **Unsloth + transformers** support the Gemma 4 checkpoint you pick (see §3).

---

## 2. Gemma 4 family — what public sources say (Apr 2026)

*Verify tool versions locally; this section is a map to official material, not a substitute for your GPU smoke test.*

| Model | Approx. role | Notes (high level) |
|--------|----------------|---------------------|
| **Gemma 4 E2B** | Edge / tightest RAM | “Effective” ~**2B** active params during inference (stored total higher; MoE-style efficiency in the family narrative). |
| **Gemma 4 E4B** | Edge / flagship phone / Pi-class | “Effective” ~**4.5B** active; **multimodal** (text + image; **audio** called out for small edge models in Google’s blog/card narrative). **Long context** quoted as **128K** for E2B/E4B in the developer model card table. |
| **Gemma 4 26B (A4B MoE)** | Workstation / IDE agents | MoE; strong rankings in Google’s public benchmark tables vs larger opens. |
| **Gemma 4 31B** | Dense flagship open | Largest in the family in public materials. |

**License:** Apache 2.0 (commercial use narrative on Google’s pages).

**Why E4B matches your lab:** You already standardized on **`gemma4:e4b`** in OpenClaw and the shim — **same lane** as “expert task employee on device or small server” once LoRA + quant paths are wired.

**Official entry points (read these, don’t trust third-party blogs alone):**

- Launch / overview: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/  
- Model card: https://ai.google.dev/gemma/docs/core/model_card_4  
- DeepMind hub: https://deepmind.google/models/gemma/gemma-4/  

**HF-style IDs** (from Google’s developer docs examples): e.g. instruction-tuned **`google/gemma-4-E4B-it`**, **`google/gemma-4-E2B-it`** — confirm exact strings on Hugging Face before pinning in `finetune.py`.

---

## 3. Gemma4 training support status (verified 2026-04-17)

**Upstream:** Gemma4 support is now available in current training stacks (Transformers 5.5.x + current Unsloth).

**Locally verified in isolated venv (`.venvs/gemma4-train`):**

- `transformers==5.5.0`
- `unsloth==2026.4.6`
- `trl==0.24.0`
- `peft==0.19.1`
- `from transformers import Gemma4Config` passes
- `AutoConfig.from_pretrained("google/gemma-4-e2b-it")` reports `model_type=gemma4`
- `python gemma4-toolshim/finetune.py --model google/gemma-4-e2b-it --max-steps 1 --skip-gguf` reaches model load / LoRA setup; current stop reason is missing local training JSONL (not architecture support)

**Quick support check:**

```bash
source /home/suspect/.n8n/.venvs/gemma4-train/bin/activate
python -c "import unsloth, transformers; from transformers import Gemma4Config, AutoConfig; print(unsloth.__version__, transformers.__version__); print(AutoConfig.from_pretrained('google/gemma-4-e2b-it').model_type)"
```

**Current `tehuti-lab-webui-venv` caveat:** this venv is root-owned on disk, so package upgrades fail with permission errors. Fix ownership (or recreate that venv) before expecting in-place upgrades there.

---

## 4. What to do next (lab + Maat)

1. **Inference path (already):** Ollama + **`gemma4:e4b`** + **`gemma4-toolshim`** for clients that expect OpenAI `tool_calls`.  
2. **Training path:** When Unsloth documents **Gemma 4** support for your chosen size, set **`DEFAULT_MODEL`** in `gemma4-toolshim/finetune.py` (replace `SWAP_FOR_GEMMA4`) and re-run a **short LoRA smoke** on `training/examples/*.jsonl` merged with **`captures.jsonl`**.  
3. **Expert library:** For each task family, version **JSONL** + **Ollama tag** + optional row in gitMaat (“task → model”).  
4. **Mobile:** E4B/E2B are the right **candidates** for on-device or edge; export path is still **quantized GGUF / vendor runtime** (LiteRT/MediaPipe/etc.) per Google’s edge story — **separate** from Ollama-on-server.

---

## 5. One-sentence alignment

**Maat** = spine (tasks, memory, MCP). **Gemma 4 E4B** = a strong **default expert substrate** for edge + lab; **this repo already owns capture + Unsloth script + MCP JSONL** — finish the **Gemma 4 training target** when the stack catches up, then register experts like any other Ollama model.

**Last updated:** 2026-04-17 (curated from workspace verification + public Gemma 4 pages).
