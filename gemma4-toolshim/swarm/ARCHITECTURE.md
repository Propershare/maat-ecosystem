# Expert LLM Swarm Architecture

## Vision
A farm of fine-tuned gemma4:e4b models, each an expert in a specific domain,
deployable locally or on mobile devices, connected via OpenClaw gateway as
"employee agents."

## Model Classes

### 1. RAG Agent (rag-expert)
- **Role:** Knowledge retrieval and synthesis
- **Tools:** query_gitmaat, read_file, search_files, web_search
- **Training focus:** Structured retrieval, citation, context assembly
- **Use case:** Answer questions from private knowledge bases

### 2. Code Agent (code-expert)
- **Role:** Write, edit, review code
- **Tools:** write_file, edit_file, bash, read_file, glob, grep
- **Training focus:** Tool-call precision for file ops, test-driven coding
- **Use case:** Local coding assistant that works offline

### 3. Ops Agent (ops-expert)
- **Role:** System monitoring, deployment, health checks
- **Tools:** execute_command, get_system_info, bash
- **Training focus:** Diagnostic reasoning, safe command execution
- **Use case:** Server/device management

### 4. Comms Agent (comms-expert)
- **Role:** Draft emails, messages, summaries
- **Tools:** Minimal — mostly generation
- **Training focus:** Tone matching, context awareness, brevity
- **Use case:** Communication assistant

### 5. Data Agent (data-expert)
- **Role:** Query databases, analyze data, generate reports
- **Tools:** run_python_code, read_file, write_file
- **Training focus:** SQL/pandas patterns, visualization
- **Use case:** Local data analysis

## Deployment Stack

```
┌─────────────────────────────────────────┐
│           OpenClaw Gateway              │
│         (orchestrator / router)          │
├─────────┬──────────┬──────────┬─────────┤
│ rag-exp │ code-exp │ ops-exp  │ comms   │
│ :11441  │ :11442   │ :11443   │ :11444  │
├─────────┴──────────┴──────────┴─────────┤
│              Ollama Runtime              │
│         (model hot-swap / queue)         │
├─────────────────────────────────────────┤
│     Tool-Call Shim (if needed)           │
│     Port 11435 → Ollama 11434           │
└─────────────────────────────────────────┘
```

## Mobile Deployment

Each expert model is ~5-10GB GGUF. For mobile:
- Use llama.cpp or MLC-LLM runtime
- 4-bit quantized (Q4_K_M) fits in 4-6GB RAM
- Tool schemas baked into model weights
- OpenClaw mobile gateway for orchestration
- Offline-first, sync when connected

## Fine-Tuning Pipeline

```
1. Capture    → shim collects real tool-call translations
2. Synthesize → generate_training.py creates diverse examples  
3. Combine    → merge captures + synthetic data
4. Fine-tune  → Unsloth LoRA on gemma4 base
5. Export     → GGUF Q4_K_M for Ollama
6. Test       → validate tool-call accuracy
7. Deploy     → Ollama model + OpenClaw agent config
```

## Agent Registration (OpenClaw)

Each expert registers as an OpenClaw agent:
```yaml
# Example: rag-expert agent config
name: rag-expert
model: ollama/gemma4-rag:latest
tools:
  - query_gitmaat
  - read_file  
  - search_files
system_prompt: |
  You are a RAG specialist. Retrieve relevant information
  and synthesize accurate answers with citations.
```

## Scaling

- **Single machine:** Run 2-3 experts simultaneously (swap others on demand)
- **Multi-device:** Distribute experts across Pi cluster / phones
- **Hybrid:** Local experts + cloud fallback for complex tasks
- **Swarm mode:** Router dispatches queries to best-fit expert
