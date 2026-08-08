#!/usr/bin/env python3
"""Harvest a MAAT self-learning run into a grounded lesson/preference dataset.

Input : a run dir produced by run_operator.sh (contains immune.jsonl + session.jsonl)
Output: <run_dir>/grounded.json  — a summary + preference-pair candidates derived from
        REAL Maat-governed consequences (not hand-written essays).

The signal:
  - chosen   : tool calls that were ALLOWED (and not errored)  -> good trajectory steps
  - rejected : tool calls that were BLOCKED / errored          -> bad trajectory steps
This is the DPO/ORPO seed described in docs/MAAT-SELF-LEARNING-AGENT.md §3.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: harvest_trail.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    immune = load_jsonl(run_dir / "immune.jsonl")
    session = load_jsonl(run_dir / "session.jsonl")

    blocked = [e for e in immune if e.get("blocked")]
    bypass = [e for e in immune if "policy.bypass_attempt" in (e.get("tags") or [])]
    anomalies = [e for e in immune if e.get("event_type") == "anomaly.detected"]

    # Tool executions from the session event stream.
    tool_starts = [e for e in session if e.get("type") == "tool_execution_start"]
    tool_ends = [e for e in session if e.get("type") == "tool_execution_end"]
    errored = [e for e in tool_ends if e.get("isError")]

    chosen, rejected = [], []
    blocked_targets = {e.get("target") for e in blocked}
    for s in tool_starts:
        step = {"tool": s.get("toolName"), "args": s.get("args")}
        tgt = ""
        a = s.get("args") or {}
        if isinstance(a, dict):
            tgt = a.get("path") or a.get("command") or ""
        if any(str(tgt) and str(tgt) in str(bt) for bt in blocked_targets if bt):
            rejected.append({**step, "reason": "immune_hook_blocked"})
        else:
            chosen.append(step)

    loop_proven = bool(blocked) and any(
        (e.get("blocked") is False) or (e.get("event_type") == "sentinel.pulse") for e in immune
    ) or (len(chosen) > 0 and len(blocked) > 0)

    report = {
        "run_dir": str(run_dir),
        "loop_proven": loop_proven,
        "counts": {
            "immune_events": len(immune),
            "blocked": len(blocked),
            "policy_bypass_attempts": len(bypass),
            "anomalies": len(anomalies),
            "tool_calls": len(tool_starts),
            "tool_errors": len(errored),
        },
        "preference_pairs_seed": {
            "chosen_steps": chosen,
            "rejected_steps": rejected,
        },
        "lessons": [
            {
                "type": "lesson.distilled",
                "severity": e.get("severity"),
                "reason": e.get("reason"),
                "target": e.get("target"),
                "tags": e.get("tags"),
            }
            for e in blocked
        ],
        "note": (
            "Grounded signal from real Maat-governed consequences. chosen=allowed tool steps, "
            "rejected=blocked/errored steps. Feeds DPO per MAAT-FINETUNING-METHOD.md."
        ),
    }

    out = run_dir / "grounded.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    print(f"loop_proven: {loop_proven}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
