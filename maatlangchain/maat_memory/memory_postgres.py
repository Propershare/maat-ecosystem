"""
Maat Memory System - PostgreSQL Backend
Cross-Session Memory for Cursor and OpenCode

Provides shared memory, audit tracking, and vector store integration
following Maat principles. Uses PostgreSQL with pgvector for storage.
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)


class MaatMemoryPostgres:
    """
    PostgreSQL-backed cross-session memory system for Cursor and OpenCode agents.
    
    Provides:
    - Session tracking
    - Conversation logging with vector search
    - Audit trail
    - Task management
    - Decision tracking
    - Change history
    - Error logging
    - Learning capture
    - Vector search for semantic queries
    """
    
    def __init__(self, db_url: Optional[str] = None, embeddings_model=None):
        """
        Initialize Maat Memory with PostgreSQL backend.
        
        Args:
            db_url: PostgreSQL connection string (defaults to PGVECTOR_DB_URL)
            embeddings_model: Embeddings model for vector search (optional)
        """
        self.db_url = db_url or self._get_pgvector_url()
        if not self.db_url:
            raise ValueError("PostgreSQL connection string required (PGVECTOR_DB_URL)")
        
        self.embeddings_model = embeddings_model
        self._conn = None
        self._ensure_schema()
    
    def _get_pgvector_url(self) -> Optional[str]:
        """Get PostgreSQL URL via portable paths (env + workspace .env candidates)."""
        from .paths import get_pgvector_db_url

        return get_pgvector_db_url()
    
    def _get_connection(self):
        """Get or create database connection."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.db_url)
        return self._conn
    
    def _ensure_schema(self):
        """Ensure PostgreSQL schema exists."""
        schema_path = Path(__file__).parent / "schema.sql"
        metadata_schema_path = Path(__file__).parent / "schema_add_metadata.sql"
        
        if not schema_path.exists():
            log.warning(f"Schema file not found: {schema_path}")
            return
        
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            # Check if schema exists by checking for a table
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'maat_sessions'
                )
            """)
            if not cur.fetchone()[0]:
                log.info("Creating Maat Memory schema...")
                schema_sql = schema_path.read_text()
                cur.execute(schema_sql)
                conn.commit()
                log.info("✅ Schema created")
            else:
                log.debug("Schema already exists")
            
            # Apply metadata migration if needed
            if metadata_schema_path.exists():
                try:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'maat_sessions' 
                            AND column_name = 'metadata'
                        )
                    """)
                    if not cur.fetchone()[0]:
                        log.info("Adding metadata columns...")
                        metadata_sql = metadata_schema_path.read_text()
                        cur.execute(metadata_sql)
                        conn.commit()
                        log.info("✅ Metadata columns added")
                except Exception as e:
                    log.warning(f"Metadata migration may have already been applied: {e}")
            
            cur.close()
        except Exception as e:
            log.error(f"Failed to ensure schema: {e}")
            raise
    
    def start_session(
        self, 
        agent: str, 
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new session for an agent with machine/terminal info."""
        from .machine_info import get_machine_info
        
        # Auto-detect machine info
        machine_info = get_machine_info()
        
        # Merge with provided metadata
        session_metadata = {
            **machine_info,
            **(metadata or {})
        }
        
        session_id = str(uuid.uuid4())
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_sessions (
                    id, agent, summary, metadata
                ) VALUES (%s, %s, %s, %s)
            """, (session_id, agent, summary or "", json.dumps(session_metadata)))
            
            # Update agent memory
            cur.execute("""
                INSERT INTO maat_agent_memory (agent, session_id, last_updated)
                VALUES (%s, %s, NOW())
                ON CONFLICT (agent) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    last_updated = NOW(),
                    updated_at = NOW()
            """, (agent, session_id))
            
            conn.commit()
            log.info(f"Started {agent} session: {session_id}")
            return session_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to start session: {e}")
            raise
        finally:
            cur.close()
    
    def end_session(self, agent: str, summary: str, key_points: Optional[List[str]] = None):
        """End current session for an agent."""
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Get current session_id
            cur.execute("""
                SELECT session_id FROM maat_agent_memory WHERE agent = %s
            """, (agent,))
            result = cur.fetchone()
            session_id = result[0] if result else None
            
            if session_id:
                cur.execute("""
                    UPDATE maat_sessions
                    SET ended_at = NOW(), summary = %s, key_points = %s
                    WHERE id = %s
                """, (summary, json.dumps(key_points or []), session_id))
                
                # Clear session_id from agent memory
                cur.execute("""
                    UPDATE maat_agent_memory
                    SET session_id = NULL, last_updated = NOW(), updated_at = NOW()
                    WHERE agent = %s
                """, (agent,))
            
            conn.commit()
            log.info(f"Ended {agent} session: {session_id}")
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to end session: {e}")
            raise
        finally:
            cur.close()
    
    def get_sessions(
        self, 
        agent: Optional[str] = None,
        hostname: Optional[str] = None,
        machine_id: Optional[str] = None,
        terminal_id: Optional[str] = None,
        limit: int = 10,
        include_ended: bool = True
    ) -> List[Dict[str, Any]]:
        """Get sessions with machine/terminal filtering."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            conditions = []
            params = []
            
            if agent:
                conditions.append("agent = %s")
                params.append(agent)
            
            if hostname:
                conditions.append("metadata->>'hostname' = %s")
                params.append(hostname)
            
            if machine_id:
                conditions.append("metadata->>'machine_id' = %s")
                params.append(machine_id)
            
            if terminal_id:
                conditions.append("metadata->>'terminal_id' = %s")
                params.append(terminal_id)
            
            if not include_ended:
                conditions.append("ended_at IS NULL")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cur.execute(f"""
                SELECT 
                    id, agent, started_at, ended_at, summary, 
                    key_points, files_modified, tasks_completed,
                    metadata, created_at, updated_at
                FROM maat_sessions
                WHERE {where_clause}
                ORDER BY started_at DESC
                LIMIT %s
            """, params + [limit])
            
            results = cur.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            log.error(f"Failed to get sessions: {e}")
            return []
        finally:
            cur.close()
    
    def log_conversation(
        self,
        agent: str,
        user_query: str,
        agent_response: str,
        tools_used: Optional[List[str]] = None,
        files_accessed: Optional[List[str]] = None,
        decisions_made: Optional[List[str]] = None,
        generate_embedding: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a conversation entry with optional embedding and machine info."""
        from .machine_info import get_machine_info
        
        # Auto-detect machine info
        machine_info = get_machine_info()
        
        # Merge with provided metadata
        conversation_metadata = {
            **machine_info,
            **(metadata or {})
        }
        
        conversation_id = str(uuid.uuid4())
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Get current session_id
            cur.execute("""
                SELECT session_id FROM maat_agent_memory WHERE agent = %s
            """, (agent,))
            result = cur.fetchone()
            session_id = result[0] if result else None
            
            # Generate embedding if model available
            embedding = None
            if generate_embedding and self.embeddings_model:
                try:
                    combined_text = f"{user_query} {agent_response}"
                    embedding = self.embeddings_model.embed_query(combined_text)
                except Exception as e:
                    log.warning(f"Failed to generate embedding: {e}")
            
            # Format embedding for PostgreSQL vector type: '[1,2,3]' format
            embedding_str = None
            if embedding:
                embedding_str = "[" + ",".join(str(float(x)) for x in embedding) + "]"
            
            cur.execute("""
                INSERT INTO maat_conversations (
                    id, session_id, agent, user_query, agent_response,
                    embedding, tools_used, files_accessed, decisions_made, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s)
            """, (
                conversation_id,
                session_id,
                agent,
                user_query,
                agent_response,
                embedding_str,
                json.dumps(tools_used or []),
                json.dumps(files_accessed or []),
                json.dumps(decisions_made or []),
                json.dumps(conversation_metadata)
            ))
            
            conn.commit()
            return conversation_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log conversation: {e}")
            raise
        finally:
            cur.close()
    
    def search_conversations(
        self, 
        query: str, 
        agent: Optional[str] = None,
        hostname: Optional[str] = None,
        machine_id: Optional[str] = None,
        terminal_id: Optional[str] = None,
        limit: int = 5,
        use_vector_search: bool = True
    ) -> List[Dict[str, Any]]:
        """Search conversations using vector similarity or text search with machine/terminal filtering."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if agent:
                filter_conditions.append("agent = %s")
                filter_params.append(agent)
            
            if hostname:
                filter_conditions.append("metadata->>'hostname' = %s")
                filter_params.append(hostname)
            
            if machine_id:
                filter_conditions.append("metadata->>'machine_id' = %s")
                filter_params.append(machine_id)
            
            if terminal_id:
                filter_conditions.append("metadata->>'terminal_id' = %s")
                filter_params.append(terminal_id)
            
            filter_clause = " AND " + " AND ".join(filter_conditions) if filter_conditions else ""
            
            if use_vector_search and self.embeddings_model:
                # Vector similarity search with filters
                query_embedding = self.embeddings_model.embed_query(query)
                query_embedding_str = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
                
                # Use function if no filters, otherwise direct query
                if not filter_conditions:
                    cur.execute("""
                        SELECT * FROM maat_search_conversations(
                            %s::vector, %s, %s
                        )
                    """, (query_embedding_str, agent, limit))
                else:
                    cur.execute(f"""
                        SELECT 
                            id, session_id, timestamp, agent, user_query, agent_response,
                            metadata, 1 - (embedding <=> %s::vector) AS similarity
                        FROM maat_conversations
                        WHERE embedding IS NOT NULL {filter_clause}
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, filter_params + [query_embedding_str, query_embedding_str, limit])
            else:
                # Text search fallback with filters
                search_conditions = ["(user_query ILIKE %s OR agent_response ILIKE %s)"]
                search_params = [f"%{query}%", f"%{query}%"]
                
                if filter_conditions:
                    search_conditions = filter_conditions + search_conditions
                    search_params = filter_params + search_params
                
                where_clause = " AND ".join(search_conditions)
                
                cur.execute(f"""
                    SELECT id, session_id, timestamp, agent, user_query, agent_response,
                           metadata, NULL::float as similarity
                    FROM maat_conversations
                    WHERE {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, search_params + [limit])
            
            results = cur.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            log.error(f"Failed to search conversations: {e}")
            return []
        finally:
            cur.close()
    
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
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_audit_trail (
                    id, agent, action, resource, before_data, after_data,
                    reason, maat_compliance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                audit_id,
                agent,
                action,
                resource,
                json.dumps(before) if before else None,
                json.dumps(after) if after else None,
                reason,
                json.dumps(maat_compliance or {
                    "truth": True,
                    "balance": True,
                    "order": True,
                    "self_reflection": True
                })
            ))
            conn.commit()
            return audit_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log audit: {e}")
            raise
        finally:
            cur.close()
    
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
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_tasks (
                    id, agent, title, description, status, priority,
                    related_files, dependencies, content_origin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id,
                agent,
                title,
                description,
                status,
                priority,
                json.dumps(related_files or []),
                json.dumps(dependencies or []),
                origin_v,
            ))
            conn.commit()
            return task_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log task: {e}")
            raise
        finally:
            cur.close()
    
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
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_decisions (
                    id, agent, context, options_considered, decision_made,
                    rationale, maat_alignment, content_origin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                decision_id,
                agent,
                context,
                json.dumps(options_considered or []),
                decision_made,
                rationale,
                json.dumps(maat_alignment or {
                    "truth": "Decision based on verified information",
                    "balance": "Change preserves working systems",
                    "order": "Follows established patterns",
                    "self_reflection": "Will monitor outcome"
                }),
                origin_v,
            ))
            conn.commit()
            return decision_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log decision: {e}")
            raise
        finally:
            cur.close()
    
    def log_change(
        self,
        agent: str,
        file_path: str,
        change_type: str,
        summary: str,
        reason: str,
        diff_preview: Optional[str] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        """Log a file change. origin= is required (T1 provenance — absence is not compliance)."""
        from .maat_provenance import parse_origin, require_scoped_write

        require_scoped_write(task_id=None, agent=agent)
        origin_v = parse_origin(origin).value

        change_id = str(uuid.uuid4())
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_changes (
                    id, agent, file_path, change_type, summary,
                    diff_preview, reason, content_origin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                change_id,
                agent,
                file_path,
                change_type,
                summary,
                diff_preview,
                reason,
                origin_v,
            ))
            
            # Update session files_modified
            cur.execute("""
                SELECT session_id FROM maat_agent_memory WHERE agent = %s
            """, (agent,))
            result = cur.fetchone()
            session_id = result[0] if result else None
            
            if session_id:
                cur.execute("""
                    UPDATE maat_sessions
                    SET files_modified = files_modified || %s::jsonb
                    WHERE id = %s
                """, (json.dumps([file_path]), session_id))
            
            conn.commit()
            return change_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log change: {e}")
            raise
        finally:
            cur.close()
    
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
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_errors (
                    id, agent, error_type, message, stack_trace,
                    context_data, resolution, prevention
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                error_id,
                agent,
                error_type,
                message,
                stack_trace,
                json.dumps(context or {}),
                resolution,
                prevention
            ))
            conn.commit()
            return error_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log error: {e}")
            raise
        finally:
            cur.close()
    
    def log_learning(
        self,
        agent: str,
        topic: str,
        insight: str,
        source: str,
        confidence: float = 0.5,
        applied: bool = False,
        application_context: Optional[str] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        """Log a learning/insight. origin= is required (T1 provenance — absence is not compliance)."""
        from .maat_provenance import parse_origin, require_scoped_write

        require_scoped_write(task_id=None, agent=agent)
        origin_v = parse_origin(origin).value

        learning_id = str(uuid.uuid4())
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO maat_learnings (
                    id, agent, topic, insight, source, confidence,
                    applied, application_context, content_origin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                learning_id,
                agent,
                topic,
                insight,
                source,
                confidence,
                applied,
                application_context,
                origin_v,
            ))
            conn.commit()
            return learning_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log learning: {e}")
            raise
        finally:
            cur.close()
    
    def get_context(self, agent: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent context for an agent."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT context_data FROM maat_agent_memory WHERE agent = %s
            """, (agent,))
            result = cur.fetchone()
            if result:
                context = result['context_data'] or []
                return context[-limit:] if isinstance(context, list) else []
            return []
        except Exception as e:
            log.error(f"Failed to get context: {e}")
            return []
        finally:
            cur.close()
    
    def add_context(self, agent: str, context_entry: Dict[str, Any]):
        """Add context entry for an agent."""
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            context_entry["timestamp"] = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO maat_agent_memory (agent, context_data, last_updated)
                VALUES (%s, %s, NOW())
                ON CONFLICT (agent) DO UPDATE SET
                    context_data = maat_agent_memory.context_data || %s::jsonb,
                    last_updated = NOW(),
                    updated_at = NOW()
            """, (agent, json.dumps([context_entry]), json.dumps([context_entry])))
            
            # Keep last 100 entries
            cur.execute("""
                UPDATE maat_agent_memory
                SET context_data = (
                    SELECT jsonb_agg(elem)
                    FROM (
                        SELECT elem
                        FROM jsonb_array_elements(context_data) AS elem
                        ORDER BY (elem->>'timestamp') DESC
                        LIMIT 100
                    ) AS limited
                )
                WHERE agent = %s
            """, (agent,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to add context: {e}")
            raise
        finally:
            cur.close()
    
    def get_recent_work(self, agent: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent work history for an agent."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT work_history FROM maat_agent_memory WHERE agent = %s
            """, (agent,))
            result = cur.fetchone()
            if result:
                work_history = result['work_history'] or []
                return work_history[-limit:] if isinstance(work_history, list) else []
            return []
        except Exception as e:
            log.error(f"Failed to get work history: {e}")
            return []
        finally:
            cur.close()
    
    def add_work_history(self, agent: str, work_entry: Dict[str, Any]):
        """Add work history entry."""
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            work_entry["timestamp"] = datetime.now().isoformat()
            
            cur.execute("""
                INSERT INTO maat_agent_memory (agent, work_history, last_updated)
                VALUES (%s, %s, NOW())
                ON CONFLICT (agent) DO UPDATE SET
                    work_history = maat_agent_memory.work_history || %s::jsonb,
                    last_updated = NOW(),
                    updated_at = NOW()
            """, (agent, json.dumps([work_entry]), json.dumps([work_entry])))
            
            # Keep last 200 entries
            cur.execute("""
                UPDATE maat_agent_memory
                SET work_history = (
                    SELECT jsonb_agg(elem)
                    FROM (
                        SELECT elem
                        FROM jsonb_array_elements(work_history) AS elem
                        ORDER BY (elem->>'timestamp') DESC
                        LIMIT 200
                    ) AS limited
                )
                WHERE agent = %s
            """, (agent,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to add work history: {e}")
            raise
        finally:
            cur.close()

    def get_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        agent: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get tasks from maat_tasks (optional status/priority/agent filters)."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            conditions = []
            params: List[Any] = []
            if status:
                conditions.append("status = %s")
                params.append(status)
            if priority:
                conditions.append("priority = %s")
                params.append(priority)
            if agent:
                conditions.append("agent = %s")
                params.append(agent)
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            cur.execute(
                f"""
                SELECT id, created_at, updated_at, agent, title, description,
                       status, priority, related_files, dependencies, completion_notes
                FROM maat_tasks
                WHERE {where_clause}
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
                LIMIT %s
                """,
                params + [limit],
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            log.error(f"Failed to get tasks: {e}")
            return []
        finally:
            cur.close()

    def get_decisions(
        self,
        agent: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get recent decisions from maat_decisions."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            conditions = []
            params: List[Any] = []
            if agent:
                conditions.append("agent = %s")
                params.append(agent)
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            cur.execute(
                f"""
                SELECT id, timestamp, agent, context, options_considered,
                       decision_made, rationale, outcome, maat_alignment, created_at
                FROM maat_decisions
                WHERE {where_clause}
                ORDER BY COALESCE(timestamp, created_at) DESC
                LIMIT %s
                """,
                params + [limit],
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            log.error(f"Failed to get decisions: {e}")
            return []
        finally:
            cur.close()

    def get_learnings(
        self,
        agent: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get learnings from maat_learnings."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            conditions = []
            params: List[Any] = []
            if agent:
                conditions.append("agent = %s")
                params.append(agent)
            if topic:
                conditions.append("topic ILIKE %s")
                params.append(f"%{topic}%")
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            cur.execute(
                f"""
                SELECT id, timestamp, agent, topic, insight, source,
                       confidence, applied, application_context, created_at
                FROM maat_learnings
                WHERE {where_clause}
                ORDER BY COALESCE(timestamp, created_at) DESC
                LIMIT %s
                """,
                params + [limit],
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            log.error(f"Failed to get learnings: {e}")
            return []
        finally:
            cur.close()

    def get_recent_changes(
        self,
        agent: Optional[str] = None,
        file_path: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get recent file/audit changes from maat_changes."""
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            conditions = []
            params: List[Any] = []
            if agent:
                conditions.append("agent = %s")
                params.append(agent)
            if file_path:
                conditions.append("file_path ILIKE %s")
                params.append(f"%{file_path}%")
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            cur.execute(
                f"""
                SELECT id, timestamp, agent, file_path, change_type, summary,
                       diff_preview, reason, reverted, revert_reason, created_at
                FROM maat_changes
                WHERE {where_clause}
                ORDER BY COALESCE(timestamp, created_at) DESC
                LIMIT %s
                """,
                params + [limit],
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            log.error(f"Failed to get recent changes: {e}")
            return []
        finally:
            cur.close()

    def get_artifacts(
        self,
        *,
        audience: Optional[str] = None,
        slug: Optional[str] = None,
        status: str = "active%",
        portable_only: bool = False,
        ring: Optional[str] = None,
        viewer_ring: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List maat_artifacts catalog (prefer portable_uri / content_sha256).

        ring: exact visibility tier filter.
        viewer_ring: max clearance — returns artifacts at or below that tier
        (outer viewer sees only outer; inner sees all).
        """
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            conditions = ["status LIKE %s"]
            params: List[Any] = [status]
            if audience:
                conditions.append("metadata->>'audience' = %s")
                params.append(audience)
            if slug:
                conditions.append("metadata->>'slug' = %s")
                params.append(slug)
            if portable_only:
                conditions.append("content_sha256 IS NOT NULL")
            if ring:
                conditions.append("ring = %s")
                params.append(ring)
            if viewer_ring in ("outer", "middle", "inner"):
                rank = {"outer": 0, "middle": 1, "inner": 2}[viewer_ring]
                conditions.append(
                    """
                    CASE COALESCE(ring, 'outer')
                        WHEN 'outer' THEN 0
                        WHEN 'middle' THEN 1
                        WHEN 'inner' THEN 2
                        ELSE 0
                    END <= %s
                    """
                )
                params.append(rank)
            cur.execute(
                f"""
                SELECT id, artifact_type, title, description, uri, portable_uri,
                       content_sha256, status, agent, machine, produced_at,
                       ring, metadata, metrics, created_at, updated_at
                FROM maat_artifacts
                WHERE {' AND '.join(conditions)}
                ORDER BY produced_at DESC NULLS LAST, created_at DESC
                LIMIT %s
                """,
                params + [limit],
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            log.error(f"Failed to get artifacts: {e}")
            return []
        finally:
            cur.close()

    def fetch_artifact(self, uri_or_sha: str) -> Dict[str, Any]:
        """Fetch portable artifact bytes/text via Memory Plane object store."""
        try:
            from .memory_plane import ArtifactBank

            return ArtifactBank().fetch(uri_or_sha)
        except Exception as e:
            log.error(f"Failed to fetch artifact: {e}")
            return {"ok": False, "error": str(e)}

    def log_artifact(
        self,
        agent: str,
        title: str,
        uri: str,
        *,
        description: str = "",
        artifact_type: str = "html_artifact",
        machine: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        status: str = "active",
        content_sha256: Optional[str] = None,
        portable_uri: Optional[str] = None,
        content_origin: Optional[str] = None,
        storage_class: Optional[str] = None,
    ) -> str:
        """Register or upsert a catalog row in maat_artifacts."""
        from .maat_provenance import parse_origin

        artifact_id = str(uuid.uuid4())
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            mid = machine or "unknown"
            # Both content_origin and storage_class are NOT NULL columns on
            # maat_artifacts. content_origin follows the same provenance rule
            # as the log_* helpers (default 'agent_authored' if absent is wrong
            # — caller's absence is not compliance). We require an explicit value
            # and surface a clear error otherwise.
            try:
                origin_value = parse_origin(content_origin).value
            except Exception:
                raise ValueError(
                    "log_artifact requires explicit content_origin "
                    "(e.g. 'agent_authored', 'operator_supplied', 'external_audit')"
                )
            storage_value = storage_class or (
                "object_backed" if (uri.startswith("maat://") or content_sha256) else "local_file"
            )
            cur.execute(
                """
                INSERT INTO maat_artifacts (
                    id, agent, machine, artifact_type, title, description, uri,
                    metrics, metadata, status, content_sha256, portable_uri,
                    content_origin, storage_class
                ) VALUES (
                    %s::uuid, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    artifact_id,
                    agent,
                    mid,
                    artifact_type,
                    title,
                    description,
                    uri,
                    json.dumps(metrics or {}),
                    json.dumps(metadata or {}),
                    status,
                    content_sha256,
                    portable_uri or (uri if uri.startswith("maat://") else None),
                    origin_value,
                    storage_value,
                ),
            )
            conn.commit()
            return artifact_id
        except Exception as e:
            conn.rollback()
            log.error(f"Failed to log artifact: {e}")
            raise
        finally:
            cur.close()

    def close(self):
        """Close database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None

