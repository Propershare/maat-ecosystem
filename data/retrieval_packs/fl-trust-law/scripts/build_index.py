#!/usr/bin/env python3
"""
Rebuild the FAISS index for the fl-trust-law retrieval pack.

Uses Ollama nomic-embed-text (768-dim) for embeddings.
Expects clean markdown files under documents/law_data_clean/.

Usage:
    python3 build_index.py
"""

from __future__ import annotations

import json
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import faiss

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PACKS_ROOT = Path(__file__).resolve().parents[2]
PACK_ID = "fl-trust-law"
CLEAN_DIR = PACKS_ROOT / PACK_ID / "documents/law_data_clean"
RAW_DIR = PACKS_ROOT / PACK_ID / "documents/law_data_raw"
CHUNKS_OUT = PACKS_ROOT / PACK_ID / "documents/rag/chunks"
INDEX_OUT = PACKS_ROOT / PACK_ID / "documents/rag/indexes/primary"

# Embedding
OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768

# Chunking
CHUNK_SIZE = 512   # chars
CHUNK_OVERLAP = 64


def ollama_embed(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts via Ollama."""
    import requests
    resp = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["embeddings"]


def chunk_text(text: str, source: str) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    chunk_idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text_str = text[start:end]
        # Preserve some content structure: try to break at newline
        if end < len(text):
            break_point = chunk_text_str.rfind('\n', CHUNK_SIZE // 4)
            if break_point > CHUNK_SIZE // 4:
                end = start + break_point
                chunk_text_str = text[start:end]

        chunks.append({
            "chunk_index": chunk_idx,
            "section_id": _extract_section(source, start),
            "chapter": _extract_chapter(source),
            "source_file": source,
            "text": chunk_text_str.strip(),
        })
        chunk_idx += 1
        start = end - CHUNK_OVERLAP
    return chunks


def _extract_section(source: str, offset: int) -> str:
    """Best-effort section ID from source path."""
    return Path(source).stem or f"offset_{offset}"


def _extract_chapter(source: str) -> str:
    """Extract chapter number from source path."""
    name = Path(source).stem
    for part in name.split('.'):
        if part.isdigit():
            return part
    return ""


def collect_clean_files() -> List[Path]:
    """Collect all clean markdown files."""
    files = []
    if CLEAN_DIR.exists():
        files.extend(sorted(CLEAN_DIR.rglob("*.md")))
    if not files and RAW_DIR.exists():
        files.extend(sorted(RAW_DIR.rglob("*.txt")))
    return files


def main():
    import requests

    # Check Ollama connectivity
    try:
        tags = requests.get("http://127.0.0.1:11434/api/tags", timeout=5).json()
        model_names = [m["name"] for m in tags.get("models", [])]
        found = any(EMBED_MODEL == mn or mn.startswith(EMBED_MODEL + ":") for mn in model_names)
        if not found:
            print(f"⚠️  Model '{EMBED_MODEL}' not found in Ollama. Available: {model_names[:10]}...")
            print("Run: ollama pull nomic-embed-text")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Cannot reach Ollama at 127.0.0.1:11434: {e}")
        print("Ensure Ollama is running with nomic-embed-text loaded.")
        sys.exit(1)

    # Collect files
    clean_files = collect_clean_files()
    if not clean_files:
        print(f"❌ No clean files found under {CLEAN_DIR} or {RAW_DIR}")
        sys.exit(1)

    print(f"📄 Found {len(clean_files)} source files")

    # Chunk all files
    all_chunks = []
    total_chars = 0
    for fpath in clean_files:
        rel = str(fpath.relative_to(PACKS_ROOT / PACK_ID))
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        chunks = chunk_text(content, rel)
        all_chunks.extend(chunks)
        total_chars += len(content)

    print(f"📝 Created {len(all_chunks)} chunks from {total_chars:,} chars")

    # Embed chunks in batches (Ollama has input limits)
    print(f"🧠 Embedding {len(all_chunks)} chunks with '{EMBED_MODEL}'...")
    batch_size = 20
    all_embeddings = []

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = ollama_embed(texts)
        all_embeddings.extend(embeddings)
        print(f"  Progress: {min(i + batch_size, len(all_chunks))}/{len(all_chunks)}", file=sys.stderr)

    if not all_embeddings:
        print("❌ No embeddings generated")
        sys.exit(1)

    # Convert to numpy
    embeddings_array = np.array(all_embeddings, dtype=np.float32)
    # Normalize for inner product = cosine
    faiss.normalize_L2(embeddings_array)

    print(f"📊 Embedding shape: {embeddings_array.shape}")

    # Build FAISS index
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(embeddings_array)
    print(f"📚 FAISS index built: {index.ntotal} vectors, {index.d} dims")

    # Save chunks and index
    CHUNKS_OUT.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.mkdir(parents=True, exist_ok=True)

    chunks_path = CHUNKS_OUT / "chunks.jsonl"
    with open(chunks_path, "w") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
    print(f"💾 Saved chunks to {chunks_path}")

    index_path = INDEX_OUT / "index.faiss"
    faiss.write_index(index, str(index_path))
    print(f"💾 Saved index to {index_path}")

    # Update manifest if exists
    manifest_path = PACKS_ROOT / PACK_ID / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        manifest["version"] = manifest.get("version", "0.0.0")
        manifest["index_built"] = True
        manifest["embedding_model"] = EMBED_MODEL
        manifest["num_chunks"] = len(all_chunks)
        manifest["embedding_dim"] = EMBED_DIM
        manifest["last_built"] = __import__("datetime").datetime.now().isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"📋 Updated manifest at {manifest_path}")

    print("\n✅ Index rebuild complete!")


if __name__ == "__main__":
    main()
