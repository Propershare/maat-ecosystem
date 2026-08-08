"""
Maat Memory Integration for MaatLangChain API
Simple logging wrapper for Cross-session memory tracking
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

log = logging.getLogger(__name__)


class MaatLogger:
    """
    Simple Maat memory logger for MaatLangChain API.

    Provides basic logging functionality without complex dependencies.
    """

    def __init__(self):
        self.maat_path = Path("/home/suspect/.n8n/.maat_memory/maat_memory.json")
        self.data = self._load_or_create()
        self.session_id = self._start_api_session()

    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing maat_memory.json or create default structure."""
        if self.maat_path.exists():
            try:
                with open(self.maat_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                log.warning(f"Error loading maat_memory.json: {e}")
                return self._create_default()
        else:
            return self._create_default()

    def _create_default(self) -> Dict[str, Any]:
        """Create default maat_memory.json structure."""
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "system": "MaatLangChain API with Maat Memory",
                "purpose": "Cross-session memory for API operations",
            },
            "sessions": [],
            "conversations": [],
            "audit_trail": [],
            "tracking": {
                "tasks": [],
                "decisions": [],
                "changes": [],
                "errors": [],
                "learnings": [],
            },
        }

    def _save(self):
        """Save maat_memory.json with timestamp update."""
        try:
            self.data["updated_at"] = datetime.now().isoformat()
            with open(self.maat_path, "w") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.error(f"Error saving maat_memory.json: {e}")

    def _start_api_session(self) -> str:
        """Start a new API session."""
        import uuid

        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "agent": "maatlangchain_api",
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "summary": "API server session for RAG operations",
            "key_points": [
                "REST API",
                "RAG queries",
                "PDF processing",
                "Maat integration",
            ],
            "files_modified": [],
            "tasks_completed": [],
        }

        self.data["sessions"].append(session)
        self._save()

        log.info(f"Started API session: {session_id}")
        return session_id

    def log_query(
        self,
        question: str,
        answer: str,
        sources: list,
        query_time: float,
        top_k: int = 5,
    ) -> str:
        """Log a RAG query to Maat memory."""
        import uuid

        conversation_id = str(uuid.uuid4())

        conversation = {
            "id": conversation_id,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "agent": "maatlangchain_api",
            "user_query": question,
            "agent_response": answer,
            "tools_used": ["rag_query", "similarity_search"],
            "files_accessed": [],
            "decisions_made": [
                f"Retrieved {len(sources)} sources",
                f"Query time: {query_time:.3f}s",
                f"Top-k: {top_k}",
            ],
            "metadata": {
                "sources_count": len(sources),
                "query_time_seconds": query_time,
                "top_k": top_k,
            },
        }

        self.data["conversations"].append(conversation)
        self._save()

        log.info(f"Logged RAG query: {question[:50]}...")
        return conversation_id

    def log_pdf_ingestion(
        self,
        pdf_path: str,
        status: str,
        chunks_created: Optional[int] = None,
        processing_time: Optional[float] = None,
        error_details: Optional[str] = None,
    ) -> str:
        """Log PDF ingestion to Maat memory."""
        import uuid

        audit_id = str(uuid.uuid4())

        audit_entry = {
            "id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "agent": "maatlangchain_api",
            "action": "pdf_ingestion",
            "resource": pdf_path,
            "before": "PDF not ingested",
            "after": f"Status: {status}",
            "reason": "API PDF processing request",
            "maat_compliance": {
                "truth": "Status accurately reported",
                "balance": "Processing preserves existing data",
                "order": "Standard PDF processing pipeline",
                "self_reflection": "Monitoring processing success",
            },
            "metadata": {
                "chunks_created": chunks_created,
                "processing_time_seconds": processing_time,
                "error_details": error_details,
            },
        }

        self.data["audit_trail"].append(audit_entry)

        # Also log as task if successful
        if status == "success":
            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "agent": "maatlangchain_api",
                "title": f"Process PDF: {Path(pdf_path).name}",
                "description": f"Ingest {pdf_path} into RAG system",
                "status": "completed",
                "priority": "medium",
                "related_files": [pdf_path],
                "dependencies": ["langchain", "pgvector"],
                "completion_notes": f"Created {chunks_created} chunks in {processing_time:.1f}s",
            }

            self.data["tracking"]["tasks"].append(task)

        self._save()

        log.info(f"Logged PDF ingestion: {pdf_path} - {status}")
        return audit_id

    def log_api_usage(
        self,
        endpoint: str,
        method: str,
        user_agent: Optional[str] = None,
        response_time: Optional[float] = None,
    ) -> str:
        """Log API usage for audit trail."""
        import uuid

        audit_id = str(uuid.uuid4())

        audit_entry = {
            "id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "agent": "maatlangchain_api",
            "action": f"{method}_{endpoint}",
            "resource": f"API endpoint: {method} {endpoint}",
            "before": None,
            "after": f"Request processed",
            "reason": "API usage monitoring",
            "maat_compliance": {
                "truth": "Accurate request tracking",
                "balance": "Fair resource usage",
                "order": "Proper API protocol",
                "self_reflection": "Performance monitoring",
            },
            "metadata": {
                "endpoint": endpoint,
                "method": method,
                "user_agent": user_agent,
                "response_time_seconds": response_time,
            },
        }

        self.data["audit_trail"].append(audit_entry)
        self._save()

        log.info(f"Logged API usage: {method} {endpoint}")
        return audit_id


# Global instance
_maat_logger: Optional[MaatLogger] = None


def get_maat_logger() -> MaatLogger:
    """Get or create Maat logger instance."""
    global _maat_logger

    if _maat_logger is None:
        _maat_logger = MaatLogger()
        log.info("Maat logger initialized for API")

    return _maat_logger
