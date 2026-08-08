"""
Sentinel stream subscriber.

Reads the archivist JSONL stream (produced by ``archivist_gitmaat``) and
maintains one compact per-session state blob per session id. Sentinel only
ever looks at structured fields — never raw text — per
docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md.

State shape (intentionally small):

    {
      "session_id": ...,
      "last_correlation_id": ...,
      "last_turn_index": int,
      "last_seen_at": iso,
      "turns": int,
      "active_gateway": str,
      "active_expert": str|None,
      "scorecard_fail_streak": int,
      "scorecard_pass_streak": int,
      "rbl_flag_streak": int,
      "stall_ticks": int,           # turns without any new gateway/tool signal
      "alerts": [ ... ]             # list of SentinelAlert dicts (capped)
    }

The state dict is kept in memory and can be written to
``<workspace>/logs/archivist/sentinel_state.json`` so dashboards / tests
can inspect it.

Stdlib only.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from archivist_gitmaat import DEFAULT_STREAM, WORKSPACE_ROOT
from gateway_contract import HALT_AT_FLAGS, PASS_AT, parse_correlation_id

ALERT_CAP = 20
STALL_THRESHOLD = 3            # consecutive stalled turns before alert
SCORECARD_FAIL_THRESHOLD = 2   # consecutive failing scorecards before alert
RBL_FLAG_STREAK_THRESHOLD = 2  # consecutive turns with any RBL flag


@dataclass
class SentinelAlert:
    kind: str
    correlation_id: str
    session_id: str
    detail: str
    at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "detail": self.detail,
            "at": self.at,
        }


@dataclass
class SessionState:
    session_id: str
    last_correlation_id: str = ""
    last_turn_index: int = -1
    last_seen_at: str = ""
    turns: int = 0
    active_gateway: str = ""
    active_expert: str = ""
    scorecard_fail_streak: int = 0
    scorecard_pass_streak: int = 0
    rbl_flag_streak: int = 0
    stall_ticks: int = 0
    alerts: list[SentinelAlert] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "last_correlation_id": self.last_correlation_id,
            "last_turn_index": self.last_turn_index,
            "last_seen_at": self.last_seen_at,
            "turns": self.turns,
            "active_gateway": self.active_gateway,
            "active_expert": self.active_expert,
            "scorecard_fail_streak": self.scorecard_fail_streak,
            "scorecard_pass_streak": self.scorecard_pass_streak,
            "rbl_flag_streak": self.rbl_flag_streak,
            "stall_ticks": self.stall_ticks,
            "alerts": [a.to_dict() for a in self.alerts[-ALERT_CAP:]],
        }


class SentinelStream:
    """In-process stream aggregator. Not a daemon — see :meth:`tail_follow`."""

    def __init__(
        self,
        stream_path: Path | str | None = None,
        *,
        state_path: Path | str | None = None,
    ) -> None:
        self.stream_path = Path(stream_path) if stream_path else DEFAULT_STREAM
        self.state_path = (
            Path(state_path)
            if state_path
            else WORKSPACE_ROOT / "logs" / "archivist" / "sentinel_state.json"
        )
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, SessionState] = {}
        self._lock = threading.Lock()
        self._offset = 0

    @property
    def sessions(self) -> dict[str, SessionState]:
        with self._lock:
            return dict(self._sessions)

    def ingest_record(self, record: dict[str, Any]) -> SessionState:
        correlation_id = record.get("correlation_id") or ""
        try:
            session_id, turn_index = parse_correlation_id(correlation_id)
        except Exception:
            session_id = record.get("agent_id") or "unknown"
            turn_index = -1

        with self._lock:
            state = self._sessions.setdefault(session_id, SessionState(session_id=session_id))
            self._update_state(state, record, turn_index)
            return state

    def _update_state(
        self, state: SessionState, record: dict[str, Any], turn_index: int
    ) -> None:
        state.turns += 1
        state.last_correlation_id = record.get("correlation_id", state.last_correlation_id)
        state.last_turn_index = turn_index
        state.last_seen_at = record.get("created_at", state.last_seen_at)

        gateway = record.get("gateway_id", state.active_gateway)
        gw_state = record.get("gateway_state") or {}
        tools_used = list(gw_state.get("tools_used") or [])

        # Stall detection: same gateway, no tools, same expert - two in a row.
        expert_tag = next(
            (t.split(":", 1)[1] for t in record.get("tags", []) if t.startswith("expert:")),
            "",
        )
        stalled = (
            gateway == state.active_gateway
            and expert_tag == state.active_expert
            and not tools_used
        )
        state.active_gateway = gateway
        state.active_expert = expert_tag

        if stalled:
            state.stall_ticks += 1
        else:
            state.stall_ticks = 0

        # Scorecard streaks.
        scorecard = record.get("maat_scorecard") or {}
        if record.get("research_grade"):
            if scorecard.get("passed"):
                state.scorecard_pass_streak += 1
                state.scorecard_fail_streak = 0
            else:
                state.scorecard_fail_streak += 1
                state.scorecard_pass_streak = 0

        # RBL streak.
        rbl = list(record.get("rbl_flags") or [])
        if rbl:
            state.rbl_flag_streak += 1
        else:
            state.rbl_flag_streak = 0

        # Alerts.
        now = record.get("created_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if state.stall_ticks >= STALL_THRESHOLD:
            state.alerts.append(
                SentinelAlert(
                    kind="stall",
                    correlation_id=state.last_correlation_id,
                    session_id=state.session_id,
                    detail=f"{state.stall_ticks} consecutive stalled turns",
                    at=now,
                )
            )
        if state.scorecard_fail_streak >= SCORECARD_FAIL_THRESHOLD:
            state.alerts.append(
                SentinelAlert(
                    kind="scorecard_streak",
                    correlation_id=state.last_correlation_id,
                    session_id=state.session_id,
                    detail=(
                        f"{state.scorecard_fail_streak} consecutive scorecards below "
                        f"pass_at={PASS_AT}"
                    ),
                    at=now,
                )
            )
        if state.rbl_flag_streak >= RBL_FLAG_STREAK_THRESHOLD:
            state.alerts.append(
                SentinelAlert(
                    kind="rbl_streak",
                    correlation_id=state.last_correlation_id,
                    session_id=state.session_id,
                    detail=(
                        f"{state.rbl_flag_streak} consecutive turns with RBL flags "
                        f"(halt_at={HALT_AT_FLAGS})"
                    ),
                    at=now,
                )
            )
        if len(state.alerts) > ALERT_CAP:
            state.alerts = state.alerts[-ALERT_CAP:]

    def ingest_many(self, records: Iterable[dict[str, Any]]) -> list[SessionState]:
        return [self.ingest_record(r) for r in records]

    def ingest_from_stream(self, *, from_start: bool = False) -> int:
        """Read new lines appended since the last call. Returns rows ingested."""
        if not self.stream_path.exists():
            return 0
        with self.stream_path.open("r", encoding="utf-8") as fh:
            if from_start:
                self._offset = 0
            fh.seek(self._offset)
            rows = 0
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self.ingest_record(record)
                rows += 1
            self._offset = fh.tell()
        return rows

    def write_state(self) -> Path:
        payload = {
            "schema": "maat.sentinel_state.v1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "stream_path": str(self.stream_path),
            "sessions": {sid: s.to_dict() for sid, s in self.sessions.items()},
        }
        tmp = self.state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        tmp.replace(self.state_path)
        return self.state_path

    def tail_follow(self, *, poll_sec: float = 1.0) -> Iterator[dict[str, Any]]:
        """Block-yield new records. Dashboards/daemons can use this."""
        self.ingest_from_stream(from_start=True)
        self.write_state()
        while True:
            before = self._offset
            added = self.ingest_from_stream()
            if added:
                self.write_state()
                yield {
                    "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "added": added,
                    "offset_before": before,
                    "offset_after": self._offset,
                    "sessions": list(self.sessions.keys()),
                }
            time.sleep(poll_sec)


__all__ = [
    "SentinelStream",
    "SessionState",
    "SentinelAlert",
    "ALERT_CAP",
    "STALL_THRESHOLD",
    "SCORECARD_FAIL_THRESHOLD",
    "RBL_FLAG_STREAK_THRESHOLD",
]


if __name__ == "__main__":
    import sys

    stream = SentinelStream()
    n = stream.ingest_from_stream(from_start=True)
    path = stream.write_state()
    print(f"ingested {n} record(s); state written to {path}")
    print(json.dumps({sid: s.to_dict() for sid, s in stream.sessions.items()}, indent=2))
    sys.exit(0)
