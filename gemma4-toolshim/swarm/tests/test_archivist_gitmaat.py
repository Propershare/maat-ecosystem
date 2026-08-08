"""Tests for archivist_gitmaat. Does not require Postgres to be running."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import archivist_gitmaat  # noqa: E402
import gateway_contract as gc  # noqa: E402


class TestArchivistAdapter(unittest.TestCase):
    def _make_record(self, research_grade: bool = False) -> gc.ArchivistRecord:
        scorecard = None
        ka2 = None
        if research_grade:
            scorecard = gc.MaatScorecard(
                scores=dict(truth=9, order=8, balance=9, justice=9, self_reflection=8)
            )
            ka2 = {
                "research_type": "historical",
                "problem": "Test problem.",
                "time_dimension": "Test time frame.",
                "level_of_analysis": "system",
                "life_cycle": {"contradictions": ["a"]},
            }
        return gc.build_record(
            correlation_id=gc.make_correlation_id("testsess", 1),
            agent_id="cursor_test",
            gateway_id="ka2-research",
            summary="Test turn for the archivist adapter.",
            sources=[gc.Source(kind="file", ref="/tmp/x.md")],
            tags=["domain:test"],
            research_grade=research_grade,
            ka2=ka2,
            scorecard=scorecard,
            content_text="A neutral, factual sentence.",
        )

    def test_persist_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            adapter = archivist_gitmaat.ArchivistGitMaatAdapter(
                stream_path=stream, enable_gitmaat=False
            )
            rec = self._make_record()
            result = adapter.persist(rec)
            self.assertEqual(result.contract_errors, [])
            self.assertEqual(result.gitmaat_status, "disabled")
            self.assertTrue(stream.exists())
            lines = stream.read_text().strip().splitlines()
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["correlation_id"], rec.correlation_id)
            self.assertEqual(parsed["schema"], gc.SCHEMA_RECORD)

    def test_persist_research_grade_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            adapter = archivist_gitmaat.ArchivistGitMaatAdapter(
                stream_path=stream, enable_gitmaat=False
            )
            rec = self._make_record(research_grade=True)
            result = adapter.persist(rec)
            self.assertEqual(result.contract_errors, [])
            self.assertTrue(result.ok)

    def test_persist_invalid_record_flags_errors_but_still_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            adapter = archivist_gitmaat.ArchivistGitMaatAdapter(
                stream_path=stream, enable_gitmaat=False
            )
            bad = {
                "schema": "maat.archivist_record.v1",
                "record_id": "r-1",
                "correlation_id": "s:0001",
                "created_at": gc.now_iso(),
                "agent_id": "test",
                "gateway_id": "test",
                "research_grade": True,
                "tags": [],
                "summary": "",
                "sources": [],
            }
            result = adapter.persist(bad)
            self.assertTrue(result.contract_errors)
            self.assertEqual(result.gitmaat_status, "skipped:contract_errors")
            self.assertTrue(stream.exists())

    def test_gitmaat_log_learning_uses_maat_memory_signature(self):
        """Regression: log_learning must use topic/insight/source, not context/lesson."""
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            adapter = archivist_gitmaat.ArchivistGitMaatAdapter(
                stream_path=stream, enable_gitmaat=True, agent_id="sig-test"
            )
            mem = mock.Mock()
            mem.log_change = mock.Mock(return_value="cid-1")
            mem.log_decision = mock.Mock(return_value="did-1")
            mem.log_learning = mock.Mock(return_value="lid-1")
            adapter._memory = mem
            adapter._memory_probed = True
            adapter._memory_status = "ok"

            rec = self._make_record(research_grade=True)
            rec.maat_scorecard = gc.MaatScorecard(
                scores=dict(truth=5, order=5, balance=5, justice=5, self_reflection=5),
                correction_notes="fail on purpose",
            )
            rd = rec.to_dict()
            rd["maat_scorecard"]["passed"] = False
            rd["maat_scorecard"]["total"] = 25
            rd["maat_scorecard"]["halt_flags"] = 0

            adapter.persist(rd)

            mem.log_learning.assert_called_once()
            _, kwargs = mem.log_learning.call_args
            self.assertIn("topic", kwargs)
            self.assertIn("insight", kwargs)
            self.assertIn("source", kwargs)
            self.assertNotIn("lesson", kwargs)
            self.assertNotIn("context", kwargs)


if __name__ == "__main__":
    unittest.main()
