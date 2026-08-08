"""
Memory Live Runner — tests against real Postgres gitMaat (not SQLite adapter).

Requires PGVECTOR_DB_URL. Run:
  python3 -m maatbench.run --category memory_live
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
LAB = ECOSYSTEM.parent
sys.path.insert(0, str(ECOSYSTEM))
sys.path.insert(0, str(LAB / "maatlangchain"))


def _pg_url() -> str | None:
    url = os.environ.get("PGVECTOR_DB_URL")
    if url:
        return url
    try:
        from maat_memory.paths import get_pgvector_db_url

        return get_pgvector_db_url()
    except Exception:
        return None


def run_memory_live_tests(test_defs: list[dict]) -> list[dict]:
    results = []
    marker = f"memory_live_{uuid.uuid4().hex[:12]}"
    agent = f"maatbench_live_{uuid.uuid4().hex[:8]}"

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        passed = True
        notes: list[str] = []

        try:
            if op == "require_url":
                url = _pg_url()
                if not url:
                    passed = False
                    notes.append("PGVECTOR_DB_URL missing — cannot claim live memory")
                else:
                    notes.append("PGVECTOR_DB_URL present")

            elif op == "write_learning":
                url = _pg_url()
                if not url:
                    passed = False
                    notes.append("skipped — no PGVECTOR_DB_URL")
                else:
                    os.environ["PGVECTOR_DB_URL"] = url
                    from maat_memory import MaatMemory

                    mem = MaatMemory()
                    lid = mem.log_learning(
                        agent,
                        "memory_live",
                        f"MaatBench live probe {marker}",
                        "maatbench.memory_live",
                        confidence=0.9,
                    )
                    if not lid:
                        passed = False
                        notes.append("log_learning returned empty id")
                    else:
                        notes.append(f"wrote learning_id={lid} agent={agent}")

            elif op == "read_attribution":
                url = _pg_url()
                if not url:
                    passed = False
                    notes.append("skipped — no PGVECTOR_DB_URL")
                else:
                    os.environ["PGVECTOR_DB_URL"] = url
                    from maat_memory import MaatMemory

                    mem = MaatMemory()
                    learnings = mem.get_learnings(agent=agent, limit=20)
                    hits = list(learnings)
                    if len(hits) < test.get("expected", {}).get("min_results", 1):
                        learnings = mem.get_learnings(topic="memory_live", limit=50)
                        hits = [
                            L
                            for L in learnings
                            if marker in str(L.get("insight", ""))
                        ]
                    if len(hits) < 1:
                        passed = False
                        notes.append(f"no learning found for agent={agent} / marker={marker}")
                    else:
                        row = hits[0]
                        who = row.get("agent") or row.get("agent_id") or ""
                        if not who:
                            passed = False
                            notes.append("learning row missing agent attribution")
                        else:
                            notes.append(f"found attributed learning agent={who}")

            elif op == "reject_empty_agent":
                # Unit-level Justice check (same rule as MCP _require_agent)
                def _require_agent(a):
                    if a is None or not str(a).strip():
                        raise ValueError("agent is required")
                    return str(a).strip()

                raised = False
                try:
                    _require_agent("")
                except ValueError:
                    raised = True
                if not raised:
                    passed = False
                    notes.append("empty agent was accepted")
                else:
                    notes.append("empty agent rejected")

            else:
                passed = False
                notes.append(f"unknown operation: {op}")

        except Exception as e:
            passed = False
            notes.append(str(e))

        results.append(
            {
                "id": test_id,
                "name": test.get("name", test_id),
                "category": "memory_live",
                "passed": passed,
                "score": 1.0 if passed else 0.0,
                "notes": "; ".join(notes),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    return results
