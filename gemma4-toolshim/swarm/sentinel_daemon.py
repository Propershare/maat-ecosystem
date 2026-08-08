"""
Sentinel daemon — continuous subscriber for the archivist record stream.

This is the "always-on" companion to ``sentinel_stream.py``. It:

    1. Opens the archivist stream (``logs/archivist/records.jsonl`` by default).
    2. Tails it forever; each new line updates the in-memory per-session state.
    3. When new alerts fire (stall, scorecard streak, RBL streak), it appends
       them to ``logs/sentinel/alerts.jsonl`` so humans and downstream tools
       (n8n, a Telegram agent, a dashboard) can react.
    4. Writes a snapshot of state to ``logs/archivist/sentinel_state.json``
       (already handled by ``SentinelStream.write_state``) on every change.

Design notes:
    * Alerts are append-only. We dedupe by (session_id, kind, correlation_id)
      so a streak that keeps advancing only fires *one* line per escalation,
      not one line per turn.
    * The daemon is stdlib-only and runs forever. Restarts on the systemd
      side. SIGTERM / SIGINT trigger a clean flush.
    * This is **MAAT Sentinel (sessions/turns layer)**, not the older
      ``maat-sentinel/`` machine-watch daemon on :4242. Both can coexist —
      they look at different things. See ``GATEWAYS.md``.

Ports / sockets:
    None. File-based. Intentional — this process is a watcher, not a server.
    If a channel wants to query live state, it reads ``sentinel_state.json``
    or tails ``alerts.jsonl``.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from archivist_gitmaat import DEFAULT_STREAM, WORKSPACE_ROOT  # noqa: E402
from sentinel_stream import SentinelAlert, SentinelStream  # noqa: E402


DEFAULT_ALERTS_PATH = WORKSPACE_ROOT / "logs" / "sentinel" / "alerts.jsonl"
DEFAULT_POLL_SEC = float(os.getenv("SENTINEL_POLL_SEC", "1.0"))


class AlertEmitter:
    """Appends new alerts to a JSONL file, deduped by (session, kind, correlation_id).

    Dedup state is in-memory (resets on restart). A persistent offset file
    would be overkill — alerts are idempotent enough that an occasional
    duplicate is cheaper than maintaining crash-safe state.
    """

    def __init__(self, path: Path | str = DEFAULT_ALERTS_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seen: set[tuple[str, str, str]] = set()

    def emit_if_new(self, alert: SentinelAlert) -> bool:
        key = (alert.session_id, alert.kind, alert.correlation_id)
        if key in self._seen:
            return False
        self._seen.add(key)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(alert.to_dict()) + "\n")
        return True


class SentinelDaemon:
    def __init__(
        self,
        *,
        stream_path: Path | str | None = None,
        alerts_path: Path | str | None = None,
        poll_sec: float = DEFAULT_POLL_SEC,
    ) -> None:
        self.stream = SentinelStream(stream_path)
        self.emitter = AlertEmitter(alerts_path or DEFAULT_ALERTS_PATH)
        self.poll_sec = poll_sec
        self._stop = False

    def request_stop(self, *_: Any) -> None:
        self._stop = True

    def _emit_new_alerts(self) -> int:
        n = 0
        for sess_state in self.stream.sessions.values():
            for alert in sess_state.alerts:
                if self.emitter.emit_if_new(alert):
                    n += 1
        return n

    def run_once(self) -> dict[str, Any]:
        """Single pass. Useful for tests and short-lived runs."""
        added = self.stream.ingest_from_stream()
        self.stream.write_state()
        fired = self._emit_new_alerts()
        return {"records_ingested": added, "alerts_fired": fired}

    def run_forever(self) -> int:
        signal.signal(signal.SIGTERM, self.request_stop)
        signal.signal(signal.SIGINT, self.request_stop)
        print(
            f"[sentinel-daemon] watching {self.stream.stream_path}", flush=True
        )
        print(
            f"[sentinel-daemon] alerts -> {self.emitter.path}", flush=True
        )
        print(
            f"[sentinel-daemon] state  -> {self.stream.state_path}", flush=True
        )
        added = self.stream.ingest_from_stream(from_start=True)
        self.stream.write_state()
        fired = self._emit_new_alerts()
        if added or fired:
            print(
                f"[sentinel-daemon] warm start: ingested {added}, fired {fired} alert(s)",
                flush=True,
            )
        while not self._stop:
            added = self.stream.ingest_from_stream()
            if added:
                self.stream.write_state()
                fired = self._emit_new_alerts()
                if fired:
                    print(
                        f"[sentinel-daemon] +{added} record(s), {fired} new alert(s)",
                        flush=True,
                    )
            time.sleep(self.poll_sec)
        print("[sentinel-daemon] stopping", flush=True)
        return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="MAAT Sentinel daemon")
    parser.add_argument("--stream", default=str(DEFAULT_STREAM))
    parser.add_argument("--alerts", default=str(DEFAULT_ALERTS_PATH))
    parser.add_argument("--poll", type=float, default=DEFAULT_POLL_SEC)
    parser.add_argument(
        "--once",
        action="store_true",
        help="Drain current stream and exit (for testing).",
    )
    args = parser.parse_args(argv)
    daemon = SentinelDaemon(
        stream_path=args.stream,
        alerts_path=args.alerts,
        poll_sec=args.poll,
    )
    if args.once:
        result = daemon.run_once()
        print(json.dumps(result, indent=2))
        return 0
    return daemon.run_forever()


if __name__ == "__main__":
    sys.exit(main())
