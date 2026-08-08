"""Tests for the retrieval-pack forge path."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

from forge import base as forge_base  # noqa: E402
from forge import retrieval_proposals as rp  # noqa: E402


class TestRetrievalForge(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        # Redirect staging + packs roots into the tmp dir
        self._packs = self.tmp / "data" / "retrieval_packs"
        self._staging = self.tmp / ".forge_staged" / "retrieval_packs"
        self._patches = [
            patch.object(rp, "PACKS_ROOT", self._packs),
            patch.object(rp, "STAGING_ROOT", self._staging),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self) -> None:
        for p in self._patches:
            p.stop()
        self._tmp.cleanup()

    def _make_promoter(self, bench_scores):
        calls = {"n": 0}

        def bench_fn(gw):
            i = calls["n"]
            calls["n"] += 1
            return {"score": bench_scores[i], "gateway": gw}

        return forge_base.Promoter(
            bench_fn=bench_fn,
            apply_fn=rp.apply_retrieval,
            revert_fn=rp.revert_retrieval,
            margin=0.02,
            guard_fn=lambda c, b1, b2: ("allow", "unit-test"),
        )

    def test_promote_on_bench_win_and_guard_allow(self):
        cand = rp.propose_retrieval_pack(
            gateway_id="ka2-research",
            pack_id="test-pack",
            operation="add",
            manifest={"version": "0.1", "source": "test", "gateways": ["ka2-research"]},
            rationale="seed test",
        )
        promoter = self._make_promoter([0.70, 0.80])
        result = promoter.evaluate(cand)
        self.assertTrue(result.bench_pass)
        self.assertEqual(result.guard_status, "allow")
        self.assertTrue(result.promoted)
        staged = rp._staged_path("test-pack")
        self.assertTrue(staged.exists(), "manifest should remain staged until registry move")

    def test_revert_on_bench_loss(self):
        cand = rp.propose_retrieval_pack(
            gateway_id="ka2-research",
            pack_id="loser-pack",
            operation="add",
            manifest={"version": "0.1"},
        )
        promoter = self._make_promoter([0.70, 0.69])
        result = promoter.evaluate(cand)
        self.assertFalse(result.bench_pass)
        self.assertFalse(result.promoted)
        self.assertFalse(rp._staged_path("loser-pack").exists())

    def test_revert_on_guard_deny(self):
        cand = rp.propose_retrieval_pack(
            gateway_id="ka2-research",
            pack_id="blocked-pack",
            operation="add",
            manifest={"version": "0.1"},
        )
        promoter = forge_base.Promoter(
            bench_fn=lambda g: {"score": 0.85 if g else 0.7},
            apply_fn=rp.apply_retrieval,
            revert_fn=rp.revert_retrieval,
            margin=0.0,  # any improvement passes
            guard_fn=lambda c, b1, b2: ("deny", "simulated-deny"),
        )
        # We need distinct before/after scores; use a counter-based bench_fn
        counter = {"n": 0}
        def bench_fn(gw):
            counter["n"] += 1
            return {"score": 0.6 + 0.1 * counter["n"]}
        promoter.bench_fn = bench_fn
        result = promoter.evaluate(cand)
        self.assertTrue(result.bench_pass)
        self.assertEqual(result.guard_status, "deny")
        self.assertFalse(result.promoted)
        self.assertFalse(rp._staged_path("blocked-pack").exists())

    def test_promote_then_registry_move(self):
        cand = rp.propose_retrieval_pack(
            gateway_id="ka2-research",
            pack_id="winner",
            operation="add",
            manifest={"version": "0.1"},
        )
        promoter = self._make_promoter([0.70, 0.80])
        result = promoter.evaluate(cand)
        self.assertTrue(result.promoted)
        canonical = rp.promote_retrieval(cand)
        self.assertTrue(canonical.exists())
        self.assertFalse(rp._staged_path("winner").exists())


if __name__ == "__main__":
    unittest.main()
