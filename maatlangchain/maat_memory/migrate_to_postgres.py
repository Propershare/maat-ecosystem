#!/usr/bin/env python3
"""
Migration script to move Maat Memory from JSON to PostgreSQL.

This script:
1. Reads existing maat_memory.json
2. Creates PostgreSQL schema if needed
3. Migrates all data to PostgreSQL
4. Validates migration
"""

import json
import os
import sys
import psycopg2
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Allow running as script from repo
_here = Path(__file__).resolve()
_ml = _here.parent.parent  # maatlangchain/
if (_ml / "maat_memory").is_dir():
    sys.path.insert(0, str(_ml))
else:
    for _p in _here.parents:
        if (_p / "maatlangchain" / "maat_memory").is_dir():
            sys.path.insert(0, str(_p / "maatlangchain"))
            break

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from maat_memory.paths import get_maat_memory_json_path, get_pgvector_db_url

MAAT_MEMORY_JSON_PATH = get_maat_memory_json_path()


def get_pgvector_url() -> Optional[str]:
    """Get PostgreSQL connection string."""
    return get_pgvector_db_url()


def load_schema() -> str:
    """Load SQL schema from file."""
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        log.error(f"Schema file not found: {schema_path}")
        sys.exit(1)
    return schema_path.read_text()


def create_schema(conn):
    """Create PostgreSQL schema."""
    log.info("Creating PostgreSQL schema...")
    schema_sql = load_schema()
    cur = conn.cursor()
    cur.execute(schema_sql)
    conn.commit()
    log.info("✅ Schema created successfully")


def migrate_sessions(conn, data: Dict[str, Any]):
    """Migrate sessions to PostgreSQL."""
    log.info("Migrating sessions...")
    cur = conn.cursor()
    
    sessions = data.get("sessions", [])
    migrated = 0
    
    for session in sessions:
        try:
            cur.execute("""
                INSERT INTO maat_sessions (
                    id, agent, started_at, ended_at, summary, 
                    key_points, files_modified, tasks_completed
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                session["id"],
                session["agent"],
                session["started_at"],
                session.get("ended_at"),
                session.get("summary"),
                json.dumps(session.get("key_points", [])),
                json.dumps(session.get("files_modified", [])),
                json.dumps(session.get("tasks_completed", []))
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate session {session.get('id')}: {e}")
    
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(sessions)} sessions")


def migrate_conversations(conn, data: Dict[str, Any], embeddings_model=None):
    """Migrate conversations to PostgreSQL (without embeddings for now)."""
    log.info("Migrating conversations...")
    cur = conn.cursor()
    
    conversations = data.get("conversations", [])
    migrated = 0
    
    for conv in conversations:
        try:
            cur.execute("""
                INSERT INTO maat_conversations (
                    id, session_id, timestamp, agent, user_query, 
                    agent_response, tools_used, files_accessed, decisions_made
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                conv["id"],
                conv.get("session_id"),
                conv["timestamp"],
                conv["agent"],
                conv["user_query"],
                conv["agent_response"],
                json.dumps(conv.get("tools_used", [])),
                json.dumps(conv.get("files_accessed", [])),
                json.dumps(conv.get("decisions_made", []))
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate conversation {conv.get('id')}: {e}")
    
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(conversations)} conversations")
    log.info("   Note: Embeddings will be generated on-demand during queries")


def migrate_audit_trail(conn, data: Dict[str, Any]):
    """Migrate audit trail to PostgreSQL."""
    log.info("Migrating audit trail...")
    cur = conn.cursor()
    
    audit_entries = data.get("audit_trail", [])
    migrated = 0
    
    for entry in audit_entries:
        try:
            cur.execute("""
                INSERT INTO maat_audit_trail (
                    id, timestamp, agent, action, resource,
                    before_data, after_data, reason, maat_compliance
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                entry["id"],
                entry["timestamp"],
                entry["agent"],
                entry["action"],
                entry["resource"],
                json.dumps(entry.get("before")) if entry.get("before") else None,
                json.dumps(entry.get("after")) if entry.get("after") else None,
                entry.get("reason", ""),
                json.dumps(entry.get("maat_compliance", {}))
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate audit entry {entry.get('id')}: {e}")
    
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(audit_entries)} audit entries")


def migrate_tracking(conn, data: Dict[str, Any]):
    """Migrate tracking data (tasks, decisions, changes, errors, learnings)."""
    tracking = data.get("tracking", {})
    
    # Migrate tasks
    log.info("Migrating tasks...")
    cur = conn.cursor()
    tasks = tracking.get("tasks", [])
    migrated = 0
    for task in tasks:
        try:
            cur.execute("""
                INSERT INTO maat_tasks (
                    id, created_at, updated_at, agent, title, description,
                    status, priority, related_files, dependencies, completion_notes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                task["id"],
                task["created_at"],
                task["updated_at"],
                task["agent"],
                task["title"],
                task.get("description"),
                task["status"],
                task["priority"],
                json.dumps(task.get("related_files", [])),
                json.dumps(task.get("dependencies", [])),
                task.get("completion_notes")
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate task {task.get('id')}: {e}")
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(tasks)} tasks")
    
    # Migrate decisions
    log.info("Migrating decisions...")
    cur = conn.cursor()
    decisions = tracking.get("decisions", [])
    migrated = 0
    for decision in decisions:
        try:
            cur.execute("""
                INSERT INTO maat_decisions (
                    id, timestamp, agent, context, options_considered,
                    decision_made, rationale, outcome, maat_alignment
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                decision["id"],
                decision["timestamp"],
                decision["agent"],
                decision["context"],
                json.dumps(decision.get("options_considered", [])),
                decision["decision_made"],
                decision["rationale"],
                decision.get("outcome"),
                json.dumps(decision.get("maat_alignment", {}))
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate decision {decision.get('id')}: {e}")
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(decisions)} decisions")
    
    # Migrate changes
    log.info("Migrating changes...")
    cur = conn.cursor()
    changes = tracking.get("changes", [])
    migrated = 0
    for change in changes:
        try:
            cur.execute("""
                INSERT INTO maat_changes (
                    id, timestamp, agent, file_path, change_type,
                    summary, diff_preview, reason, reverted, revert_reason
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                change["id"],
                change["timestamp"],
                change["agent"],
                change["file_path"],
                change["change_type"],
                change["summary"],
                change.get("diff_preview"),
                change["reason"],
                change.get("reverted", False),
                change.get("revert_reason")
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate change {change.get('id')}: {e}")
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(changes)} changes")
    
    # Migrate errors
    log.info("Migrating errors...")
    cur = conn.cursor()
    errors = tracking.get("errors", [])
    migrated = 0
    for error in errors:
        try:
            cur.execute("""
                INSERT INTO maat_errors (
                    id, timestamp, agent, error_type, message,
                    stack_trace, context_data, resolution, prevention
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                error["id"],
                error["timestamp"],
                error["agent"],
                error["error_type"],
                error["message"],
                error.get("stack_trace"),
                json.dumps(error.get("context", {})),
                error.get("resolution"),
                error.get("prevention")
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate error {error.get('id')}: {e}")
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(errors)} errors")
    
    # Migrate learnings
    log.info("Migrating learnings...")
    cur = conn.cursor()
    learnings = tracking.get("learnings", [])
    migrated = 0
    for learning in learnings:
        try:
            cur.execute("""
                INSERT INTO maat_learnings (
                    id, timestamp, agent, topic, insight,
                    source, confidence, applied, application_context
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (
                learning["id"],
                learning["timestamp"],
                learning["agent"],
                learning["topic"],
                learning["insight"],
                learning["source"],
                learning.get("confidence", 0.5),
                learning.get("applied", False),
                learning.get("application_context")
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate learning {learning.get('id')}: {e}")
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(learnings)} learnings")


def migrate_agent_memory(conn, data: Dict[str, Any]):
    """Migrate agent memory to PostgreSQL."""
    log.info("Migrating agent memory...")
    cur = conn.cursor()
    
    agent_memory = data.get("agent_memory", {})
    migrated = 0
    
    for agent, mem in agent_memory.items():
        try:
            cur.execute("""
                INSERT INTO maat_agent_memory (
                    agent, session_id, last_updated,
                    context_data, preferences, work_history
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (agent) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    last_updated = EXCLUDED.last_updated,
                    context_data = EXCLUDED.context_data,
                    preferences = EXCLUDED.preferences,
                    work_history = EXCLUDED.work_history,
                    updated_at = NOW()
            """, (
                agent,
                mem.get("session_id"),
                mem.get("last_updated"),
                json.dumps(mem.get("context", [])),
                json.dumps(mem.get("preferences", {})),
                json.dumps(mem.get("work_history", []))
            ))
            if cur.rowcount > 0:
                migrated += 1
        except Exception as e:
            log.warning(f"Failed to migrate agent memory for {agent}: {e}")
    
    conn.commit()
    log.info(f"✅ Migrated {migrated}/{len(agent_memory)} agent memory entries")


def validate_migration(conn, data: Dict[str, Any]):
    """Validate migration by comparing counts."""
    log.info("Validating migration...")
    cur = conn.cursor()
    
    # Check sessions
    cur.execute("SELECT COUNT(*) FROM maat_sessions")
    sessions_count = cur.fetchone()[0]
    expected_sessions = len(data.get("sessions", []))
    
    # Check conversations
    cur.execute("SELECT COUNT(*) FROM maat_conversations")
    conversations_count = cur.fetchone()[0]
    expected_conversations = len(data.get("conversations", []))
    
    # Check audit trail
    cur.execute("SELECT COUNT(*) FROM maat_audit_trail")
    audit_count = cur.fetchone()[0]
    expected_audit = len(data.get("audit_trail", []))
    
    log.info(f"  Sessions: {sessions_count}/{expected_sessions}")
    log.info(f"  Conversations: {conversations_count}/{expected_conversations}")
    log.info(f"  Audit entries: {audit_count}/{expected_audit}")
    
    if (sessions_count == expected_sessions and 
        conversations_count == expected_conversations and
        audit_count == expected_audit):
        log.info("✅ Migration validation passed")
        return True
    else:
        log.warning("⚠️  Migration validation: some counts don't match")
        return False


def main():
    """Main migration function."""
    log.info("Starting Maat Memory migration to PostgreSQL...")
    
    # Load JSON data
    if not MAAT_MEMORY_JSON_PATH.exists():
        log.error(f"JSON file not found: {MAAT_MEMORY_JSON_PATH}")
        sys.exit(1)
    
    with open(MAAT_MEMORY_JSON_PATH, "r") as f:
        data = json.load(f)
    
    log.info(f"Loaded {len(data.get('sessions', []))} sessions from JSON")
    
    # Get PostgreSQL connection
    PGVECTOR_DB_URL = get_pgvector_url()
    if not PGVECTOR_DB_URL:
        log.error("PGVECTOR_DB_URL not found")
        sys.exit(1)
    
    log.info("Connecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(PGVECTOR_DB_URL)
        log.info("✅ Connected to PostgreSQL")
    except Exception as e:
        log.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)
    
    try:
        # Create schema
        create_schema(conn)
        
        # Migrate data
        migrate_sessions(conn, data)
        migrate_conversations(conn, data)
        migrate_audit_trail(conn, data)
        migrate_tracking(conn, data)
        migrate_agent_memory(conn, data)
        
        # Validate
        validate_migration(conn, data)
        
        log.info("✅ Migration complete!")
        log.info("   You can now use PostgreSQL backend for Maat Memory")
        log.info("   The JSON file will be kept as backup")
        
    except Exception as e:
        log.error(f"Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

