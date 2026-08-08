#!/usr/bin/env python3
"""Write mediation controls — 20 tests, no database required."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.name != "maat_memory" else HERE.parent
# maat_memory/ is HERE when tests live beside modules; package root is parent
PKG_ROOT = HERE.parent if HERE.name == "maat_memory" else HERE.parents[1]
# test file is maat_memory/test_write_mediation.py → ROOT = maatlangchain
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from maat_memory.maat_provenance import ContentOrigin, ProvenanceError  # noqa: E402
from maat_memory.write_mediation import (  # noqa: E402
    MediatedWriter,
    MediationError,
    Principal,
    PrincipalKind,
    TokenRegistry,
    refuse_client_origin,
    resolve_write_origin,
    stamp_origin,
)


class TestWriteMediation(unittest.TestCase):
    def test_01_agent_stamps_agent_authored(self):
        p = Principal("cursor_x", PrincipalKind.AGENT)
        self.assertEqual(stamp_origin(p), ContentOrigin.AGENT_AUTHORED)

    def test_02_human_stamps_human_authored(self):
        p = Principal("imhotep", PrincipalKind.HUMAN)
        self.assertEqual(stamp_origin(p), ContentOrigin.HUMAN_AUTHORED)

    def test_03_system_stamps_system(self):
        p = Principal("write_service", PrincipalKind.SYSTEM)
        self.assertEqual(stamp_origin(p), ContentOrigin.SYSTEM_GENERATED)

    def test_04_empty_agent_id_refused(self):
        with self.assertRaises(MediationError):
            stamp_origin(Principal("", PrincipalKind.AGENT))

    def test_05_absent_claim_ok(self):
        stamped = ContentOrigin.AGENT_AUTHORED
        self.assertEqual(refuse_client_origin(None, stamped), stamped)

    def test_06_client_claim_human_refused(self):
        with self.assertRaises(ProvenanceError):
            refuse_client_origin("human_authored", ContentOrigin.AGENT_AUTHORED)

    def test_07_matching_claim_still_refused(self):
        # Client is not the mint — even agreeing is refused
        with self.assertRaises(ProvenanceError):
            refuse_client_origin("agent_authored", ContentOrigin.AGENT_AUTHORED)

    def test_08_resolve_write_origin_stamps(self):
        p = Principal("cursor_x", PrincipalKind.AGENT)
        self.assertEqual(resolve_write_origin(p), ContentOrigin.AGENT_AUTHORED)

    def test_09_resolve_with_claim_refuses(self):
        p = Principal("cursor_x", PrincipalKind.AGENT)
        with self.assertRaises(ProvenanceError):
            resolve_write_origin(p, claimed_origin="human_authored")

    def test_10_token_issue_and_resolve(self):
        with tempfile.TemporaryDirectory() as td:
            reg = TokenRegistry.load(Path(td) / "tokens.json", pepper="test-pepper")
            raw = reg.issue("cursor_staydangerous_data_drive")
            p = reg.resolve(raw)
            self.assertEqual(p.agent_id, "cursor_staydangerous_data_drive")
            self.assertEqual(p.kind, PrincipalKind.AGENT)

    def test_11_invalid_token_refused(self):
        with tempfile.TemporaryDirectory() as td:
            reg = TokenRegistry.load(Path(td) / "tokens.json", pepper="test-pepper")
            with self.assertRaises(MediationError):
                reg.resolve("not-a-real-token")

    def test_12_absent_token_refused(self):
        with tempfile.TemporaryDirectory() as td:
            reg = TokenRegistry.load(Path(td) / "tokens.json", pepper="test-pepper")
            with self.assertRaises(MediationError):
                reg.resolve(None)

    def test_13_token_file_chmod_600(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "tokens.json"
            reg = TokenRegistry.load(path, pepper="p")
            reg.issue("a")
            self.assertEqual(oct(path.stat().st_mode & 0o777), "0o600")

    def test_14_registry_persists_hash_not_raw(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "tokens.json"
            reg = TokenRegistry.load(path, pepper="p")
            raw = reg.issue("agent_a")
            stored = json.loads(path.read_text())
            blob = json.dumps(stored)
            self.assertNotIn(raw, blob)

    def test_15_mediated_writer_stamps(self):
        mem = MagicMock()
        mem.log_decision.return_value = "dec-1"
        p = Principal("cursor_x", PrincipalKind.AGENT)
        w = MediatedWriter(mem, p)
        did = w.log_decision("ctx", "dec", "why")
        self.assertEqual(did, "dec-1")
        args, kwargs = mem.log_decision.call_args
        self.assertEqual(args[0], "cursor_x")
        self.assertEqual(kwargs["origin"], "agent_authored")

    def test_16_mediated_writer_strips_client_origin_kw(self):
        mem = MagicMock()
        mem.log_task.return_value = "t-1"
        w = MediatedWriter(mem, Principal("cursor_x", PrincipalKind.AGENT))
        w.log_task("title", "desc", origin="human_authored")  # stripped
        _, kwargs = mem.log_task.call_args
        self.assertEqual(kwargs["origin"], "agent_authored")

    def test_17_writer_ignores_spoofed_agent_kw(self):
        mem = MagicMock()
        mem.log_task.return_value = "t-1"
        w = MediatedWriter(mem, Principal("real_agent", PrincipalKind.AGENT))
        w.log_task("t", "d", agent="evil_human")
        args, kwargs = mem.log_task.call_args
        self.assertEqual(args[0], "real_agent")

    def test_18_bearer_prefix_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            reg = TokenRegistry.load(Path(td) / "t.json", pepper="p")
            raw = reg.issue("a1")
            p = reg.resolve(f"Bearer {raw}")
            self.assertEqual(p.agent_id, "a1")

    def test_19_human_token_kind(self):
        with tempfile.TemporaryDirectory() as td:
            reg = TokenRegistry.load(Path(td) / "t.json", pepper="p")
            raw = reg.issue("imhotep", kind=PrincipalKind.HUMAN)
            self.assertEqual(reg.resolve(raw).stamped_origin(), ContentOrigin.HUMAN_AUTHORED)

    def test_20_agent_cannot_mint_human_via_claim(self):
        p = Principal("cursor_x", PrincipalKind.AGENT)
        with self.assertRaises(ProvenanceError):
            resolve_write_origin(p, claimed_origin="human_authored")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestWriteMediation)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ran = result.testsRun
    failed = len(result.failures) + len(result.errors)
    print(f"\n{ran - failed}/{ran} controls held")
    raise SystemExit(0 if result.wasSuccessful() and ran == 20 else 1)
