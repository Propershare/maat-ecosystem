# Maat initiation — problem / solution report and progress meter

**Principle:** If a fix is not complete, the document says so. **Maat is truth:** overclaiming erodes trust and governance.

This report is the **initiation layer** for Tehuti Lab: what broke, what we changed, what remains open, and what evidence you must collect to **raise** the meter and to **train** the stack.

---

## 1. Executive truth (not marketing)

| Claim | True today? | Caveat |
|--------|-------------|--------|
| Ollama uses the GPU for local Gemma | **Usually yes** after tuning | Service-wide **huge context** still steals VRAM (KV cache); watch `ollama ps` and `nvidia-smi`. |
| Local models follow instructions + tools | **Basics verified** | One-line + single **bash** tool test only — **not** full agent stress or multi-step Maat law. |
| MaatBench “passed” | **Partial** | **`contract_integrity` only** (11 schema tests). Full bench (policy, memory, events, portability, learning) needs **`maat_core`** and running organs. |
| Training pipeline exists | **Yes** | Synthetic JSONL + shim **captures** + `finetune.py`; **base model ID** for Gemma 4 in Unsloth may lag Hugging Face. |
| gitMaat always logged | **Partial** | JSON fallback works; PostgreSQL path needs valid **`PGVECTOR_DB_URL`**. |

**Outcome is always Maat:** partial success is documented as partial — not as “green everywhere.”

---

## 2. Problems observed and fixes applied

### 2.1 Ollama felt “CPU-bound” / GPU underused

| Problem | Cause | Fix | Residual risk |
|---------|--------|-----|----------------|
| High CPU share in `ollama ps` | **`OLLAMA_CONTEXT_LENGTH=64000`** (or similar) inflated KV cache; weights spill to CPU. | Lower service default (**8k–16k**), **`OLLAMA_NUM_PARALLEL=1`**, doc in [`OLLAMA-LOCAL-GPU-TUNING.md`](OLLAMA-LOCAL-GPU-TUNING.md); template [`ollama-override-temp.conf`](../ollama-override-temp.conf). | Very long single requests still need **`num_ctx`** per call — may still push offload. |
| systemd typo | **`OOLAMA_NUM_PARALLEL`** (wrong spelling). | Correct to **`OLLAMA_NUM_PARALLEL`**. | Other typos in drop-ins bypass silently — **review env keys** after edits. |
| Second `ollama serve` failed | Port **11434** already bound by **`ollama.service`**. | Use **`systemctl restart ollama`**, not duplicate process. | N/A |

### 2.2 OpenClaw default model burned cloud credits

| Problem | Cause | Fix | Residual risk |
|---------|--------|-----|----------------|
| Opus / Codex spend | **`agents.defaults.model.primary`** pointed at paid API. | Set **`ollama/gemma4:e4b`**, local fallbacks, fix Ollama **`apiKey`**. | Per-session UI can still pick cloud — **policy** is separate from defaults. |

### 2.3 Tests and bench

| Problem | Cause | Fix | Residual risk |
|---------|--------|-----|----------------|
| `test_gemma4_e2b_local.py` flaky “empty content” | **`gemma4:e2b`** sometimes puts text in **`thinking`**, **`content`** empty; **`num_predict`** too low. | Accept **content OR thinking**; raise **`num_predict`**; env **`OLLAMA_TEST_MODEL`**. | Other models may need different heuristics. |
| `python3 -m maatbench.run` import error | Eager import of **`maat_core`**. | **Lazy imports** in [`maat-ecosystem/maatbench/run.py`](../maat-ecosystem/maatbench/run.py); **`--category contract_integrity`** runs without **`maat_core`**. | Full categories still need **`maat_core`**. |
| Schema path missing | Runner expected **`maat-core/schemas`**. | Prefer **[`skeleton/schemas`](../maat-ecosystem/skeleton/schemas)** in [`schema_runner.py`](../maat-ecosystem/maatbench/runners/schema_runner.py). | N/A |

### 2.4 Ka UI / ecosystem messaging

| Problem | Cause | Fix | Residual risk |
|---------|--------|-----|----------------|
| Story vs code disconnected | Replit landing lacked “reference body” strip. | [`UI-MAAT-ECOSYSTEM-STRIP.md`](../maat-ecosystem/docs/UI-MAAT-ECOSYSTEM-STRIP.md), `site/index.html` **`#ecosystem`**, **§3g** in [`REPLIT-CONTINUE.md`](../maat-ecosystem/docs/REPLIT-CONTINUE.md). | Public URLs still placeholders until GitHub/forge. |

---

## 3. Initiation layer — definition

**Initiation** = mandatory gates before an operator trusts this node for Maat-aligned local AI.

**Minimum bar (automated):**

```bash
bash scripts/run-tehuti-local-tests.sh
```

Includes: Ollama tags, **gemma4:e2b** + **gemma4:e4b** (chat + tool call), **MaatBench `contract_integrity`**.

**Extended bar (manual / future automation):**

- Full **MaatBench** when **`maat_core`** is installed and organs are up.
- **MCP health** (8014, 8015, …) per your [`MANIFEST.ka`](../maat-ecosystem/MANIFEST.ka).
- **gitMaat** read/write with PostgreSQL.
- **OpenClaw** `openclaw doctor` / channels probe.

---

## 4. Progress smart meter (honest scoring)

Scores are **0.0–1.0** per dimension. **Overall** is the minimum of dimensions (weakest link), per Maat “truth over average.”

| Dimension | Weight (importance) | Evidence / test | Typical today* | To reach 1.0 |
|-----------|---------------------|------------------|----------------|--------------|
| **D1 — Inference local** | High | Init script Gemma tests + `nvidia-smi` under load | 0.85–1.0 | Stable GPU share; documented **per-request** long-context policy. |
| **D2 — Schema / contract** | High | `maatbench.run --category contract_integrity` | **1.0** when green | Re-run after any **`skeleton/schemas`** change. |
| **D3 — Policy / memory bench** | High | Full MaatBench categories | **0.0** until `maat_core` + fixtures | Install/run **`policy_fidelity`**, **`memory_fidelity`**, etc. |
| **D4 — Coordination (gitMaat)** | Medium | DB query + log round-trip | 0.0–1.0 by host | Valid **`PGVECTOR_DB_URL`**; tool path from OpenClaw to gitMaat. |
| **D5 — Training readiness** | Medium | Synthetic JSONL + capture volume + finetune dry-run | 0.3–0.6 | thousands of **captures**, domain **synthetic**, **finetune** smoke on GPU. |
| **D6 — Gateway / agents** | Medium | OpenClaw default local model + one channel reply | varies | Documented defaults; no silent cloud fallback. |

\*“Typical today” is illustrative — **recompute after every run** of the initiation script and bench.

**Suggested overall meter:**

```text
overall = min(D1, D2, D3, D4, D5, D6)   # Maat: truth is the bottleneck
```

Display however you like (Replit, MAAT Studio, terminal): a **six-segment bar** plus one **“limiting dimension”** label.

Machine-readable template (fill `score` 0..1 after each audit): [`initiation-meter.example.json`](initiation-meter.example.json).

---

## 5. What to collect to raise the meter — evidence and datasets

Training and governance improve only with **recorded evidence**. Prioritize:

### 5.1 For **better tool use / OpenClaw alignment**

| Dataset / evidence | Source | Target volume | Notes |
|--------------------|--------|---------------|--------|
| **Shim captures** | `gemma4-toolshim/training_data/captures.jsonl` | 500+ diverse turns | Route real traffic through **shim** so tool extractions are logged. |
| **Synthetic** | `generate_training.py` | 1k–10k | Breadth; not a substitute for live failures. |
| **Failure log** | Manual or agent: “shim could not extract” | All cases | Drives template and **finetune** priorities — **truth**. |

### 5.2 For **MaatBench / governance**

| Dataset / evidence | Source | Target | Notes |
|--------------------|--------|--------|--------|
| Policy scenarios | `maatbench/contracts/policy_tests.json` extensions | grow with real incidents | Each **new bypass attempt** → new test. |
| Memory audit cases | Memory fidelity contracts + gitMaat logs | paired expected/actual | Proves **attribution** and **rollback** stories. |

### 5.3 For **gitMaat continuity**

| Dataset / evidence | Source | Target | Notes |
|--------------------|--------|--------|--------|
| Decisions + learnings | `log_decision` / `log_learning` API or scripts | every significant infra change | Example: [`log-gitmaat-ollama-gpu-policy.py`](../scripts/log-gitmaat-ollama-gpu-policy.py). |

### 5.4 Suggested “initiation complete for training” threshold

- **D2 = 1.0** (schemas green)
- **D1 ≥ 0.85** (local inference stable)
- **≥ 200** real **captures** OR **≥ 2k** curated synthetic **plus** 50 logged **failure** examples
- Written **rationale** (this report section updated) for any dimension **&lt; 1.0**

---

## 6. Maintainer actions

1. After **infra or schema** changes: run **`run-tehuti-local-tests.sh`** and paste summary into your **gitMaat** or weekly note.
2. Update **§4 meter** numbers in this file **or** generate a small `initiation-status.json` from CI later.
3. Never mark **D3** complete until **full MaatBench** runs green — that is **order**, not optimism.

---

## 7. Related files

- [`scripts/run-tehuti-local-tests.sh`](../scripts/run-tehuti-local-tests.sh) — initiation automation
- [`docs/OLLAMA-LOCAL-GPU-TUNING.md`](OLLAMA-LOCAL-GPU-TUNING.md) — VRAM / context policy
- [`maat-ecosystem/MANIFEST.ka`](../maat-ecosystem/MANIFEST.ka) — organ map
- [`maat-ecosystem/maatbench/README.md`](../maat-ecosystem/maatbench/README.md) — bench tiers
- [`gemma4-toolshim/README.md`](../gemma4-toolshim/README.md) — capture + finetune

---

*Document version: 2026-04-07 — Tehuti Lab / Maat initiation layer.*
