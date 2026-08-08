#!/usr/bin/env python3
"""Enrollment birth + chronology tests (no network organs required)."""

from __future__ import annotations

import os
import sys
import unittest
import uuid

_ML = "/mnt/data_drive/maatlangchain"
if _ML not in sys.path:
    sys.path.insert(0, _ML)

from maat_memory.memory_plane.enrollment import EnrollmentBirth, build_full_identity


class TestEnrollmentBirth(unittest.TestCase):
    def test_working_on_required(self):
        out = EnrollmentBirth().birth(working_on="  ", principal_id="imhotep")
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "working_on_required")

    def test_birth_chronology_identity(self):
        aid = f"cursor_test_birth_{uuid.uuid4().hex[:8]}"
        os.environ["MAAT_AGENT_ID"] = aid
        try:
            birth = EnrollmentBirth().birth(
                working_on="unit_test: birth+chronology",
                principal_id="imhotep",
                agent_id=aid,
                role="tester",
            )
            self.assertTrue(birth.get("ok"), birth)
            self.assertEqual(birth["principal_id"], "imhotep")
            self.assertEqual(birth["working_on"], "unit_test: birth+chronology")
            self.assertIn("full_identity", birth)
            fi = birth["full_identity"]
            self.assertEqual(fi["principal"]["principal_id"], "imhotep")
            self.assertEqual(fi["working_on"], "unit_test: birth+chronology")

            card = EnrollmentBirth().identity_card(agent_id=aid)
            self.assertTrue(card.get("ok"))
            self.assertEqual(card["birth_id"], birth["birth_id"])

            upd = EnrollmentBirth().update_work(aid, "unit_test: work_update")
            self.assertTrue(upd.get("ok"))
            chron = EnrollmentBirth().chronology(aid)
            types = [e["event_type"] for e in chron]
            self.assertIn("birth", types)
            self.assertIn("work_update", types)
        finally:
            os.environ.pop("MAAT_AGENT_ID", None)

    def test_build_identity_shape(self):
        card = build_full_identity(
            agent_id="a1",
            machine_id="m1",
            principal_id="imhotep",
            working_on="shape check",
        )
        self.assertEqual(card["schema"], "maat.enrollment.identity.v0")
        self.assertIn("principal", card)
        self.assertIn("machine", card)
        self.assertIn("workspace", card)


if __name__ == "__main__":
    unittest.main()
