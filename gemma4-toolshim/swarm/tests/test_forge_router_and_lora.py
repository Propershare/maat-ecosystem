"""Tests for router + LoRA forge paths."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import ka2_router  # noqa: E402
from forge import base as fbase  # noqa: E402
from forge import router_proposals as rp  # noqa: E402
from forge import lora_pipeline as lp  # noqa: E402
import gateway_contract as gc  # noqa: E402


class TestRouterProposals(unittest.TestCase):
    def test_add_and_remove_expert_keyword(self):
        experts = [
            {"name": "scout", "keywords": ["find", "locate"]},
            {"name": "analyst", "keywords": ["decide"]},
        ]
        tables = {
            "RESEARCH_GRADE_SIGNALS": list(ka2_router.RESEARCH_GRADE_SIGNALS),
            "CASUAL_SIGNALS": list(ka2_router.CASUAL_SIGNALS),
        }
        cand_add = rp.propose_add_keyword(
            gateway_id="ka2-research",
            expert_name="scout",
            table="expert_keywords",
            words=["grep"],
        )
        exps_after, _ = rp.apply_router(cand_add, experts=experts, tables=tables)
        scout = next(e for e in exps_after if e["name"] == "scout")
        self.assertIn("grep", scout["keywords"])

        cand_rm = rp.propose_remove_keyword(
            gateway_id="ka2-research",
            expert_name="scout",
            table="expert_keywords",
            words=["locate"],
        )
        exps_after2, _ = rp.apply_router(cand_rm, experts=experts, tables=tables)
        scout = next(e for e in exps_after2 if e["name"] == "scout")
        self.assertNotIn("locate", scout["keywords"])

    def test_table_change_is_isolated(self):
        experts = []
        tables = {
            "RESEARCH_GRADE_SIGNALS": list(ka2_router.RESEARCH_GRADE_SIGNALS),
            "CASUAL_SIGNALS": list(ka2_router.CASUAL_SIGNALS),
        }
        cand = rp.propose_add_keyword(
            gateway_id="ka2-research",
            expert_name=None,
            table="RESEARCH_GRADE_SIGNALS",
            words=["sankofa analysis"],
        )
        _, tables_after = rp.apply_router(cand, experts=experts, tables=tables)
        self.assertIn("sankofa analysis", tables_after["RESEARCH_GRADE_SIGNALS"])
        self.assertNotIn(
            "sankofa analysis", ka2_router.RESEARCH_GRADE_SIGNALS,
            "applying a candidate must not mutate the live module table",
        )


class TestLoraDatasetFilter(unittest.TestCase):
    def _record(self, **overrides):
        scorecard = gc.MaatScorecard(
            scores=dict(truth=9, order=9, balance=9, justice=9, self_reflection=9)
        )
        rec = gc.build_record(
            correlation_id=gc.make_correlation_id("s", 1),
            agent_id="cursor_test",
            gateway_id="ka2-research",
            summary="clean",
            sources=[gc.Source(kind="file", ref="/tmp/x")],
            tags=["tag:archivist:approved"],
            research_grade=True,
            ka2={
                "research_type": "historical",
                "problem": "t",
                "time_dimension": "t",
                "level_of_analysis": "system",
                "life_cycle": {"contradictions": ["a"]},
            },
            scorecard=scorecard,
            content_text="neutral sentence.",
        ).to_dict()
        rec.update(overrides)
        return rec

    def test_clean_record_is_eligible(self):
        ok, reason = lp.is_training_eligible(self._record())
        self.assertTrue(ok, reason)

    def test_non_research_record_dropped(self):
        rec = self._record(research_grade=False)
        ok, reason = lp.is_training_eligible(rec)
        self.assertFalse(ok)
        self.assertEqual(reason, "not_research_grade")

    def test_rbl_flag_drops(self):
        rec = self._record(rbl_flags=["static_over_motion"])
        ok, reason = lp.is_training_eligible(rec)
        self.assertFalse(ok)
        self.assertEqual(reason, "rbl_flags_present")

    def test_missing_approval_tag_drops(self):
        rec = self._record(tags=["domain:x"])
        ok, reason = lp.is_training_eligible(rec)
        self.assertFalse(ok)
        self.assertEqual(reason, "missing_archivist_approval_tag")

    def test_build_dataset_filters_stream(self):
        with tempfile.TemporaryDirectory() as td:
            stream = Path(td) / "records.jsonl"
            out = Path(td) / "dataset.jsonl"
            rows = [
                self._record(),
                self._record(research_grade=False),
                self._record(rbl_flags=["static_over_motion"]),
                self._record(tags=["domain:x"]),
            ]
            with stream.open("w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r) + "\n")
            path, report, digest = lp.build_dataset(
                stream_path=stream,
                out_path=out,
            )
            self.assertEqual(report.total_seen, 4)
            self.assertEqual(report.kept, 1)
            self.assertTrue(path.exists())
            self.assertEqual(len(digest), 64)


class TestLoraRunFinetuneDryRun(unittest.TestCase):
    def test_dry_run_builds_command_without_executing(self):
        cand = lp.propose_lora(
            gateway_id="ka2-research",
            expert_name="scout",
            base_model="unsloth/llama-3.1-8b-Instruct",
            dataset_path="/tmp/ds.jsonl",
            dataset_hash="abc" * 10,
            adapter_out="/tmp/out",
        )
        result = lp.run_finetune(cand, dry_run=True)
        self.assertTrue(result["ok"])
        self.assertIn("--dataset", result["cmd"])
        self.assertIn("/tmp/ds.jsonl", result["cmd"])


if __name__ == "__main__":
    unittest.main()
