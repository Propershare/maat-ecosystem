"""Tests for the post-turn Guard validator. No network required."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import gateway_contract as gc  # noqa: E402
import guard_validator as gv  # noqa: E402


def _research_record(total: int = 45) -> gc.ArchivistRecord:
    per_axis = max(0, min(10, total // 5))
    card = gc.MaatScorecard(
        scores=dict(
            truth=per_axis,
            order=per_axis,
            balance=per_axis,
            justice=per_axis,
            self_reflection=total - 4 * per_axis,
        )
    )
    ka2 = {
        "research_type": "historical",
        "problem": "test",
        "time_dimension": "test",
        "level_of_analysis": "system",
        "life_cycle": {"contradictions": ["a"]},
    }
    return gc.build_record(
        correlation_id=gc.make_correlation_id("s", 1),
        agent_id="cursor_test",
        gateway_id="ka2-research",
        summary="t",
        sources=[gc.Source(kind="file", ref="/tmp/x")],
        research_grade=True,
        ka2=ka2,
        scorecard=card,
        content_text="Neutral factual sentence.",
    )


class TestGuardValidator(unittest.TestCase):
    def test_allow_on_healthy_record(self):
        d = gv.validate_turn(_research_record(total=45), call_guard_http=False)
        self.assertEqual(d.decision, "allow")
        self.assertEqual(d.next_action, "proceed")
        self.assertEqual(d.reasons, [])

    def test_review_on_low_scorecard(self):
        d = gv.validate_turn(_research_record(total=35), call_guard_http=False)
        self.assertEqual(d.decision, "review")
        self.assertTrue(any("scorecard_fail" in r for r in d.reasons))
        self.assertEqual(d.next_action, "reroute_deeper_model")

    def test_deny_on_three_rbl_flags(self):
        rec = _research_record()
        d = gv.validate_turn(
            rec,
            content_text=(
                "It has always been this way. "
                "Humans progress steadily. "
                "Universal truth: an isolated incident explains everything."
            ),
            call_guard_http=False,
        )
        self.assertEqual(d.decision, "deny")
        self.assertEqual(d.next_action, "halt")
        self.assertTrue(any(r.startswith("rbl_halt") for r in d.reasons))

    def test_review_on_forbidden_hit(self):
        rec = _research_record()
        d = gv.validate_turn(
            rec,
            content_text="let us delve into this",
            call_guard_http=False,
        )
        self.assertEqual(d.decision, "review")
        self.assertTrue(any(r.startswith("forbidden_hits") for r in d.reasons))

    def test_research_grade_without_ka2_triggers_review(self):
        card = gc.MaatScorecard(
            scores=dict(truth=9, order=9, balance=9, justice=9, self_reflection=9)
        )
        rec = gc.build_record(
            correlation_id=gc.make_correlation_id("s", 1),
            agent_id="cursor_test",
            gateway_id="ka2-research",
            summary="t",
            sources=[gc.Source(kind="file", ref="/tmp/x")],
            research_grade=True,
            ka2=None,
            scorecard=card,
            content_text="ok",
        )
        d = gv.validate_turn(rec, call_guard_http=False)
        self.assertEqual(d.decision, "review")
        self.assertIn("ka2_header_missing", d.reasons)

    def test_scorecard_is_recomputed_authoritatively(self):
        rec = _research_record(total=45)
        d = gv.validate_turn(rec, call_guard_http=False)
        self.assertIsNotNone(d.scorecard)
        self.assertEqual(d.scorecard["pass_at"], gc.PASS_AT)
        self.assertTrue(d.scorecard["passed"])

    def test_guard_http_flag_off_leaves_unprobed(self):
        d = gv.validate_turn(_research_record(), call_guard_http=False)
        self.assertEqual(d.guard_http_status, "unprobed")


if __name__ == "__main__":
    unittest.main()
