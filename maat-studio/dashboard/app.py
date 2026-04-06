"""
MAAT Studio Dashboard — minimal Flask app

Reads from:
- ~/.maat/identities.json
- ~/.maat/events.jsonl
- config.yaml

Read-only. No writes to the ecosystem.
"""

import json
from pathlib import Path

MAAT_HOME = Path.home() / ".maat"


def get_agents():
    path = MAAT_HOME / "identities.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def get_recent_events(limit=50):
    path = MAAT_HOME / "events.jsonl"
    if not path.exists():
        return []
    lines = path.read_text().strip().split("\n")
    events = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except Exception:
            pass
    return events


def get_event_counts():
    events = get_recent_events(limit=1000)
    counts = {}
    for e in events:
        t = e.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# When Flask is added:
# @app.route("/")
# def index():
#     return render_template("dashboard.html",
#         agents=get_agents(),
#         events=get_recent_events(),
#         counts=get_event_counts(),
#     )
