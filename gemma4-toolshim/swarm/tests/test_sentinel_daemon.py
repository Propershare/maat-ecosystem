"""Tests for sentinel_daemon."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

import sentinel_daemon as sd  # noqa: E402


def _write_record(stream: Path, *, correlation_id: str, gateway: str, rbl: list[str] | None = None, research: bool = False, passed: bool = True) -> None:
    record = {
        "schema": "maat.archivist_record.v1",
        "correlation_id": correlation_id,
        "created_at": "2026-04-16T12:00:00Z",
        "agent_id": "test",
        "gateway_id": gateway,
        "research_grade": research,
        "tags": [f"expert:default", f"gateway:{gateway}"],
        "summary": "x",
        "sources": [],
        "rbl_flags": list(rbl or []),
        "gateway_state": {"turn_index": int(correlation_id.split(":")[-1]), "tools_used": []},
    }
    if research:
        record["maat_scorecard"] = {
            "schema": "maat.ka2_scorecard.v1",
            "scores": {"truth": 10, "order": 10, "balance": 10, "justice": 10, "self_reflection": 10},
            "total": 50 if passed else 20,
            "pass_at": 40,
            "passed": passed,
            "halt_flags": len(rbl or []),
        }
    with stream.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


class TestAlertEmitterDedup(unittest.TestCase):
    def test_dedup_same_key(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "alerts.jsonl"
            em = sd.AlertEmitter(path)
            from sentinel_stream import SentinelAlert
            a = SentinelAlert(kind="stall", correlation_id="s:1", session_id="s", detail="x", at="now")
            self.assertTrue(em.emit_if_new(a))
            self.assertFalse(em.emit_if_new(a))
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)


class TestDaemonRunOnce(unittest.TestCase):
    def test_run_once_ingests_and_fires_alerts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            alerts = Path(td) / "alerts.jsonl"
            for i in range(3):
                _write_record(
                    stream,
                    correlation_id=f"sess:{i}",
                    gateway="test-gw",
                    rbl=["individualism_over_systemic"],
                    research=True,
                    passed=False,
                )
            daemon = sd.SentinelDaemon(stream_path=stream, alerts_path=alerts)
            result = daemon.run_once()
            self.assertEqual(result["records_ingested"], 3)
            self.assertGreaterEqual(result["alerts_fired"], 1)
            text = alerts.read_text(encoding="utf-8")
            self.assertTrue(text)
            first_line = json.loads(text.splitlines()[0])
            self.assertIn(first_line["kind"], {"rbl_streak", "scorecard_streak", "stall"})


if __name__ == "__main__":
    unittest.main()
