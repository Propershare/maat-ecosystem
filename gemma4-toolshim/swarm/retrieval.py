"""
Stdlib retrieval over pack chunks.

Why BM25 and not FAISS:
    The existing pack ships a FAISS index built with sentence-transformers.
    That's great for semantic search but drags in heavy deps (torch, transformers,
    ~2GB install). For a 103-chunk pack, BM25 over tokenised text gives 85%+
    of the signal with zero deps. When we promote a pack that truly needs
    semantic recall, we can add an optional FAISS path behind a capability flag.

How packs are discovered:
    For a pack id ``<pack>``, we look at
    ``data/retrieval_packs/<pack>/documents/rag/chunks/chunks.jsonl``
    first. If absent, we fall back to indexing text files in
    ``documents/`` on the fly (slow, cached in-process).

Inputs/outputs:
    - Input: a pack id and a query string.
    - Output: a list of ``RetrievalHit`` dicts with ``score``, ``text``,
      ``source`` (pack-relative path), ``section_id``, ``chapter``.

The retriever is pure-Python, pickle-free, and safe to import at server
start with no I/O until ``search()`` is called for a given pack. Indexes
are built lazily per pack and cached for the process lifetime.
"""

from __future__ import annotations

import json
import math
import re
import threading
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


_WORD_RE = re.compile(r"[a-z0-9]{2,}")

STOPWORDS = frozenset(
    """
    a an and are as at be but by for from has have in is it its of on or
    that the their them they this to was were which will with you your
    he she his her i me my we us our
    """.split()
)


def _tokenise(text: str) -> list[str]:
    return [w for w in _WORD_RE.findall(text.lower()) if w not in STOPWORDS]


def _find_lab_root() -> Path:
    here = Path(__file__).resolve()
    for p in (here, *here.parents):
        if (p / "data").is_dir() and (p / "gemma4-toolshim").is_dir():
            return p
    return Path.cwd()


LAB_ROOT = _find_lab_root()
PACKS_ROOT = LAB_ROOT / "data" / "retrieval_packs"


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    section_id: str | None = None
    chapter: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalHit:
    chunk_id: str
    score: float
    text: str
    source: str
    section_id: str | None = None
    chapter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "score": round(self.score, 4),
            "text": self.text,
            "source": self.source,
            "section_id": self.section_id,
            "chapter": self.chapter,
        }


class _BM25Index:
    """Minimal Okapi BM25 over in-memory chunks. k1=1.5, b=0.75."""

    def __init__(self, chunks: list[Chunk], *, k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.doc_tokens: list[list[str]] = [_tokenise(c.text) for c in chunks]
        self.doc_len: list[int] = [len(toks) for toks in self.doc_tokens]
        self.avg_len: float = (sum(self.doc_len) / len(self.doc_len)) if self.doc_len else 0.0
        self.doc_freq: Counter[str] = Counter()
        for toks in self.doc_tokens:
            for term in set(toks):
                self.doc_freq[term] += 1
        self.n = len(chunks)
        self.term_to_docs: dict[str, list[int]] = {}
        for i, toks in enumerate(self.doc_tokens):
            for term in set(toks):
                self.term_to_docs.setdefault(term, []).append(i)

    def search(self, query: str, *, top_k: int = 5) -> list[tuple[int, float]]:
        q_tokens = _tokenise(query)
        if not q_tokens or self.n == 0:
            return []
        scores: dict[int, float] = {}
        for term in q_tokens:
            docs = self.term_to_docs.get(term)
            if not docs:
                continue
            df = self.doc_freq[term]
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for i in docs:
                tf = self.doc_tokens[i].count(term)
                dl = self.doc_len[i] or 1
                denom = tf + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1))
                scores[i] = scores.get(i, 0.0) + idf * tf * (self.k1 + 1) / (denom or 1)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return ranked[:top_k]


_CACHE_LOCK = threading.Lock()
_PACK_CACHE: dict[str, _BM25Index | None] = {}
_PACK_CHUNKS: dict[str, list[Chunk]] = {}


def _load_chunks_jsonl(path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = str(row.get("text", ""))
            if not text:
                continue
            cid = str(row.get("chunk_index", line_no))
            chunks.append(
                Chunk(
                    id=cid,
                    text=text,
                    source=str(row.get("source_file") or path.name),
                    section_id=row.get("section_id"),
                    chapter=row.get("chapter"),
                    meta={k: v for k, v in row.items() if k not in {"text"}},
                )
            )
    return chunks


def _load_dir_fallback(docs_root: Path, *, max_files: int = 500, max_chars: int = 4000) -> list[Chunk]:
    """If no pre-built chunks.jsonl, greedily index *.md / *.txt in documents_root.

    Each file becomes one chunk truncated to ``max_chars``. This is a
    last-resort path so a pack with no rag/ still gets some retrieval.
    """
    chunks: list[Chunk] = []
    if not docs_root.is_dir():
        return chunks
    for i, path in enumerate(sorted(docs_root.rglob("*"))):
        if i >= max_files:
            break
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:max_chars]
        except Exception:
            continue
        if not text.strip():
            continue
        rel = path.relative_to(docs_root).as_posix()
        chunks.append(Chunk(id=f"file:{rel}", text=text, source=rel))
    return chunks


def load_pack_chunks(pack_id: str) -> list[Chunk]:
    if pack_id in _PACK_CHUNKS:
        return _PACK_CHUNKS[pack_id]
    pack_dir = PACKS_ROOT / pack_id
    chunks_file = pack_dir / "documents" / "rag" / "chunks" / "chunks.jsonl"
    if chunks_file.is_file():
        chunks = _load_chunks_jsonl(chunks_file)
    else:
        chunks = _load_dir_fallback(pack_dir / "documents")
    _PACK_CHUNKS[pack_id] = chunks
    return chunks


def get_index(pack_id: str) -> _BM25Index | None:
    with _CACHE_LOCK:
        if pack_id in _PACK_CACHE:
            return _PACK_CACHE[pack_id]
        chunks = load_pack_chunks(pack_id)
        if not chunks:
            _PACK_CACHE[pack_id] = None
            return None
        idx = _BM25Index(chunks)
        _PACK_CACHE[pack_id] = idx
        return idx


def search(pack_id: str, query: str, *, top_k: int = 5) -> list[RetrievalHit]:
    """Search one pack. Returns empty list if pack is unknown or empty."""
    idx = get_index(pack_id)
    if idx is None:
        return []
    chunks = _PACK_CHUNKS[pack_id]
    hits: list[RetrievalHit] = []
    for i, score in idx.search(query, top_k=top_k):
        c = chunks[i]
        hits.append(
            RetrievalHit(
                chunk_id=c.id,
                score=float(score),
                text=c.text,
                source=c.source,
                section_id=c.section_id,
                chapter=c.chapter,
            )
        )
    return hits


def search_many(pack_ids: Iterable[str], query: str, *, top_k_per_pack: int = 3) -> list[RetrievalHit]:
    """Search across multiple packs and merge by score."""
    out: list[RetrievalHit] = []
    for pid in pack_ids:
        out.extend(search(pid, query, top_k=top_k_per_pack))
    out.sort(key=lambda h: h.score, reverse=True)
    return out


def format_context_block(hits: list[RetrievalHit], *, max_chars: int = 3500) -> str:
    """Render hits as a single text block to inject into a model prompt.

    Truncates at ``max_chars`` total to keep context windows sane; trims each
    hit's text proportionally if the raw sum would exceed the budget.
    """
    if not hits:
        return ""
    parts = []
    running = 0
    per_hit_budget = max(200, max_chars // max(1, len(hits)))
    for i, h in enumerate(hits, 1):
        head = f"[{i}] {h.source}"
        if h.section_id:
            head += f" §{h.section_id}"
        snippet = h.text.strip()
        if len(snippet) > per_hit_budget:
            snippet = snippet[:per_hit_budget] + "…"
        block = f"{head}\n{snippet}"
        if running + len(block) > max_chars:
            break
        parts.append(block)
        running += len(block)
    return "\n\n".join(parts)


__all__ = [
    "Chunk",
    "RetrievalHit",
    "search",
    "search_many",
    "format_context_block",
    "load_pack_chunks",
    "get_index",
    "PACKS_ROOT",
]


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Retrieval smoke test over a pack")
    parser.add_argument("pack", help="pack id (e.g. fl-trust-law)")
    parser.add_argument("query", nargs="+", help="query terms")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()
    q = " ".join(args.query)
    hits = search(args.pack, q, top_k=args.k)
    if not hits:
        print(f"no hits for pack={args.pack!r} query={q!r}", file=sys.stderr)
        sys.exit(2)
    for i, h in enumerate(hits, 1):
        print(f"{i:>2}  score={h.score:6.3f}  {h.source}  §{h.section_id or '-'}")
        print(f"    {h.text[:200].strip()}")
