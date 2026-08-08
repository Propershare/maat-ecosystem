"""Tests for ka2_router."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import ka2_router  # noqa: E402


class TestDetectors(unittest.TestCase):
    def test_casual_is_not_research_grade(self):
        rg, _ = ka2_router.detect_research_grade("hey can you just ping the status please")
        self.assertFalse(rg)

    def test_scout_expert_forces_research_grade(self):
        rg, _ = ka2_router.detect_research_grade("list files in /tmp", expert_name="scout")
        self.assertTrue(rg)

    def test_two_signals_trip_research_grade(self):
        rg, hits = ka2_router.detect_research_grade(
            "compare the history of A and B with a proper analysis"
        )
        self.assertTrue(rg, f"expected research_grade, hits={hits}")

    def test_level_defaults_to_system(self):
        level, _ = ka2_router.detect_level_of_analysis("what about it")
        self.assertEqual(level, "system")

    def test_level_picks_group(self):
        level, _ = ka2_router.detect_level_of_analysis("study this group in the community")
        self.assertEqual(level, "group")

    def test_level_picks_institution(self):
        level, _ = ka2_router.detect_level_of_analysis(
            "the court and the ministry and the university"
        )
        self.assertEqual(level, "institution")

    def test_research_type_historical(self):
        rtype, _ = ka2_router.detect_research_type("history of the city through the years")
        self.assertEqual(rtype, "historical")

    def test_research_type_comparative(self):
        rtype, _ = ka2_router.detect_research_type("compare A versus B")
        self.assertEqual(rtype, "comparative")


class TestRoute(unittest.TestCase):
    def test_route_returns_correlation_id(self):
        d = ka2_router.route(
            "Archivist: persist this record.", session_id="s1", turn_index=3
        )
        self.assertEqual(d.correlation_id, "s1:0003")
        self.assertEqual(d.expert_name, "archivist")
        self.assertTrue(d.research_grade)

    def test_route_tags_shape(self):
        d = ka2_router.route(
            "Analyze the history of Kemetic institutions",
            session_id="s1",
            turn_index=0,
        )
        self.assertIn("expert:" + d.expert_name, d.tags)
        self.assertTrue(any(t.startswith("level:") for t in d.tags))
        self.assertTrue(any(t.startswith("research_type:") for t in d.tags))
        self.assertIn("research_grade:true", d.tags)

    def test_override_expert_forces_selection(self):
        d = ka2_router.route(
            "Write me a Python script that sorts numbers.",
            session_id="s1",
            turn_index=0,
            override_expert="archivist",
        )
        self.assertEqual(d.expert_name, "archivist")
        self.assertIn("route:override", d.tags)

    def test_fallback_tag_on_unknown_message(self):
        d = ka2_router.route(
            "xyzzy plugh blarg",
            session_id="s1",
            turn_index=0,
        )
        self.assertIn("route:fallback", d.tags)


if __name__ == "__main__":
    unittest.main()
