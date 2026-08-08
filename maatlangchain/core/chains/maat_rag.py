"""
MaatRAG — LangChain PGVector wrapper with light metrics.

Used by api/main_original.py and tests/unit/test_maat_rag.py.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Union

from langchain_core.documents import Document

log = logging.getLogger(__name__)


class MaatRAG:
    """Retrieval helper over a LangChain vector store + embeddings."""

    def __init__(self, vector_store: Any, embeddings: Any = None) -> None:
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.performance_stats: Dict[str, Any] = {
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "total_processing_time": 0.0,
        }

    def search_similar(
        self,
        query: str,
        collection_name: str = "maat_knowledge",
        top_k: int = 5,
    ) -> List[Document]:
        """Similarity search; collection_name passed to filter when supported."""
        t0 = time.time()
        _ = collection_name  # PGVector collection is usually fixed on the store
        try:
            docs = self.vector_store.similarity_search(query, k=top_k)
        except TypeError:
            docs = self.vector_store.similarity_search(query, top_k)

        self.performance_stats["total_processing_time"] += time.time() - t0
        return docs

    def store_document(
        self,
        chunks: List[Document],
        collection_name: str,
    ) -> bool:
        """Persist document chunks; empty input returns False."""
        if not chunks:
            return False
        t0 = time.time()
        try:
            if hasattr(self.vector_store, "add_documents"):
                self.vector_store.add_documents(chunks)
            elif hasattr(self.vector_store, "add_texts"):
                texts = [c.page_content for c in chunks]
                metas = [c.metadata for c in chunks]
                self.vector_store.add_texts(texts, metadatas=metas)
            else:
                log.error("vector_store has no add_documents/add_texts")
                return False
        except Exception as e:
            log.error("store_document failed: %s", e)
            return False

        self.performance_stats["documents_processed"] += 1
        self.performance_stats["chunks_created"] += len(chunks)
        self.performance_stats["total_processing_time"] += time.time() - t0
        return True

    def query(
        self,
        question: str,
        collection_name: str = "maat_knowledge",
        top_k: int = 5,
        llm_model: Optional[str] = None,
        max_context_length: int = 4000,
    ) -> Dict[str, Any]:
        """
        Retrieve + synthesize a simple answer (no external LLM unless extended).

        *llm_model* is reserved for future Ollama/OpenAI wiring; today we stitch
        from top chunks like the lightweight /rag/query path in main_original.
        """
        _ = llm_model
        docs = self.search_similar(question, collection_name, top_k)
        if not docs:
            return {
                "answer": "No relevant documents found.",
                "sources": [],
                "metadata": {"confidence": "low"},
            }

        ctx = "\n\n".join(d.page_content for d in docs[:top_k])
        if len(ctx) > max_context_length:
            ctx = ctx[:max_context_length] + "..."

        lead = docs[0].page_content
        answer = lead[:500] + ("..." if len(lead) > 500 else "")

        sources: List[Dict[str, Any]] = []
        for d in docs[:top_k]:
            sources.append(
                {
                    "file_name": d.metadata.get("file_name", "unknown"),
                    "page": d.metadata.get("page", 0),
                    "preview": d.page_content[:200],
                    "confidence": 0.0,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "confidence": "medium",
                "collection_name": collection_name,
                "context_chars": len(ctx),
            },
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        return dict(self.performance_stats)

    def reset_stats(self) -> None:
        for k in self.performance_stats:
            if k == "total_processing_time":
                self.performance_stats[k] = 0.0
            else:
                self.performance_stats[k] = 0
