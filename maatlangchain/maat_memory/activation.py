"""
Maat Balance: gitMaat Activation System
Purpose: Enable automatic logging for all agents to activate gitMaat coordination
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps

# Add maatlangchain to path
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root / "maatlangchain") not in sys.path:
    sys.path.insert(0, str(workspace_root / "maatlangchain"))

from maat_memory import MaatMemory, get_unique_agent_id

log = logging.getLogger(__name__)


class GitMaatActivator:
    """Activates gitMaat logging for agents"""
    
    def __init__(self):
        self.memory = MaatMemory()
        self.activated_agents = set()
    
    def enable_agent_logging(self, agent_id: Optional[str] = None) -> bool:
        """
        Enable logging for an agent.
        
        Args:
            agent_id: Agent identifier (auto-detected if None)
            
        Returns:
            True if activation successful
        """
        if agent_id is None:
            agent_id = get_unique_agent_id("unknown")
        
        try:
            # Test connection
            self.memory.get_tasks(status="pending", limit=1)
            self.activated_agents.add(agent_id)
            log.info(f"✅ Activated gitMaat logging for agent: {agent_id}")
            return True
        except Exception as e:
            log.error(f"❌ Failed to activate gitMaat for {agent_id}: {e}")
            return False
    
    def auto_log_session(self, agent_id: str, action: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Automatically log agent session.
        
        Args:
            agent_id: Agent identifier
            action: Action description
            context: Optional context data
            
        Returns:
            Session ID if successful
        """
        if agent_id not in self.activated_agents:
            self.enable_agent_logging(agent_id)
        
        try:
            summary = f"{action}" + (f" - {context.get('summary', '')}" if context else "")
            session_id = self.memory.start_session(
                agent=agent_id,
                summary=summary
            )
            log.debug(f"Logged session {session_id} for {agent_id}: {action}")
            return session_id
        except Exception as e:
            log.error(f"Failed to log session for {agent_id}: {e}")
            return None
    
    def auto_log_task(self, agent_id: str, title: str, description: str, 
                     status: str = "pending", priority: str = "medium") -> Optional[int]:
        """
        Automatically create/update task.
        
        Args:
            agent_id: Agent identifier
            title: Task title
            description: Task description
            status: Task status (pending, in_progress, completed)
            priority: Task priority (high, medium, low)
            
        Returns:
            Task ID if successful
        """
        if agent_id not in self.activated_agents:
            self.enable_agent_logging(agent_id)
        
        try:
            task_id = self.memory.log_task(
                agent=agent_id,
                title=title,
                description=description,
                status=status,
                priority=priority
            )
            log.debug(f"Logged task {task_id} for {agent_id}: {title}")
            return task_id
        except Exception as e:
            log.error(f"Failed to log task for {agent_id}: {e}")
            return None
    
    def auto_log_change(self, agent_id: str, file_path: str, change_type: str,
                       description: str, reason: Optional[str] = None) -> Optional[int]:
        """
        Automatically log file change.
        
        Args:
            agent_id: Agent identifier
            file_path: File path
            change_type: Type of change (create, update, delete)
            description: Change description
            reason: Optional reason
            
        Returns:
            Change ID if successful
        """
        if agent_id not in self.activated_agents:
            self.enable_agent_logging(agent_id)
        
        try:
            change_id = self.memory.log_change(
                agent=agent_id,
                file_path=file_path,
                change_type=change_type,
                summary=description,
                reason=reason or ""
            )
            log.debug(f"Logged change {change_id} for {agent_id}: {file_path}")
            return change_id
        except Exception as e:
            log.error(f"Failed to log change for {agent_id}: {e}")
            return None


# Global activator instance
_activator = GitMaatActivator()


def activate_gitmaat(agent_id: Optional[str] = None) -> bool:
    """Convenience function to activate gitMaat for an agent."""
    return _activator.enable_agent_logging(agent_id)


def log_agent_action(agent_id: str, action: str, **kwargs):
    """Convenience function to log agent action."""
    return _activator.auto_log_session(agent_id, action, kwargs)


# Decorator for automatic logging
def gitmaat_logged(agent_id: Optional[str] = None):
    """
    Decorator to automatically log function calls to gitMaat.
    
    Usage:
        @gitmaat_logged(agent_id="my_agent")
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            agent = agent_id or get_unique_agent_id("decorated")
            _activator.enable_agent_logging(agent)
            
            # Log function call
            action = f"{func.__name__}({', '.join(map(str, args))})"
            session_id = _activator.auto_log_session(agent, action)
            
            try:
                result = func(*args, **kwargs)
                # Log success
                if session_id:
                    _activator.auto_log_change(
                        agent, 
                        f"function:{func.__name__}",
                        "execute",
                        f"Executed {func.__name__} successfully"
                    )
                return result
            except Exception as e:
                # Log error
                if session_id:
                    _activator.auto_log_change(
                        agent,
                        f"function:{func.__name__}",
                        "error",
                        f"Error in {func.__name__}: {str(e)}"
                    )
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test activation
    print("Testing gitMaat activation...")
    activator = GitMaatActivator()
    
    # Test agent activation
    test_agent = get_unique_agent_id("test")
    if activator.enable_agent_logging(test_agent):
        print(f"✅ Activated gitMaat for {test_agent}")
        
        # Test logging
        session_id = activator.auto_log_session(test_agent, "Test activation")
        task_id = activator.auto_log_task(test_agent, "Test Task", "Testing gitMaat activation")
        change_id = activator.auto_log_change(test_agent, "test.py", "create", "Test change")
        
        print(f"✅ Session logged: {session_id}")
        print(f"✅ Task logged: {task_id}")
        print(f"✅ Change logged: {change_id}")
    else:
        print("❌ Activation failed")

