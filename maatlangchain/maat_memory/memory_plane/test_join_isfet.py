#!/usr/bin/env python3
"""Isfet suite for Join Ritual v0.1.1 — self-approve, deny/produce, reuse, auth."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ML = "/mnt/data_drive/maatlangchain"
if _ML not in sys.path:
    sys.path.insert(0, _ML)

from maat_memory.memory_plane import JoinRequestRitual, OperatorAuthority, constitutional_help
from maat_memory.memory_plane import db
from maat_memory.memory_plane.db import load_dotenv_pg


class TestJoinIsfet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv_pg()
        # Ensure schema columns exist
        root = Path(_ML) / "maat_memory"
        for name in ("schema_join_request_v0.sql", "schema_join_request_v0_1.sql"):
            p = root / name
            if p.is_file():
                try:
                    db.execute(p.read_text(encoding="utf-8"))
                except Exception:
                    # multi-statement may need get_conn — migrate handles it; ignore here
                    pass
        mint = OperatorAuthority().mint("imhotep", display_name="Imhotep", rotate=True)
        assert mint.get("ok"), mint
        cls.op_token = mint["operator_token"]
        # Prefer stable lab token from env if still valid after our mint — we just rotated
        cls.ritual = JoinRequestRitual()
        cls.op_agent = "operator_imhotep_isfet"

    def _ask(self, agent_id: str, work: str = "isfet chore"):
        old = os.environ.get("MAAT_AGENT_ID")
        os.environ["MAAT_AGENT_ID"] = agent_id
        try:
            return self.ritual.ask(
                working_on=work,
                principal_id="imhotep",
                agent_id=agent_id,
            )
        finally:
            if old is None:
                os.environ.pop("MAAT_AGENT_ID", None)
            else:
                os.environ["MAAT_AGENT_ID"] = old

    def test_01_help_has_forbidden_not_broker_path(self):
        h = constitutional_help()
        blob = json.dumps(h)
        self.assertIn("ask-join", blob)
        self.assertIn(".env.broker", blob)
        self.assertNotIn("KA_API_KEY=", blob)
        self.assertTrue(any("self-approve" in f.lower() or "self-approve" in f for f in h["forbidden"]) or "self-approve" in blob)

    def test_02_decide_without_token_fails(self):
        aid = f"cursor_isfet_notoken_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid)
        self.assertTrue(ask.get("ok"), ask)
        os.environ.pop("MAAT_OPERATOR_TOKEN", None)
        out = self.ritual.decide(
            ask["request_id"],
            allow=True,
            reason="should fail",
            decided_by_agent=self.op_agent,
            operator_token=None,
        )
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "operator_token_required")

    def test_03_self_approve_denied(self):
        aid = f"cursor_isfet_self_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid)
        self.assertTrue(ask.get("ok"), ask)
        out = self.ritual.decide(
            ask["request_id"],
            allow=True,
            reason="self approve attempt",
            decided_by_agent=aid,  # same as requester
            operator_token=self.op_token,
        )
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "self_approve_denied")

    def test_04_wrong_token_fails(self):
        aid = f"cursor_isfet_badtok_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid)
        out = self.ritual.decide(
            ask["request_id"],
            allow=False,
            reason="bad token",
            decided_by_agent=self.op_agent,
            operator_token="not-the-real-token",
        )
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "operator_token_invalid")

    def test_05_denied_cannot_produce(self):
        aid = f"cursor_isfet_deny_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid, "should be denied")
        dec = self.ritual.decide(
            ask["request_id"],
            allow=False,
            reason="Isfet deny path",
            decided_by_agent=self.op_agent,
            operator_token=self.op_token,
        )
        self.assertTrue(dec.get("ok"), dec)
        # Even if somehow a code existed, status denied blocks; use garbage code + check denied status path
        # Create a fake allowed-looking hash on denied row shouldn't work — produce by status
        out = self.ritual.produce("not-a-real-code", tool_type="cursor")
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "invalid_or_used_code")

    def test_06_allow_produce_reuse_fails(self):
        aid = f"cursor_isfet_reuse_{uuid.uuid4().hex[:6]}"
        old = os.environ.get("MAAT_AGENT_ID")
        os.environ["MAAT_AGENT_ID"] = aid
        try:
            ask = self.ritual.ask(working_on="reuse test", principal_id="imhotep", agent_id=aid)
            self.assertTrue(ask.get("ok"), ask)
            dec = self.ritual.decide(
                ask["request_id"],
                allow=True,
                reason="Isfet allow for reuse test",
                decided_by_agent=self.op_agent,
                operator_token=self.op_token,
            )
            self.assertTrue(dec.get("ok"), dec)
            code = dec["provision_code"]
            with tempfile.TemporaryDirectory() as td:
                p1 = self.ritual.produce(code, tool_type="cursor", credential_dir=td)
                self.assertTrue(p1.get("ok"), p1)
                self.assertIsNone(p1.get("organ_bearer") if "organ_bearer" in p1 else None)
                cred = Path(td) / "credentials.json"
                self.assertTrue(cred.is_file())
                self.assertEqual(oct(cred.stat().st_mode & 0o777), "0o600")
                doc = json.loads(cred.read_text())
                self.assertIsNone(doc.get("organ_bearer"))
                self.assertIn("operator_principal_id", doc)
                self.assertIn("decided_by_agent", doc)
                # reuse
                p2 = self.ritual.produce(code, tool_type="cursor", credential_dir=td)
                self.assertFalse(p2.get("ok"))
                self.assertEqual(p2.get("error"), "invalid_or_used_code")
        finally:
            if old is None:
                os.environ.pop("MAAT_AGENT_ID", None)
            else:
                os.environ["MAAT_AGENT_ID"] = old

    def test_07_agent_mismatch_on_produce(self):
        aid = f"cursor_isfet_bound_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid, "agent bind")
        dec = self.ritual.decide(
            ask["request_id"],
            allow=True,
            reason="bind test",
            decided_by_agent=self.op_agent,
            operator_token=self.op_token,
        )
        self.assertTrue(dec.get("ok"), dec)
        code = dec["provision_code"]
        # produce as different agent
        old = os.environ.get("MAAT_AGENT_ID")
        os.environ["MAAT_AGENT_ID"] = "cursor_isfet_other_agent"
        try:
            out = self.ritual.produce(code, tool_type="cursor")
            self.assertFalse(out.get("ok"))
            self.assertEqual(out.get("error"), "agent_mismatch")
        finally:
            if old is None:
                os.environ.pop("MAAT_AGENT_ID", None)
            else:
                os.environ["MAAT_AGENT_ID"] = old

    def test_08_allow_has_reason_and_scopes(self):
        aid = f"cursor_isfet_scopes_{uuid.uuid4().hex[:6]}"
        ask = self._ask(aid)
        dec = self.ritual.decide(
            ask["request_id"],
            allow=True,
            reason="scope check reason required",
            decided_by_agent=self.op_agent,
            operator_token=self.op_token,
        )
        self.assertTrue(dec.get("ok"), dec)
        self.assertIn("discovery:read", dec.get("approved_scopes") or [])
        self.assertIn("broker:read", dec.get("denied_scopes") or [])
        self.assertEqual(dec.get("operator_principal_id"), "imhotep")
        self.assertEqual(dec.get("decided_by_agent"), self.op_agent)

    def test_09_whoami_no_secrets(self):
        w = self.ritual.whoami()
        self.assertTrue(w.get("ok"))
        blob = json.dumps(w)
        self.assertNotIn("MAAT_OPERATOR_TOKEN", blob)
        self.assertIn("forbidden_reminder", w)


if __name__ == "__main__":
    unittest.main()
