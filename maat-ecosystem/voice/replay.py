"""
MAAT Session Replayer

Replay a past agent session from the event log.
Shows exactly what happened, decision by decision.
"""

import json
from pathlib import Path

MAAT_HOME = Path.home() / ".maat"


def replay_session(session_id: str):
    """Replay all events from a specific session."""
    path = MAAT_HOME / "events.jsonl"
    if not path.exists():
        print("No event log found.")
        return

    session_events = []
    for line in path.read_text().strip().split("\n"):
        try:
            event = json.loads(line)
            if event.get("session_id") == session_id:
                session_events.append(event)
        except Exception:
            pass

    if not session_events:
        print(f"No events found for session {session_id}")
        return

    print(f"🔄 Replaying session {session_id}")
    print(f"   {len(session_events)} events\n")

    for i, event in enumerate(session_events, 1):
        sev = event.get("severity", "info")
        etype = event.get("type", "?")
        ts = event.get("timestamp", "")

        # Color-code by severity
        prefix = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "debug": "🔍"}.get(sev, "•")

        print(f"  {i:3d}. {prefix} [{ts}] {etype}")
        payload = event.get("payload", {})
        if payload:
            for k, v in payload.items():
                print(f"       {k}: {v}")
        print()


def list_sessions():
    """List all unique sessions in the event log."""
    path = MAAT_HOME / "events.jsonl"
    if not path.exists():
        print("No event log found.")
        return

    sessions = {}
    for line in path.read_text().strip().split("\n"):
        try:
            event = json.loads(line)
            sid = event.get("session_id")
            if sid:
                if sid not in sessions:
                    sessions[sid] = {"start": event.get("timestamp"), "count": 0}
                sessions[sid]["count"] += 1
        except Exception:
            pass

    print(f"📋 {len(sessions)} sessions found\n")
    for sid, info in sessions.items():
        print(f"  {sid}  ({info['count']} events, started {info['start']})")
