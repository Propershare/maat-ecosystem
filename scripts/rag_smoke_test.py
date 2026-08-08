#!/usr/bin/env python3
"""
End-to-end RAG smoke test: PGVector + embeddings + MaatRAG write + read.

Loads PGVECTOR_DB_URL from env or ~/.n8n/.env (secrets not printed).
Exit 0 on success, 1 on failure.

Usage:
  cd /home/suspect/.n8n && python3 scripts/rag_smoke_test.py
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
MAAT = WORKSPACE / "maatlangchain"
sys.path.insert(0, str(MAAT))


def _load_pgvector_url() -> str | None:
    url = os.environ.get("PGVECTOR_DB_URL")
    if url:
        return url.strip().strip('"').strip("'")
    for env_path in (WORKSPACE / ".env", MAAT / ".env", WORKSPACE / "maatlangchain" / ".env"):
        if not env_path.exists():
            continue
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("PGVECTOR_DB_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def main() -> int:
    pg = _load_pgvector_url()
    if not pg:
        print("FAIL: PGVECTOR_DB_URL not set and not found in .env")
        return 1

    os.environ["PGVECTOR_DB_URL"] = pg

    import psycopg2

    try:
        conn = psycopg2.connect(pg)
        cur = conn.cursor()
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        if not cur.fetchone():
            print("FAIL: pgvector extension missing in database")
            conn.close()
            return 1
        conn.close()
    except Exception as e:
        print(f"FAIL: database connection: {e}")
        return 1

    try:
        from langchain_community.vectorstores import PGVector
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError as e:
        print(f"FAIL: missing dependency: {e}")
        return 1

    from langchain_core.documents import Document

    from core.chains.maat_rag import MaatRAG

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    vector_store = PGVector(
        connection_string=pg,
        embedding_function=embeddings,
        collection_name="maat_knowledge",
        use_jsonb=True,
    )
    rag = MaatRAG(vector_store=vector_store, embeddings=embeddings)

    token = f"E2E_SMOKE_{uuid.uuid4().hex[:12]}"
    text = (
        f"This is a Tehuti Lab RAG smoke test document. Unique token: {token}. "
        "If retrieval works, a similarity search for this token should return this chunk."
    )
    doc = Document(
        page_content=text,
        metadata={
            "file_name": "rag_smoke_test.txt",
            "source": "scripts/rag_smoke_test.py",
            "smoke_test": "true",
            "token": token,
        },
    )

    if not rag.store_document([doc], "maat_knowledge"):
        print("FAIL: store_document returned False")
        return 1

    results = rag.search_similar(token, "maat_knowledge", top_k=5)
    if not results:
        print("FAIL: similarity search returned no documents after insert")
        return 1

    joined = " ".join(r.page_content for r in results)
    if token not in joined:
        print("FAIL: inserted token not in top-k results")
        prev = [r.page_content[:80] for r in results]
        print(f"  top_k={len(results)}, preview={prev}")
        return 1

    print("PASS: end-to-end RAG smoke test")
    print("  - pgvector: OK")
    print("  - embed model: sentence-transformers/all-MiniLM-L6-v2 (CPU)")
    print("  - collection: maat_knowledge")
    print(f"  - wrote 1 chunk, retrieved token in top-{len(results)}")
    print(f"  - token (safe to grep logs): {token}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
