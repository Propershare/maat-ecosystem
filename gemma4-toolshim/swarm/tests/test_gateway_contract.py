"""Unit tests for gateway_contract. Stdlib-only.

Run from ``gemma4-toolshim/swarm/``::

    python3 -m unittest tests.test_gateway_contract
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import gateway_contract as gc  # noqa: E402


class TestCorrelationId(unittest.TestCase):
    def test_roundtrip(self):
        cid = gc.make_correlation_id("sess-abc", 7)
        self.assertEqual(cid, "sess-abc:0007")
        sess, turn = gc.parse_correlation_id(cid)
        self.assertEqual(sess, "sess-abc")
        self.assertEqual(turn, 7)

    def test_rejects_missing_session(self):
        with self.assertRaises(ValueError):
            gc.make_correlation_id("", 0)

    def test_rejects_negative_turn(self):
        with self.assertRaises(ValueError):
            gc.make_correlation_id("s", -1)


class TestScorecard(unittest.TestCase):
    def test_total_and_pass(self):
        card = gc.MaatScorecard(
            scores=dict(truth=9, order=9, balance=9, justice=9, self_reflection=9)
        )
        self.assertEqual(card.total, 45)
        self.assertTrue(card.passed)

    def test_halt_forces_fail_even_if_numerically_high(self):
        card = gc.MaatScorecard(
            scores=dict(truth=10, order=10, balance=10, justice=10, self_reflection=10),
            halt_flags=3,
        )
        self.assertEqual(card.total, 50)
        self.assertFalse(card.passed)

    def test_threshold_is_40(self):
        card = gc.MaatScorecard(
            scores=dict(truth=8, order=8, balance=8, justice=8, self_reflection=8)
        )
        self.assertEqual(card.total, 40)
        self.assertTrue(card.passed)
        low = gc.MaatScorecard(
            scores=dict(truth=7, order=8, balance=8, justice=8, self_reflection=8),
            correction_notes="truth axis weak",
        )
        self.assertEqual(low.total, 39)
        self.assertFalse(low.passed)


class TestValidateRecord(unittest.TestCase):
    def _minimal(self, **overrides):
        record = gc.build_record(
            correlation_id=gc.make_correlation_id("sess", 1),
            agent_id="cursor_test",
            gateway_id="ka2-research",
            summary="Test record for the gateway contract.",
            sources=[gc.Source(kind="file", ref="/tmp/foo.md", line_start=1, line_end=2)],
            tags=["domain:test"],
            research_grade=False,
            content_text="A neutral factual sentence.",
        )
        d = record.to_dict()
        d.update(overrides)
        return d

    def test_minimal_non_research_is_valid(self):
        errs = gc.validate_record(self._minimal())
        self.assertEqual(errs, [], f"unexpected: {errs}")

    def test_research_grade_requires_ka2_and_scorecard(self):
        record = self._minimal(research_grade=True)
        errs = gc.validate_record(record)
        self.assertIn("research_grade=true requires ka2 header", errs)
        self.assertIn("research_grade=true requires maat_scorecard", errs)

    def test_scorecard_pass_at_is_sacred(self):
        card = gc.MaatScorecard(
            scores=dict(truth=9, order=9, balance=9, justice=9, self_reflection=9)
        ).to_dict()
        card["pass_at"] = 30  # sabotage
        record = self._minimal(research_grade=True)
        record["ka2"] = {
            "research_type": "historical",
            "problem": "x",
            "time_dimension": "y",
            "life_cycle": {"contradictions": ["a"]},
        }
        record["maat_scorecard"] = card
        errs = gc.validate_record(record)
        self.assertTrue(any("pass_at is sacred" in e for e in errs))

    def test_example_file_validates(self):
        data = gc.load_example_record()
        self.assertEqual(gc.validate_record(data), [])


class TestDetectors(unittest.TestCase):
    def test_ai_tell_vocab(self):
        hits = gc.detect_forbidden_hits(
            "let us delve into this tapestry", research_grade=False, ka2=None
        )
        self.assertIn("ai_tell_vocabulary", hits)

    def test_missing_method_naming_when_research_grade(self):
        hits = gc.detect_forbidden_hits(
            "brief answer", research_grade=True, ka2={}
        )
        self.assertIn("missing_method_naming", hits)

    def test_static_snapshot_required_motion(self):
        ka2 = {"research_type": "historical", "life_cycle": {}}
        hits = gc.detect_forbidden_hits(
            "this is a description of the history of X",
            research_grade=True,
            ka2=ka2,
        )
        self.assertIn("static_snapshot_required_motion", hits)

    def test_motion_present_silences_hit(self):
        ka2 = {
            "research_type": "historical",
            "life_cycle": {"periods": ["a"], "contradictions": ["b"]},
        }
        hits = gc.detect_forbidden_hits(
            "this is a description of the history of X",
            research_grade=True,
            ka2=ka2,
        )
        self.assertNotIn("static_snapshot_required_motion", hits)

    def test_rbl_detects_static_language(self):
        flags = gc.detect_rbl_flags("It has always been this way.")
        self.assertIn("static_over_motion", flags)


if __name__ == "__main__":
    unittest.main()
