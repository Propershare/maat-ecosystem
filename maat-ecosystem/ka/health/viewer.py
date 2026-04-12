"""
MAAT Log Viewer

Filter and display events from the MAAT event log.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

MAAT_HOME = Path.home() / ".maat"


def filter_events(events, agent_id=None, event_type=None, severity=None, since=None):
    filtered = []
    for e in events:
        if agent_id and e.get("payload", {}).get("agent_id") != agent_id:
            continue
        if event_type and not e.get("type", "").startswith(event_type):
            continue
        if severity and e.get("severity") != severity:
            continue
        if since and e.get("timestamp", "") < since:
            continue
        filtered.append(e)
    return filtered


def load_events():
    path = MAAT_HOME / "events.jsonl"
    if not path.exists():
        return []
    events = []
    for line in path.read_text().strip().split("\n"):
        try:
            events.append(json.loads(line))
        except Exception:
            pass
    return events


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MAAT Event Log Viewer")
    parser.add_argument("--agent", help="Filter by agent ID")
    parser.add_argument("--type", help="Filter by event type prefix")
    parser.add_argument("--severity", help="Filter by severity")
    parser.add_argument("--since", help="Filter events after this timestamp")
    parser.add_argument("-n", "--limit", type=int, default=50)
    args = parser.parse_args()

    events = load_events()
    events = filter_events(events, args.agent, args.type, args.severity, args.since)

    for e in events[-args.limit:]:
        sev = e.get("severity", "info")
        print(f"[{sev:8s}] {e.get('type', '?'):30s} {e.get('timestamp', '')}")
        payload = e.get("payload", {})
        if payload:
            for k, v in payload.items():
                print(f"           {k}: {v}")
        print()
