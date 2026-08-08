"""
LDAP Integration for gitMaat
Maat-Aligned LDAP Authentication Tracking

Logs LDAP authentication events and maps users to agents.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

log = logging.getLogger(__name__)


class LDAPIntegration:
    """LDAP integration for gitMaat tracking."""

    def __init__(self, memory):
        """
        Initialize LDAP integration.
        
        Args:
            memory: MaatMemory instance (PostgreSQL backend)
        """
        self.memory = memory

    def log_ldap_auth(
        self,
        agent: str,
        ldap_user: str,
        success: bool,
        groups: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log LDAP authentication event to gitMaat.
        
        Args:
            agent: Agent identifier
            ldap_user: LDAP username (uid)
            success: Whether authentication succeeded
            groups: LDAP groups user belongs to
            metadata: Additional metadata
            
        Returns:
            Audit trail entry ID
        """
        action = "ldap_auth_success" if success else "ldap_auth_failure"
        resource = f"ldap_user:{ldap_user}"
        
        audit_metadata = {
            "ldap_user": ldap_user,
            "success": success,
            "groups": groups or [],
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Log to audit trail
        self.memory.log_audit(
            agent=agent,
            action=action,
            resource=resource,
            before_data=None,
            after_data={"ldap_user": ldap_user, "groups": groups or []},
            reason=f"LDAP authentication {'succeeded' if success else 'failed'} for {ldap_user}",
            maat_compliance={
                "truth": True,  # Accurate authentication record
                "balance": True,  # Fair access control
                "order": True,  # Structured logging
                "self_reflection": True  # Complete audit trail
            },
            metadata=audit_metadata
        )
        
        log.info(f"Logged LDAP auth event: {action} for {ldap_user}")
        return action

    def get_ldap_user_groups(self, ldap_user: str) -> List[str]:
        """
        Get LDAP groups for a user from recent audit trail.
        
        Args:
            ldap_user: LDAP username (uid)
            
        Returns:
            List of group names
        """
        # Query audit trail for most recent successful auth
        audit_entries = self.memory.get_audit_trail(
            action="ldap_auth_success",
            resource=f"ldap_user:{ldap_user}",
            limit=1
        )
        
        if audit_entries and len(audit_entries) > 0:
            metadata = audit_entries[0].get("metadata", {})
            if isinstance(metadata, dict):
                return metadata.get("groups", [])
            elif isinstance(metadata, str):
                import json
                try:
                    metadata_dict = json.loads(metadata)
                    return metadata_dict.get("groups", [])
                except:
                    pass
        
        return []

    def map_ldap_to_agent(
        self,
        ldap_user: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Map LDAP user to agent ID in gitMaat.
        
        Args:
            ldap_user: LDAP username (uid)
            agent_id: Agent identifier (e.g., cursor_imhotep)
            metadata: Additional metadata
        """
        # Update agent memory with LDAP user mapping
        agent_memory = self.memory.get_agent_memory(agent_id)
        
        if agent_memory:
            # Update existing agent memory
            context_data = agent_memory.get("context_data", [])
            if isinstance(context_data, str):
                import json
                try:
                    context_data = json.loads(context_data)
                except:
                    context_data = []
            
            # Add LDAP user mapping
            ldap_mapping = {
                "ldap_user": ldap_user,
                "mapped_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            if not isinstance(context_data, list):
                context_data = []
            
            context_data.append(ldap_mapping)
            
            self.memory.update_agent_memory(
                agent=agent_id,
                context_data=context_data
            )
        else:
            # Create new agent memory entry
            context_data = [{
                "ldap_user": ldap_user,
                "mapped_at": datetime.now().isoformat(),
                **(metadata or {})
            }]
            
            # Use start_session to create agent memory
            self.memory.start_session(
                agent=agent_id,
                summary=f"LDAP user {ldap_user} mapped to agent",
                metadata={
                    "ldap_user": ldap_user,
                    **(metadata or {})
                }
            )
        
        log.info(f"Mapped LDAP user {ldap_user} to agent {agent_id}")

    def get_ldap_user_from_agent(self, agent_id: str) -> Optional[str]:
        """
        Get LDAP user mapped to an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            LDAP username or None
        """
        agent_memory = self.memory.get_agent_memory(agent_id)
        
        if agent_memory:
            context_data = agent_memory.get("context_data", [])
            if isinstance(context_data, str):
                import json
                try:
                    context_data = json.loads(context_data)
                except:
                    return None
            
            if isinstance(context_data, list) and len(context_data) > 0:
                # Get most recent LDAP mapping
                for entry in reversed(context_data):
                    if isinstance(entry, dict) and "ldap_user" in entry:
                        return entry["ldap_user"]
        
        return None

