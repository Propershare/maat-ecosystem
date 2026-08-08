"""End-to-end smoke test: fl-trust-law pack wired to a KA2-compliant gateway.

This is the integration checkpoint for todo #12 of the
`maat_evolving_expert_gateways` plan: we verify the mechanism, not the
content. If this test stays green, the pack plumbing works the same way
it would for any other pack we drop in later.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import gateway_registry as greg  # noqa: E402


LAB_ROOT = _HERE.parents[3]
PACK_DIR = LAB_ROOT / "data" / "retrieval_packs" / "fl-trust-law"


class TestFLPackAttached(unittest.TestCase):
    def test_gateway_declared_in_registry(self):
        reg = greg.GatewayRegistry.load()
        entry = reg.get("fl-trust-law")
        self.assertIsNotNone(entry, "fl-trust-law gateway missing from registry")
        assert entry is not None
        self.assertIn("fl-trust-law", entry.retrieval_packs)
        self.assertEqual(entry.archivist_schema, "maat.archivist_record.v1")
        self.assertEqual(entry.research_type_default, "applied")

    def test_pack_dir_has_manifest_and_readme(self):
        self.assertTrue(PACK_DIR.is_dir(), f"pack dir missing: {PACK_DIR}")
        self.assertTrue((PACK_DIR / "manifest.json").is_file())
        self.assertTrue((PACK_DIR / "README.md").is_file())
        self.assertTrue((PACK_DIR / "scripts" / "install.sh").is_file())

    def test_manifest_is_well_formed(self):
        manifest = json.loads((PACK_DIR / "manifest.json").read_text())
        self.assertEqual(manifest["schema"], "maat.retrieval_pack.v1")
        self.assertEqual(manifest["id"], "fl-trust-law")
        self.assertIn("aggregate_sha256", manifest)
        self.assertEqual(manifest["source"]["path"], "Legal_AI_FL.rar")
        self.assertIn("fl-trust-law", manifest["bound_gateways"])

    def test_installed_documents_visible_if_present(self):
        """If the install script has been run, basic structure exists.
        If it has not, we do not fail — CI may not have ``unrar`` available.
        """
        docs = PACK_DIR / "documents"
        if not docs.is_dir():
            self.skipTest("documents/ not extracted (run scripts/install.sh)")
        self.assertTrue((docs / "law_data_clean").is_dir())
        file_count = sum(1 for _ in docs.rglob("*") if _.is_file())
        self.assertGreater(file_count, 10)


if __name__ == "__main__":
    unittest.main()
