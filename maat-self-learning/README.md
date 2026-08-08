# maat-self-learning

Increment 1 of the **MAAT Self-Learning Agent** (spec: [`../docs/MAAT-SELF-LEARNING-AGENT.md`](../docs/MAAT-SELF-LEARNING-AGENT.md)).

Proves the core loop: a tool-capable **operator** model, contained inside `maat-runtime` with the **immune
hook** on, acts on a bounded task; the **immune trail** captures the real Maat-governed consequences
(allowed scratch writes + a blocked sacred-path write); `harvest_trail.py` turns that trail into a
**grounded preference/lesson dataset**.

This folder lives **outside** `maat-runtime` on purpose — it *uses* the runtime, never modifies it
(respects that fork's `AGENTS.md`).

## Run

```bash
# Frontier operator (chosen to prove the loop). Needs a key:
export ANTHROPIC_API_KEY=...        # or OPENAI_API_KEY / OPENROUTER_API_KEY
./run_operator.sh

# Local plumbing proof only (weak tool-caller; pull qwen-coder first):
./run_operator.sh --local
```

Without a credential the launcher **refuses cleanly** (Maat: no faked runs).

## Output (per run, under `runs/<timestamp>/`)

| File | What |
|------|------|
| `immune.jsonl` | Append-only immune event trail (the enforcement evidence) |
| `session.jsonl` | `pi --mode json` event stream (operator's actions) |
| `grounded.json` | Harvested summary + preference-pair seed (chosen=allowed, rejected=blocked/errored) |
| `workspace/` | The sandbox the operator writes into |

## Harvest

```bash
python3 harvest_trail.py runs/<timestamp>
```

## Files

- `run_operator.sh` — launcher (immune env + verified `pi` flags + clean refusal).
- `tasks/bounded_task_01.md` — the bounded task (includes a sacred-path tripwire that must be blocked).
- `harvest_trail.py` — immune+session JSONL → `grounded.json`.
- `operator-models.json` — local Ollama operator template (later).
