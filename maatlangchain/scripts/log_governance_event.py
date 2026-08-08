#!/usr/bin/env python3
"""Insert one compact governance row into maat-memory (stdin JSON).

Used by Forge (Node) when FORGE_LOG_MEMORY=1. Requires PGVECTOR_DB_URL.

Example:
  echo '{"record_type":"forge_preflight","machine_id":"x",...}' | \\
    python3 maatlangchain/scripts/log_governance_event.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    # .../maatlangchain/scripts/this.py → maatlangchain/ on path for `maat_memory`
    maatlangchain = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(maatlangchain))
    raw = sys.stdin.read()
    if not raw.strip():
        print("empty stdin", file=sys.stderr)
        return 2
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"invalid json: {e}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("payload must be a JSON object", file=sys.stderr)
        return 2
    agent = str(payload.pop("_agent", "maat-forge"))
    from maat_memory.memory_postgres import MaatMemoryPostgres

    mem = MaatMemoryPostgres()
    mem.log_governance_event(payload, agent=agent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
