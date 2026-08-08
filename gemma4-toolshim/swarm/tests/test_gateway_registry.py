"""Tests for gateway_registry."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import gateway_registry as reg  # noqa: E402


SAMPLE_YAML = """\
gateways:
  - id: alpha
    description: Test gateway
    default_expert: scout
    archivist_schema: maat.archivist_record.v1
    research_type_default: historical
    level_of_analysis_default: system
    model: ollama/test
    retrieval_packs:
      - pack-one
      - pack-two
    tools:
      - read_file
    preset_file: openclaw/presets/alpha/preset.json5
  - id: bravo
    description: Second gateway
    default_expert: analyst
    archivist_schema: maat.archivist_record.v1
    research_type_default: descriptive
    level_of_analysis_default: institution
    model: ollama/test
    retrieval_packs: []
    tools:
      - read_file
"""


class TestGatewayRegistry(unittest.TestCase):
    def test_load_from_path(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "registry.yaml"
            path.write_text(SAMPLE_YAML)
            r = reg.GatewayRegistry.load(path)
            self.assertEqual(r.list_ids(), ["alpha", "bravo"])
            alpha = r.get("alpha")
            self.assertIsNotNone(alpha)
            assert alpha is not None
            self.assertEqual(alpha.default_expert, "scout")
            self.assertEqual(alpha.retrieval_packs, ["pack-one", "pack-two"])
            self.assertEqual(alpha.tools, ["read_file"])

    def test_add_and_upsert(self):
        r = reg.GatewayRegistry()
        r.add(reg.GatewayEntry(id="g1", default_expert="scout"))
        with self.assertRaises(KeyError):
            r.add(reg.GatewayEntry(id="g1", default_expert="scout"))
        r.upsert(reg.GatewayEntry(id="g1", default_expert="archivist"))
        self.assertEqual(r.get("g1").default_expert, "archivist")

    def test_canonical_registry_parses(self):
        r = reg.GatewayRegistry.load()
        self.assertIn("ka2-research", r.list_ids())
        self.assertIn("fl-trust-law", r.list_ids())

    def test_check_preset_files_reports_missing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.yaml"
            path.write_text(
                "gateways:\n"
                "  - id: g1\n"
                "    preset_file: does/not/exist.json5\n"
            )
            r = reg.GatewayRegistry.load(path)
            missing = r.check_preset_files()
            self.assertEqual(len(missing), 1)
            self.assertEqual(missing[0][0], "g1")


if __name__ == "__main__":
    unittest.main()
