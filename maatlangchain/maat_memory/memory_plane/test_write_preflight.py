"""Unit tests for storage write preflight (Host Body Awareness)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from maat_memory.memory_plane.write_preflight import (
    check_write,
    classify_path,
    infer_artifact_type,
    load_storage_law,
)


class WritePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.law = load_storage_law()

    def test_law_loads(self) -> None:
        self.assertIn("storage_roots", self.law)
        self.assertIn("cockpit", self.law["storage_roots"])
        self.assertIn("live_bulk", self.law["storage_roots"])

    def test_classify_cockpit_home(self) -> None:
        c = classify_path("/home/suspect/.n8n/docs/foo.md", self.law)
        self.assertEqual(c["mount_class"], "cockpit")

    def test_classify_data_drive(self) -> None:
        c = classify_path("/mnt/data_drive/hermes/pack.json", self.law)
        self.assertEqual(c["mount_class"], "live_bulk")

    def test_classify_model_home(self) -> None:
        c = classify_path("/mnt/ai_models/huggingface/foo", self.law)
        self.assertEqual(c["mount_class"], "model_home")

    def test_classify_backup(self) -> None:
        c = classify_path("/mnt/ai_backup/snapshots/x", self.law)
        self.assertEqual(c["mount_class"], "backup")

    def test_deny_large_cockpit_write(self) -> None:
        with patch(
            "maat_memory.memory_plane.write_preflight.disk_used_pct",
            return_value=80.0,
        ):
            r = check_write(
                "/home/suspect/.n8n/big.bin",
                estimated_size_mb=200,
                law=self.law,
            )
        self.assertEqual(r["decision"], "DENY_EVENT")
        self.assertFalse(r["ok"])

    def test_no_go_model_weight_on_cockpit(self) -> None:
        with patch(
            "maat_memory.memory_plane.write_preflight.disk_used_pct",
            return_value=50.0,
        ):
            r = check_write(
                "/home/suspect/.n8n/models/weights.gguf",
                estimated_size_mb=1,
                artifact_type="model_weight",
                law=self.law,
            )
        self.assertEqual(r["decision"], "NO_GO")

    def test_allow_small_cockpit_doc(self) -> None:
        with patch(
            "maat_memory.memory_plane.write_preflight.disk_used_pct",
            return_value=80.0,
        ):
            r = check_write(
                "/home/suspect/.n8n/docs/note.md",
                estimated_size_mb=0.1,
                law=self.law,
            )
        self.assertEqual(r["decision"], "ALLOW")
        self.assertTrue(r["ok"])

    def test_allow_bulk_on_data_drive(self) -> None:
        with patch(
            "maat_memory.memory_plane.write_preflight.disk_used_pct",
            return_value=49.0,
        ):
            r = check_write(
                "/mnt/data_drive/hermes/artifact.bin",
                estimated_size_mb=500,
                law=self.law,
            )
        self.assertEqual(r["decision"], "ALLOW")

    def test_infer_model_weight(self) -> None:
        t = infer_artifact_type(
            "/home/suspect/.n8n/models/foo.gguf", law=self.law
        )
        self.assertEqual(t, "model_weight")


if __name__ == "__main__":
    unittest.main()
