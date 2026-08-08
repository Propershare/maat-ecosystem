#!/usr/bin/env python3
"""
Log Ollama GPU policy decision + learning to Maat JSON store (no PostgreSQL required).

Uses maat_memory/memory.py directly so a broken PGVECTOR_DB_URL does not block logging.

Run from workspace root:
  python3 scripts/log-gitmaat-ollama-gpu-policy.py

After PostgreSQL is healthy, decisions also sync via your normal MaatMemory workflows;
this script still appends to .maat_memory/maat_memory.json for audit trail.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mem_path = ROOT / "maatlangchain/maat_memory/memory.py"
    mi_path = ROOT / "maatlangchain/maat_memory/machine_info.py"
    if not mem_path.is_file():
        print("missing", mem_path, file=sys.stderr)
        return 1
    mm = _load_module("maat_mem_json", mem_path)
    mi = _load_module("maat_machine_info", mi_path)
    MaatMemory = mm.MaatMemory
    get_unique_agent_id = mi.get_unique_agent_id
    AGENT = get_unique_agent_id("cursor")

    memory = MaatMemory()
    memory.log_decision(
        AGENT,
        context="Ollama local inference on staydangerous (12GB-class GPU)",
        decision_made="Lower default OLLAMA_CONTEXT_LENGTH (8192–16384), OLLAMA_NUM_PARALLEL=1; avoid 64k service default; prefer per-request num_ctx for rare long context.",
        rationale="High service-wide context inflates KV cache and forces CPU offload; small models need VRAM for weights and layers on GPU.",
        options_considered=[
            "Keep OLLAMA_CONTEXT_LENGTH=64000",
            "Raise OLLAMA_NUM_PARALLEL for throughput",
            "Move inference to cloud",
        ],
    )
    memory.log_learning(
        agent=AGENT,
        topic="Ollama GPU headroom / KV cache",
        insight="Daemon-level OLLAMA_CONTEXT_LENGTH is mostly KV RAM, not model quality. Moderate service default (8k–16k) + per-request num_ctx preserves GPU residency for small models.",
        source="docs/OLLAMA-LOCAL-GPU-TUNING.md",
        confidence=0.9,
        applied=True,
        application_context="systemd override ollama.service",
    )
    print(f"Logged decision + learning as {AGENT} -> {mm.MAAT_MEMORY_JSON_PATH}")
    print("See docs/OLLAMA-LOCAL-GPU-TUNING.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
