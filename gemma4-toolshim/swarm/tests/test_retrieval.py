"""Retrieval tests.

Covers:
    * tokenisation drops stopwords, lowercases, ignores 1-char tokens
    * BM25 ranks the chunk containing the query term higher than unrelated ones
    * ``format_context_block`` truncates to the character budget
    * fl-trust-law pack loads (real fixture) and surfaces FL-law hits
    * unknown pack returns no hits without raising
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

import retrieval  # noqa: E402


class TestTokeniser(unittest.TestCase):
    def test_drops_stopwords_and_lowercases(self) -> None:
        toks = retrieval._tokenise("The quick Brown Fox JUMPS")
        self.assertNotIn("the", toks)
        self.assertIn("quick", toks)
        self.assertIn("brown", toks)

    def test_ignores_single_chars(self) -> None:
        toks = retrieval._tokenise("a b c dog")
        self.assertEqual(toks, ["dog"])


class TestBM25Basics(unittest.TestCase):
    def _write_pack(self, tmp: Path, pack_id: str, chunks: list[dict]) -> None:
        chunks_dir = tmp / "data" / "retrieval_packs" / pack_id / "documents" / "rag" / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        with (chunks_dir / "chunks.jsonl").open("w", encoding="utf-8") as fh:
            for c in chunks:
                fh.write(json.dumps(c) + "\n")

    def test_ranks_matching_chunk_first(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._write_pack(
                tmp,
                "bm25-demo",
                [
                    {"chunk_index": 0, "text": "cats drink milk and sleep all day", "section_id": "1"},
                    {"chunk_index": 1, "text": "dogs bark at mailmen on the street", "section_id": "2"},
                    {"chunk_index": 2, "text": "birds fly south for the winter months", "section_id": "3"},
                ],
            )
            original = retrieval.PACKS_ROOT
            try:
                retrieval.PACKS_ROOT = tmp / "data" / "retrieval_packs"
                retrieval._PACK_CACHE.clear()
                retrieval._PACK_CHUNKS.clear()
                hits = retrieval.search("bm25-demo", "dogs bark street", top_k=3)
            finally:
                retrieval.PACKS_ROOT = original
                retrieval._PACK_CACHE.clear()
                retrieval._PACK_CHUNKS.clear()
            self.assertTrue(hits)
            self.assertEqual(hits[0].section_id, "2")


class TestContextFormatter(unittest.TestCase):
    def test_truncates_to_budget(self) -> None:
        hits = [
            retrieval.RetrievalHit(
                chunk_id=str(i),
                score=1.0 - i * 0.1,
                text="x" * 1000,
                source=f"src{i}.md",
            )
            for i in range(5)
        ]
        out = retrieval.format_context_block(hits, max_chars=500)
        self.assertLessEqual(len(out), 700)  # allow headers/newlines
        self.assertTrue(out)

    def test_empty_returns_empty(self) -> None:
        self.assertEqual(retrieval.format_context_block([]), "")


class TestFlPackLiveFixture(unittest.TestCase):
    """Relies on fl-trust-law pack being installed. Skipped otherwise."""

    def setUp(self) -> None:
        chunks_file = (
            retrieval.PACKS_ROOT
            / "fl-trust-law"
            / "documents"
            / "rag"
            / "chunks"
            / "chunks.jsonl"
        )
        if not chunks_file.is_file():
            self.skipTest("fl-trust-law pack not installed")

    def test_trust_query_returns_hits(self) -> None:
        retrieval._PACK_CACHE.clear()
        retrieval._PACK_CHUNKS.clear()
        hits = retrieval.search("fl-trust-law", "trust modification beneficiary", top_k=5)
        self.assertTrue(hits, "expected at least one hit for trust query")
        # Every returned hit must have text + score > 0.
        for h in hits:
            self.assertGreater(h.score, 0.0)
            self.assertTrue(h.text)


class TestUnknownPackIsSafe(unittest.TestCase):
    def test_returns_empty(self) -> None:
        self.assertEqual(retrieval.search("definitely-not-a-real-pack-abc123", "hello"), [])


if __name__ == "__main__":
    unittest.main()
