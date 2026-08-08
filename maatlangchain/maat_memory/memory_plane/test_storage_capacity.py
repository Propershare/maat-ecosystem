#!/usr/bin/env python3
"""Storage capacity consciousness — unit tests (mocked disk_usage)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from maat_memory.memory_plane.storage import (  # noqa: E402
    DEFAULT_STORAGE_FULL_PCT,
    StorageAwareness,
    StorageCapacityError,
)


class TestStorageCapacity(unittest.TestCase):
    def _awareness(self, roots_rows, machine_roots=None):
        reg = MagicMock()
        reg.enroll_machine.return_value = {"machine_id": "m1"}
        reg.get_machine.return_value = {
            "machine_id": "m1",
            "storage_roots": machine_roots or {},
            "status": "enrolled",
        }
        sa = StorageAwareness(reg)
        return sa, roots_rows

    def test_01_default_threshold_92(self):
        sa = StorageAwareness(MagicMock())
        with patch.dict("os.environ", {}, clear=False):
            # remove if set
            import os

            os.environ.pop("MAAT_STORAGE_FULL_PCT", None)
            self.assertEqual(sa.full_pct_threshold(), DEFAULT_STORAGE_FULL_PCT)

    def test_02_no_declared_roots_deny(self):
        sa, _ = self._awareness([])
        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=[]):
            out = sa.check_capacity("m1")
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "no_declared_roots")

    def test_03_unmeasured_deny(self):
        rows = [
            {
                "root_id": "r1",
                "storage_class": "artifact",
                "base_uri": "file:///no/such/path/zzz",
                "machine_id": "m1",
            }
        ]
        sa, _ = self._awareness(rows)
        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=rows):
            with patch.object(Path, "exists", return_value=False):
                out = sa.check_capacity("m1")
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "capacity_unmeasured")

    def test_04_over_threshold_deny(self):
        rows = [
            {
                "root_id": "r1",
                "storage_class": "artifact",
                "base_uri": "file:///tmp",
                "machine_id": "m1",
            }
        ]
        sa, _ = self._awareness(rows)
        usage = MagicMock(total=100, used=95, free=5)

        class U:
            total, used, free = 100, 95, 5

        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=rows):
            with patch("maat_memory.memory_plane.storage.shutil.disk_usage", return_value=U):
                out = sa.check_capacity("m1")
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "all_roots_full")

    def test_05_under_threshold_allow(self):
        rows = [
            {
                "root_id": "r1",
                "storage_class": "artifact",
                "base_uri": "file:///tmp",
                "machine_id": "m1",
            }
        ]
        sa, _ = self._awareness(rows)

        class U:
            total, used, free = 100, 40, 60

        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=rows):
            with patch("maat_memory.memory_plane.storage.shutil.disk_usage", return_value=U):
                out = sa.check_capacity("m1")
        self.assertTrue(out["ok"])
        self.assertIsNotNone(out["preferred_root"])

    def test_06_prefer_data_drive(self):
        rows = [
            {
                "root_id": "rootish",
                "storage_class": "coordination",
                "base_uri": "file:///tmp",
                "machine_id": "m1",
            },
            {
                "root_id": "dd",
                "storage_class": "artifact",
                "base_uri": "file:///mnt/data_drive/hermes",
                "machine_id": "m1",
            },
        ]
        sa, _ = self._awareness(rows)

        def fake_usage(path):
            class U:
                pass

            u = U()
            p = str(path)
            if "data_drive" in p:
                u.total, u.used, u.free = 1000, 400, 600
            else:
                u.total, u.used, u.free = 1000, 400, 600
            return u

        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=rows):
            with patch(
                "maat_memory.memory_plane.storage.shutil.disk_usage", side_effect=fake_usage
            ):
                with patch.object(Path, "exists", return_value=True):
                    out = sa.check_capacity("m1")
        self.assertTrue(out["ok"])
        pref = (out.get("preferred_root") or {}).get("probe") or ""
        self.assertIn("data_drive", pref)

    def test_07_assert_capacity_raises(self):
        sa, _ = self._awareness([])
        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=[]):
            with self.assertRaises(StorageCapacityError):
                sa.assert_capacity("m1")

    def test_08_env_threshold_override(self):
        sa = StorageAwareness(MagicMock())
        with patch.dict("os.environ", {"MAAT_STORAGE_FULL_PCT": "50"}):
            self.assertEqual(sa.full_pct_threshold(), 50.0)

    def test_09_unset_env_still_checks(self):
        """Absence of MAAT_STORAGE_FULL_PCT does not skip — default applies."""
        sa = StorageAwareness(MagicMock())
        import os

        os.environ.pop("MAAT_STORAGE_FULL_PCT", None)
        self.assertEqual(sa.full_pct_threshold(), 92.0)

    def test_10_machine_soft_roots_counted(self):
        sa, _ = self._awareness([], machine_roots={"cwd": "/tmp"})

        class U:
            total, used, free = 100, 10, 90

        with patch("maat_memory.memory_plane.storage.db.fetchall", return_value=[]):
            with patch("maat_memory.memory_plane.storage.shutil.disk_usage", return_value=U):
                out = sa.check_capacity("m1")
        self.assertTrue(out["ok"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestStorageCapacity)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ran = result.testsRun
    failed = len(result.failures) + len(result.errors)
    print(f"\n{ran - failed}/{ran} controls held")
    raise SystemExit(0 if result.wasSuccessful() else 1)
