#!/usr/bin/env python3
"""
Parity check: Ollama tags vs opencode.json provider.ollama.models keys.
Run from anywhere; defaults to repo-root opencode.json next to scripts/.

Ideas borrowed from a structured "inventory" workflow — keeps OpenCode's model
picker honest without any claw-code dependency.

Usage:
  python3 scripts/check-opencode-ollama-drift.py
  python3 scripts/check-opencode-ollama-drift.py /path/to/opencode.json
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def ollama_tags() -> set[str]:
    out = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if out.returncode != 0:
        print("ollama list failed:", out.stderr or out.stdout, file=sys.stderr)
        sys.exit(1)
    tags: set[str] = set()
    for line in out.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\S+)", line)
        if m:
            tags.add(m.group(1))
    return tags


def config_model_keys(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    models = (
        data.get("provider", {})
        .get("ollama", {})
        .get("models", {})
    )
    return set(models.keys()) if isinstance(models, dict) else set()


def main() -> None:
    cfg = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root() / "opencode.json"
    if not cfg.is_file():
        print(f"Missing config: {cfg}", file=sys.stderr)
        sys.exit(1)

    ollama = ollama_tags()
    declared = config_model_keys(cfg)

    only_ollama = sorted(ollama - declared)
    only_config = sorted(declared - ollama)

    print(f"Config: {cfg}")
    print(f"Ollama tags: {len(ollama)} | opencode.json models: {len(declared)}")

    if only_ollama:
        print("\nIn Ollama but NOT in opencode.json (add under provider.ollama.models):")
        for t in only_ollama:
            print(f"  + {t}")

    if only_config:
        print("\nIn opencode.json but NOT in ollama list (typo or not pulled):")
        for t in only_config:
            print(f"  - {t}")

    if not only_ollama and not only_config:
        print("\nNo drift — lists match.")
        sys.exit(0)

    sys.exit(2 if only_ollama else 0)


if __name__ == "__main__":
    main()
