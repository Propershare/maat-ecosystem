# Gemma4 Tool-Call Shim & Fine-Tuning Pipeline

A proxy shim that makes Gemma4 (via Ollama) work with OpenAI-compatible tool-call APIs, plus a complete pipeline to capture real usage data and fine-tune the model to emit native tool calls.

---

## Architecture

```
OpenCode / any OpenAI client
           │
           ▼ POST /v1/chat/completions (port 11435)
    ┌─────────────────┐
    │   shim.py v3    │  ← extracts tool calls from <thinking>
    └──────┬──────────┘
           │ POST /api/chat (port 11434)
           ▼
        Ollama
      (gemma4:e4b)
```

The shim intercepts requests that include `tools`, forces Ollama to respond non-streaming, then parses Gemma4's `<thinking>` field using 6 progressive strategies to extract tool call intent. It converts the result to proper OpenAI `tool_calls` format and re-streams to the client.

### Multi-Turn Support

The shim handles multi-turn conversations where tool results come back:

```
User → [tool call extracted] → Tool runs → Tool result → User message
         (shim turn 1)                    (shim turn 2)
```

Tool result messages (`role: "tool"`) are sanitized and passed through to Ollama so the model can continue the conversation.

---

## Files

| File | Purpose |
|------|---------|
| `shim.py` | Main proxy (v3 — hardened) |
| `gemma4-shim.service` | systemd user service |
| `generate_training.py` | Synthetic training data generator |
| `finetune.py` | Unsloth LoRA fine-tuning script |
| `training_data/captures.jsonl` | Live captures from production |
| `training_data/synthetic.jsonl` | Synthetic training examples |
| `output/` | Fine-tuned model artifacts |

---

## Quick Start

### 1. Run the Shim

```bash
# Direct
python3 shim.py

# With options
SHIM_PORT=11435 OLLAMA_BASE=http://localhost:11434 python3 shim.py

# Health check
curl http://localhost:11435/health
```

### 2. Install as systemd User Service

```bash
# Copy service file
cp gemma4-shim.service ~/.config/systemd/user/

# Enable and start
systemctl --user daemon-reload
systemctl --user enable gemma4-shim
systemctl --user start gemma4-shim

# Check status
systemctl --user status gemma4-shim

# View logs
journalctl --user -u gemma4-shim -f
```

### 3. Configure OpenCode

Point OpenCode (or any OpenAI-compatible client) to the shim port instead of Ollama directly:

```json
{
  "base_url": "http://localhost:11435/v1",
  "model": "gemma4:e4b"
}
```

---

## Training Data Pipeline

### Step 1: Generate Synthetic Data

```bash
python3 generate_training.py --count 1000 --output training_data/synthetic.jsonl
```

This generates 1000 diverse tool-call examples covering:
- Single tool calls (bash, read, write, grep, glob, edit)
- Multi-turn conversations with tool results
- Error recovery patterns
- Parallel tool calls
- Complex chained workflows

### Step 2: Collect Live Captures

The shim automatically captures every successful tool-call extraction to `training_data/captures.jsonl`. No configuration needed — it happens in the background using a thread-safe writer.

Each capture includes:
- Full conversation history (messages + tools)
- The corrected assistant message with proper `tool_calls`
- Source metadata (thinking/content/native)
- Timestamp

### Step 3: Merge and Review

```bash
# Count captures so far
wc -l training_data/captures.jsonl training_data/synthetic.jsonl

# Peek at a capture
head -1 training_data/captures.jsonl | python3 -m json.tool
```

### Step 4: Fine-Tune

```bash
# Install dependencies
pip install "transformers>=5.5.0" "unsloth>=2026.4.6" trl peft accelerate bitsandbytes datasets

# Verify Gemma4 support before training
python3 -c "import unsloth, transformers; from transformers import Gemma4Config, AutoConfig; print('unsloth', unsloth.__version__); print('transformers', transformers.__version__); print('model_type', AutoConfig.from_pretrained('google/gemma-4-e2b-it').model_type)"

# Quick test (100 steps, no GGUF export)
python3 finetune.py --max-steps 100 --skip-gguf

# Full training run
python3 finetune.py

# Custom model
python3 finetune.py --model google/gemma-4-e2b-it --max-steps 2000
```

The fine-tuning script:
1. Loads the selected Gemma model in 4-bit (QLoRA) via Unsloth
2. Applies LoRA adapters (r=16, alpha=32) to q/k/v/o projections
3. Trains on all JSONL data with `SFTTrainer`
4. Saves LoRA adapter + full GGUF Q4_K_M

Note: if you use `/home/suspect/.n8n/tehuti-lab-webui-venv`, ensure the venv is writable by your user. A root-owned venv will fail package upgrades with permission errors.

### Step 5: Deploy to Ollama

```bash
# After fine-tuning, import the model
ollama create gemma3-toolcall -f output/Modelfile

# Test it
ollama run gemma3-toolcall "List files in the current directory"

# Update shim to use new model (or set in OpenCode config)
```

---

## Shim Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | OpenAI-compatible (shimmed) |
| `/api/chat` | POST | Ollama native format (shimmed) |
| `/health` | GET | Health + stats JSON |
| `/*` | GET/POST | Transparent proxy to Ollama |

### Health Response

```json
{
  "status": "ok",
  "version": "3",
  "shim_port": 11435,
  "ollama_base": "http://localhost:11434",
  "ollama_status": "reachable",
  "stats": {
    "requests": 142,
    "shims": 89,
    "captures": 89,
    "errors": 0
  },
  "timestamp": "2025-04-06T12:00:00+00:00"
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama API URL |
| `SHIM_PORT` | `11435` | Port for the shim to listen on |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `TRAINING_DATA_DIR` | `./training_data/` | Directory for captures |

---

## Tool Extraction Strategies

The shim tries 6 strategies in order, returning on first success:

1. **Function call syntax** — `tool_name(arg="value")`
2. **JSON near tool name** — `{"path": "..."}` adjacent to a tool mention
3. **Key=value patterns** — `path = "file.py"` in natural language
4. **Code blocks with path** — fenced ``` blocks + file path mention
5. **NL plan extraction** — backtick file paths + inline content
6. **Path + code block fallback** — most lenient, picks best write tool

---

## Gemma4 Notes

Gemma4 tends to plan tool calls in its `<thinking>` field rather than emitting them as structured JSON. The shim bridges this gap while real training data accumulates. After fine-tuning, the model should emit native `tool_calls` directly.

### When Gemma-4 Is in Transformers/Unsloth

Update `finetune.py`:
```python
# SWAP_FOR_GEMMA4
DEFAULT_MODEL = "unsloth/gemma-4-12b-it"  # or your preferred size
```

The training data format is model-agnostic — the captures and synthetic data work with any instruction-tuned model.

---

## Training Data Format

Each JSONL line is a JSON object:

```json
{
  "conversations": [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "List all Python files"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "bash",
          "arguments": "{\"command\": \"find . -name '*.py' -type f\"}"
        }
      }]
    }
  ],
  "tools": [...]
}
```

Compatible with: **Unsloth**, **Axolotl**, **LLaMA-Factory**, and any framework that supports the OpenAI chat format.

---

## Development

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python3 shim.py

# Test health
curl -s http://localhost:11435/health | python3 -m json.tool

# Watch captures in real-time
tail -f training_data/captures.jsonl | python3 -m json.tool

# Generate and check training data
python3 generate_training.py --count 50 --output /tmp/test.jsonl
wc -l /tmp/test.jsonl
head -1 /tmp/test.jsonl | python3 -m json.tool
```

---

## License

MIT — use freely.
