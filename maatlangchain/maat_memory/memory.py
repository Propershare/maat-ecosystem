"""
Maat Memory System - Cross-Session Memory for Cursor and OpenCode

Provides shared memory, audit tracking, and vector store integration
following Maat principles.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

log = logging.getLogger(__name__)

from .paths import get_maat_memory_backup_dir, get_maat_memory_json_path

MAAT_MEMORY_JSON_PATH = get_maat_memory_json_path()
MAAT_MEMORY_BACKUP_DIR = get_maat_memory_backup_dir()


class MaatMemory:
    """
    Cross-session memory system for Cursor and OpenCode agents.
    
    Provides:
    - Session tracking
    - Conversation logging
    - Audit trail
    - Task management
    - Decision tracking
    - Change history
    - Error logging
    - Learning capture
    - Vector store integration
    """
    
    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = memory_path or MAAT_MEMORY_JSON_PATH
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        MAAT_MEMORY_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self._data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load maat_memory.json, creating if it doesn't exist."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Error loading maat_memory.json: {e}")
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
                "system": "MaatLangChain Cross-Session Memory",
                "purpose": "Shared memory for Cursor and OpenCode agents",
                "governance": "Maat principles"
            },
            "sessions": [],
            "conversations": [],
            "audit_trail": [],
            "knowledge_base": {
                "vector_store": {
                    "type": "postgresql_pgvector",
                    "connection": "PGVECTOR_DB_URL",
                    "collection": "maat_knowledge"
                }
            },
            "agent_memory": {
                "cursor": {
                    "session_id": None,
                    "last_updated": None,
                    "context": [],
                    "preferences": {},
                    "work_history": []
                },
                "opencode": {
                    "session_id": None,
                    "last_updated": None,
                    "context": [],
                    "preferences": {},
                    "work_history": []
                }
            },
            "tracking": {
                "tasks": [],
                "decisions": [],
                "changes": [],
                "errors": [],
                "learnings": []
            }
        }
    
    def _save(self):
        """Save maat_memory.json with backup."""
        # Create backup
        if self.memory_path.exists():
            backup_path = MAAT_MEMORY_BACKUP_DIR / f"maat_memory-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            try:
                import shutil
                shutil.copy2(self.memory_path, backup_path)
            except Exception as e:
                log.warning(f"Failed to create backup: {e}")
        
        # Update timestamp
        self._data["updated_at"] = datetime.now().isoformat()
        
        # Save
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.error(f"Error saving maat_memory.json: {e}")
            raise
    
    def start_session(self, agent: str, summary: Optional[str] = None) -> str:
        """Start a new session for an agent."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            self._data["agent_memory"][agent] = {
                "session_id": None,
                "last_updated": None,
                "context": [],
                "preferences": {},
                "work_history": []
            }
        
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "agent": agent,
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "summary": summary or "",
            "key_points": [],
            "files_modified": [],
            "tasks_completed": []
        }
        
        self._data["sessions"].append(session)
        self._data["agent_memory"][agent]["session_id"] = session_id
        self._data["agent_memory"][agent]["last_updated"] = datetime.now().isoformat()
        self._save()
        
        log.info(f"Started {agent} session: {session_id}")
        return session_id
    
    def end_session(self, agent: str, summary: str, key_points: Optional[List[str]] = None):
        """End current session for an agent."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            self._data["agent_memory"][agent] = {
                "session_id": None,
                "last_updated": None,
                "context": [],
                "preferences": {},
                "work_history": []
            }
        
        agent_mem = self._data["agent_memory"][agent]
        session_id = agent_mem.get("session_id")
        
        if session_id:
            for session in self._data["sessions"]:
                if session["id"] == session_id:
                    session["ended_at"] = datetime.now().isoformat()
                    session["summary"] = summary
                    if key_points:
                        session["key_points"] = key_points
                    break
        
        agent_mem["session_id"] = None
        agent_mem["last_updated"] = datetime.now().isoformat()
        self._save()
        
        log.info(f"Ended {agent} session: {session_id}")
    
    def log_conversation(
        self,
        agent: str,
        user_query: str,
        agent_response: str,
        tools_used: Optional[List[str]] = None,
        files_accessed: Optional[List[str]] = None,
        decisions_made: Optional[List[str]] = None
    ) -> str:
        """Log a conversation entry."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            self._data["agent_memory"][agent] = {
                "session_id": None,
                "last_updated": None,
                "context": [],
                "preferences": {},
                "work_history": []
            }
        
        agent_mem = self._data["agent_memory"][agent]
        session_id = agent_mem.get("session_id")
        
        conversation_id = str(uuid.uuid4())
        conversation = {
            "id": conversation_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "user_query": user_query,
            "agent_response": agent_response,
            "tools_used": tools_used or [],
            "files_accessed": files_accessed or [],
            "decisions_made": decisions_made or []
        }
        
        self._data["conversations"].append(conversation)
        self._save()
        
        return conversation_id
    
    def log_audit(
        self,
        agent: str,
        action: str,
        resource: str,
        before: Optional[Any] = None,
        after: Optional[Any] = None,
        reason: str = "",
        maat_compliance: Optional[Dict[str, bool]] = None
    ) -> str:
        """Log an audit trail entry."""
        audit_id = str(uuid.uuid4())
        audit_entry = {
            "id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "resource": resource,
            "before": before,
            "after": after,
            "reason": reason,
            "maat_compliance": maat_compliance or {
                "truth": True,
                "balance": True,
                "order": True,
                "self_reflection": True
            }
        }
        
        self._data["audit_trail"].append(audit_entry)
        self._save()
        
        return audit_id
    
    def log_task(
        self,
        agent: str,
        title: str,
        description: str,
        status: str = "pending",
        priority: str = "medium",
        related_files: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        """Log a task. origin= is required (T1 provenance — absence is not compliance)."""
        from .maat_provenance import parse_origin, require_scoped_write

        require_scoped_write(task_id=None, agent=agent)
        origin_v = parse_origin(origin).value

        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "agent": agent,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "related_files": related_files or [],
            "dependencies": dependencies or [],
            "completion_notes": None,
            "content_origin": origin_v,
        }
        
        self._data["tracking"]["tasks"].append(task)
        self._save()
        
        return task_id
    
    def log_decision(
        self,
        agent: str,
        context: str,
        decision_made: str,
        rationale: str,
        options_considered: Optional[List[str]] = None,
        maat_alignment: Optional[Dict[str, str]] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        """Log a decision. origin= is required (T1 provenance — absence is not compliance)."""
        from .maat_provenance import parse_origin, require_scoped_write

        require_scoped_write(task_id=None, agent=agent)
        origin_v = parse_origin(origin).value

        decision_id = str(uuid.uuid4())
        decision = {
            "id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "context": context,
            "options_considered": options_considered or [],
            "decision_made": decision_made,
            "rationale": rationale,
            "outcome": None,
            "content_origin": origin_v,
            "maat_alignment": maat_alignment or {
                "truth": "Decision based on verified information",
                "balance": "Change preserves working systems",
                "order": "Follows established patterns",
                "self_reflection": "Will monitor outcome"
            }
        }
        
        self._data["tracking"]["decisions"].append(decision)
        self._save()
        
        return decision_id
    
    def log_change(
        self,
        agent: str,
        file_path: str,
        change_type: str,
        summary: str,
        reason: str,
        diff_preview: Optional[str] = None
    ) -> str:
        """Log a file change."""
        change_id = str(uuid.uuid4())
        change = {
            "id": change_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "file_path": file_path,
            "change_type": change_type,
            "summary": summary,
            "diff_preview": diff_preview,
            "reason": reason,
            "reverted": False,
            "revert_reason": None
        }
        
        self._data["tracking"]["changes"].append(change)
        
        # Update session files_modified
        agent_mem = self._data["agent_memory"][agent]
        session_id = agent_mem.get("session_id")
        if session_id:
            for session in self._data["sessions"]:
                if session["id"] == session_id:
                    if file_path not in session["files_modified"]:
                        session["files_modified"].append(file_path)
                    break
        
        self._save()
        
        return change_id
    
    def log_error(
        self,
        agent: str,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        resolution: Optional[str] = None,
        prevention: Optional[str] = None
    ) -> str:
        """Log an error."""
        error_id = str(uuid.uuid4())
        error = {
            "id": error_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "error_type": error_type,
            "message": message,
            "stack_trace": stack_trace,
            "context": context or {},
            "resolution": resolution,
            "prevention": prevention
        }
        
        self._data["tracking"]["errors"].append(error)
        self._save()
        
        return error_id
    
    def log_learning(
        self,
        agent: str,
        topic: str,
        insight: str,
        source: str,
        confidence: float = 0.5,
        applied: bool = False,
        application_context: Optional[str] = None
    ) -> str:
        """Log a learning/insight."""
        learning_id = str(uuid.uuid4())
        learning = {
            "id": learning_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "topic": topic,
            "insight": insight,
            "source": source,
            "confidence": confidence,
            "applied": applied,
            "application_context": application_context
        }
        
        self._data["tracking"]["learnings"].append(learning)
        self._save()
        
        return learning_id
    
    def get_context(self, agent: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent context for an agent."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            return []
        
        agent_mem = self._data["agent_memory"][agent]
        return agent_mem.get("context", [])[-limit:]
    
    def add_context(self, agent: str, context_entry: Dict[str, Any]):
        """Add context entry for an agent."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            self._data["agent_memory"][agent] = {
                "session_id": None,
                "last_updated": None,
                "context": [],
                "preferences": {},
                "work_history": []
            }
        
        agent_mem = self._data["agent_memory"][agent]
        if "context" not in agent_mem:
            agent_mem["context"] = []
        agent_mem["context"].append({
            **context_entry,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 100 entries
        agent_mem["context"] = agent_mem["context"][-100:]
        agent_mem["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search conversations (simple text search, can be enhanced with vector search)."""
        results = []
        query_lower = query.lower()
        
        for conv in self._data["conversations"]:
            if (query_lower in conv.get("user_query", "").lower() or
                query_lower in conv.get("agent_response", "").lower()):
                results.append(conv)
        
        return results[:limit]
    
    def get_recent_work(self, agent: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent work history for an agent."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            return []
        
        agent_mem = self._data["agent_memory"][agent]
        return agent_mem.get("work_history", [])[-limit:]
    
    def add_work_history(self, agent: str, work_entry: Dict[str, Any]):
        """Add work history entry."""
        # Ensure agent memory exists
        if agent not in self._data["agent_memory"]:
            self._data["agent_memory"][agent] = {
                "session_id": None,
                "last_updated": None,
                "context": [],
                "preferences": {},
                "work_history": []
            }
        
        agent_mem = self._data["agent_memory"][agent]
        if "work_history" not in agent_mem:
            agent_mem["work_history"] = []
        agent_mem["work_history"].append({
            **work_entry,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 200 entries
        agent_mem["work_history"] = agent_mem["work_history"][-200:]
        agent_mem["last_updated"] = datetime.now().isoformat()
        self._save()

