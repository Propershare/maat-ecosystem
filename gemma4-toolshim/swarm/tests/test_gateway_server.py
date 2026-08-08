"""Tests for gateway_server GatewayService.

The tests drive ``GatewayService`` directly (not over HTTP) so they stay
fast and offline. The Ollama dispatch is monkeypatched to avoid network.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent.parent))

import archivist_gitmaat as ag  # noqa: E402
import gateway_server as gs  # noqa: E402


class TestGatewayService(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        stream = Path(self.tmp.name) / "records.jsonl"
        self.service = gs.GatewayService()
        self.service.adapter = ag.ArchivistGitMaatAdapter(
            stream_path=stream,
            enable_gitmaat=False,
            agent_id="test-gateway",
        )

    def _fake_ollama(self, text: str = "ok reply"):
        return {
            "ok": True,
            "text": text,
            "model": "gemma4:e4b",
            "latency_ms": 42,
            "eval_count": 9,
        }

    def test_describe_reports_registry(self):
        d = self.service.describe()
        self.assertEqual(d["service"], "maat-gateway-server")
        self.assertIn("scout", d["registry_gateways"])
        self.assertIn("fl-trust-law", d["registry_gateways"])

    def test_ask_produces_structured_result(self):
        with mock.patch.object(gs, "_ollama_generate", return_value=self._fake_ollama("hello back")):
            result = self.service.ask(
                message="quick hello",
                session_id="sess-1",
            )
        self.assertEqual(result["reply"], "hello back")
        self.assertIn(result["gateway"], {"scout", None, "ka2-research"})
        self.assertIsNotNone(result["correlation_id"])
        self.assertEqual(result["turn_index"], 0)
        self.assertIn(result["decision"]["decision"], {"allow", "deny", "review"})
        self.assertEqual(result["persist"]["gitmaat_status"], "disabled")

    def test_ask_gateway_id_selects_gateway(self):
        with mock.patch.object(gs, "_ollama_generate", return_value=self._fake_ollama()):
            result = self.service.ask(
                message="Florida trust question",
                gateway_id="fl-trust-law",
                session_id="sess-2",
            )
        self.assertEqual(result["gateway"], "fl-trust-law")

    def test_ask_unknown_gateway_raises(self):
        with self.assertRaises(KeyError):
            self.service.ask(
                message="anything",
                gateway_id="does-not-exist",
                session_id="sess-3",
            )

    def test_ask_turn_indices_increment_per_session(self):
        with mock.patch.object(gs, "_ollama_generate", return_value=self._fake_ollama()):
            r1 = self.service.ask(message="one", session_id="sess-inc")
            r2 = self.service.ask(message="two", session_id="sess-inc")
            r3 = self.service.ask(message="three", session_id="other")
        self.assertEqual(r1["turn_index"], 0)
        self.assertEqual(r2["turn_index"], 1)
        self.assertEqual(r3["turn_index"], 0)

    def test_ask_handles_ollama_unreachable(self):
        with mock.patch.object(
            gs,
            "_ollama_generate",
            return_value={"ok": False, "error": "ollama_unreachable: refused", "latency_ms": 1},
        ):
            result = self.service.ask(
                message="hello",
                session_id="sess-err",
            )
        self.assertEqual(result["reply"], "")
        self.assertIn("ollama_unreachable", result["model_error"])
        self.assertIn("model_error:ollama_unreachable", result["tags"])

    def test_ask_research_grade_produces_ka2_and_scorecard(self):
        with mock.patch.object(gs, "_ollama_generate", return_value=self._fake_ollama("a thorough answer with sources cited")):
            result = self.service.ask(
                message="Analyze the history of Kemetic institutional formation.",
                session_id="sess-research",
            )
        self.assertTrue(result["research_grade"])
        decision = result["decision"]
        self.assertIsNotNone(decision["scorecard"])
        self.assertEqual(decision["scorecard"]["schema"], "maat.ka2_scorecard.v1")
        self.assertEqual(decision["scorecard"]["pass_at"], 40)


class TestRAGIntegration(unittest.TestCase):
    """Asks via the fl-trust-law gateway and asserts retrieval fired."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        stream = Path(self.tmp.name) / "records.jsonl"
        self.service = gs.GatewayService()
        self.service.adapter = ag.ArchivistGitMaatAdapter(
            stream_path=stream,
            enable_gitmaat=False,
            agent_id="test-gateway",
        )
        chunks_file = (
            gs.retrieval.PACKS_ROOT
            / "fl-trust-law"
            / "documents"
            / "rag"
            / "chunks"
            / "chunks.jsonl"
        )
        if not chunks_file.is_file():
            self.skipTest("fl-trust-law pack not installed")

    def test_pack_gateway_injects_context_and_file_sources(self):
        captured = {}

        def _spy(model, prompt, system=None):
            captured["prompt"] = prompt
            return {"ok": True, "text": "answer with [1] citation", "model": model, "latency_ms": 1, "eval_count": 1}

        with mock.patch.object(gs, "_ollama_generate", side_effect=_spy):
            result = self.service.ask(
                message="trust modification beneficiary consent",
                gateway_id="fl-trust-law",
                session_id="sess-rag",
            )

        self.assertIn("CONTEXT:", captured["prompt"])
        self.assertIn("QUESTION:", captured["prompt"])
        self.assertEqual(result["gateway"], "fl-trust-law")
        # The persisted record must include excerpts in its payload.
        import json as _json
        stream_path = self.service.adapter.stream_path
        with open(stream_path, encoding="utf-8") as fh:
            rows = [_json.loads(l) for l in fh if l.strip()]
        self.assertTrue(rows)
        last = rows[-1]
        sources = last["sources"]
        file_sources = [s for s in sources if s["kind"] == "file"]
        self.assertTrue(file_sources, "expected at least one file source from retrieval")
        self.assertTrue(
            any("fl-trust-law" in s["ref"] for s in file_sources),
            "expected ref to include pack id",
        )
        excerpts = last.get("payload", {}).get("retrieved_excerpts", [])
        self.assertTrue(excerpts, "expected retrieved_excerpts in payload")


class TestInfoEndpointShape(unittest.TestCase):
    def test_info_payload_mentions_channel_agnostic(self):
        self.assertTrue(gs._INFO_PAYLOAD["channel_agnostic"])
        self.assertIn("POST /ask", gs._INFO_PAYLOAD["endpoints"])


if __name__ == "__main__":
    unittest.main()
