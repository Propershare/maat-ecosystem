"""
Audit Trail System
Maat: Truth - Track all actions for accountability and learning
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

from core.integrations.postgres import get_postgres_connection
from config.shared_config import get_shared_config

log = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""
    ACCESS = "access"
    QUERY = "query"
    MODIFY = "modify"
    CREATE = "create"
    DELETE = "delete"
    POLICY_VIOLATION = "policy_violation"
    CLASSIFICATION = "classification"
    SYSTEM = "system"


@dataclass
class AuditEvent:
    """Represents an audit event."""
    event_type: AuditEventType
    actor: str  # User ID, agent ID, or system
    action: str
    resource: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    success: bool = True
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class AuditTrail:
    """
    Audit trail system for tracking all actions.
    
    Stores audit events in PostgreSQL for persistence and analysis.
    """
    
    def __init__(self):
        self.config = get_shared_config()
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure audit trail table exists."""
        try:
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS maat_audit_trail (
                            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                            event_type VARCHAR(50) NOT NULL,
                            actor VARCHAR(255) NOT NULL,
                            action VARCHAR(255) NOT NULL,
                            resource VARCHAR(500),
                            metadata JSONB DEFAULT '{}'::jsonb,
                            timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            success BOOLEAN NOT NULL DEFAULT TRUE,
                            error TEXT,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                        );
                        
                        CREATE INDEX IF NOT EXISTS maat_audit_trail_event_type_idx 
                        ON maat_audit_trail(event_type);
                        
                        CREATE INDEX IF NOT EXISTS maat_audit_trail_actor_idx 
                        ON maat_audit_trail(actor);
                        
                        CREATE INDEX IF NOT EXISTS maat_audit_trail_timestamp_idx 
                        ON maat_audit_trail(timestamp);
                        
                        CREATE INDEX IF NOT EXISTS maat_audit_trail_metadata_idx 
                        ON maat_audit_trail USING GIN (metadata);
                    """)
                    conn.commit()
                    log.info("Audit trail table ensured")
        except Exception as e:
            log.error(f"Failed to ensure audit trail table: {e}")
    
    def log(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> Optional[str]:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            actor: Who performed the action
            action: What action was performed
            resource: Resource affected
            metadata: Additional metadata
            success: Whether action succeeded
            error: Error message if failed
        
        Returns:
            Event ID if successful, None otherwise
        """
        event = AuditEvent(
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            metadata=metadata or {},
            success=success,
            error=error
        )
        
        try:
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO maat_audit_trail (
                            event_type, actor, action, resource, metadata, 
                            timestamp, success, error
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        event.event_type.value,
                        event.actor,
                        event.action,
                        event.resource,
                        json.dumps(event.metadata),
                        event.timestamp,
                        event.success,
                        event.error
                    ))
                    event_id = cur.fetchone()[0]
                    conn.commit()
                    log.debug(f"Audit event logged: {event_id}")
                    return str(event_id)
        except Exception as e:
            log.error(f"Failed to log audit event: {e}")
            return None
    
    def query(
        self,
        actor: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit trail.
        
        Args:
            actor: Filter by actor
            event_type: Filter by event type
            action: Filter by action
            resource: Filter by resource
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum results
        
        Returns:
            List of audit events
        """
        try:
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    conditions = []
                    params = []
                    
                    if actor:
                        conditions.append("actor = %s")
                        params.append(actor)
                    
                    if event_type:
                        conditions.append("event_type = %s")
                        params.append(event_type.value)
                    
                    if action:
                        conditions.append("action = %s")
                        params.append(action)
                    
                    if resource:
                        conditions.append("resource = %s")
                        params.append(resource)
                    
                    if start_time:
                        conditions.append("timestamp >= %s")
                        params.append(start_time)
                    
                    if end_time:
                        conditions.append("timestamp <= %s")
                        params.append(end_time)
                    
                    where_clause = " AND ".join(conditions) if conditions else "1=1"
                    
                    cur.execute(f"""
                        SELECT 
                            id, event_type, actor, action, resource, 
                            metadata, timestamp, success, error, created_at
                        FROM maat_audit_trail
                        WHERE {where_clause}
                        ORDER BY timestamp DESC
                        LIMIT %s
                    """, params + [limit])
                    
                    results = []
                    for row in cur.fetchall():
                        results.append({
                            "id": str(row[0]),
                            "event_type": row[1],
                            "actor": row[2],
                            "action": row[3],
                            "resource": row[4],
                            "metadata": row[5] if row[5] else {},
                            "timestamp": row[6].isoformat() if row[6] else None,
                            "success": row[7],
                            "error": row[8],
                            "created_at": row[9].isoformat() if row[9] else None,
                        })
                    
                    return results
        except Exception as e:
            log.error(f"Failed to query audit trail: {e}")
            return []

