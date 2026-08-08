"""Tests for sentinel_stream."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import gateway_contract as gc  # noqa: E402
import sentinel_stream as ss  # noqa: E402


def _make_record(
    session_id: str,
    turn: int,
    *,
    gateway: str = "ka2-research",
    expert: str = "archivist",
    tools: list[str] | None = None,
    research_grade: bool = True,
    total: int = 45,
    rbl: list[str] | None = None,
) -> dict:
    scorecard = None
    ka2 = None
    if research_grade:
        per = max(0, min(10, total // 5))
        scorecard = gc.MaatScorecard(
            scores=dict(
                truth=per,
                order=per,
                balance=per,
                justice=per,
                self_reflection=total - 4 * per,
            )
        )
        ka2 = {
            "research_type": "historical",
            "problem": "t",
            "time_dimension": "t",
            "level_of_analysis": "system",
            "life_cycle": {"contradictions": ["a"]},
        }
    rec = gc.build_record(
        correlation_id=gc.make_correlation_id(session_id, turn),
        agent_id="cursor_test",
        gateway_id=gateway,
        summary="t",
        sources=[gc.Source(kind="file", ref="/tmp/x")],
        tags=[f"expert:{expert}"],
        research_grade=research_grade,
        ka2=ka2,
        scorecard=scorecard,
        gateway_state={
            "turn_index": turn,
            "tools_used": tools or [],
            "model_id": "ollama/gemma4:e4b",
        },
        content_text="neutral text",
    )
    d = rec.to_dict()
    if rbl:
        d["rbl_flags"] = list(rbl)
    return d


class TestSentinelStream(unittest.TestCase):
    def test_ingest_single_record(self):
        stream = ss.SentinelStream(
            stream_path=Path("/tmp/never-read"),
            state_path=Path("/tmp/sentinel_state_never.json"),
        )
        state = stream.ingest_record(_make_record("s1", 0))
        self.assertEqual(state.session_id, "s1")
        self.assertEqual(state.turns, 1)
        self.assertEqual(state.active_gateway, "ka2-research")
        self.assertEqual(state.scorecard_pass_streak, 1)

    def test_stall_alerts_after_threshold(self):
        stream = ss.SentinelStream(
            stream_path=Path("/tmp/a"), state_path=Path("/tmp/b")
        )
        for i in range(4):
            stream.ingest_record(
                _make_record("s1", i, tools=[], expert="archivist")
            )
        state = stream.sessions["s1"]
        self.assertGreaterEqual(state.stall_ticks, ss.STALL_THRESHOLD)
        self.assertTrue(any(a.kind == "stall" for a in state.alerts))

    def test_scorecard_fail_streak_alert(self):
        stream = ss.SentinelStream(
            stream_path=Path("/tmp/a"), state_path=Path("/tmp/b")
        )
        for i in range(3):
            stream.ingest_record(_make_record("s2", i, total=30))
        state = stream.sessions["s2"]
        self.assertGreaterEqual(state.scorecard_fail_streak, ss.SCORECARD_FAIL_THRESHOLD)
        self.assertTrue(any(a.kind == "scorecard_streak" for a in state.alerts))

    def test_rbl_streak_alert(self):
        stream = ss.SentinelStream(
            stream_path=Path("/tmp/a"), state_path=Path("/tmp/b")
        )
        for i in range(2):
            stream.ingest_record(
                _make_record("s3", i, rbl=["static_over_motion"])
            )
        state = stream.sessions["s3"]
        self.assertEqual(state.rbl_flag_streak, 2)
        self.assertTrue(any(a.kind == "rbl_streak" for a in state.alerts))

    def test_ingest_from_stream_file(self):
        with tempfile.TemporaryDirectory() as td:
            stream_path = Path(td) / "records.jsonl"
            state_path = Path(td) / "state.json"
            with stream_path.open("w", encoding="utf-8") as fh:
                for i in range(3):
                    fh.write(json.dumps(_make_record("sX", i)) + "\n")
            sentinel = ss.SentinelStream(stream_path=stream_path, state_path=state_path)
            n = sentinel.ingest_from_stream(from_start=True)
            self.assertEqual(n, 3)
            sentinel.write_state()
            saved = json.loads(state_path.read_text())
            self.assertIn("sessions", saved)
            self.assertIn("sX", saved["sessions"])
            self.assertEqual(saved["sessions"]["sX"]["turns"], 3)


if __name__ == "__main__":
    unittest.main()
