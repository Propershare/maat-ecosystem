"""
Maat Balance: Multi-Agent Coordination System
Purpose: Distribute tasks, balance workload, coordinate agents
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from maat_memory import MaatMemory, get_unique_agent_id

log = logging.getLogger(__name__)


class TaskDistributor:
    """Distributes tasks across agents for balanced workload"""
    
    def __init__(self):
        self.memory = MaatMemory()
    
    def get_agent_load(self, agent_id: str) -> int:
        """Get current task load for an agent."""
        try:
            tasks = self.memory.get_tasks(agent=agent_id, status="in_progress")
            return len(tasks)
        except Exception as e:
            log.error(f"Failed to get load for {agent_id}: {e}")
            return 0
    
    def assign_task(self, task: Dict[str, Any], available_agents: List[str]) -> Optional[str]:
        """
        Assign task to best agent based on load.
        
        Args:
            task: Task dictionary
            available_agents: List of available agent IDs
            
        Returns:
            Assigned agent ID or None
        """
        if not available_agents:
            return None
        
        # Get load for each agent
        agent_loads = {}
        for agent_id in available_agents:
            agent_loads[agent_id] = self.get_agent_load(agent_id)
        
        # Assign to agent with lowest load
        best_agent = min(agent_loads.items(), key=lambda x: x[1])[0]
        
        try:
            # Update task with assigned agent
            self.memory.log_task(
                agent=best_agent,
                title=task.get('title', ''),
                description=task.get('description', ''),
                status="in_progress",
                priority=task.get('priority', 'medium')
            )
            log.info(f"Assigned task to {best_agent} (load: {agent_loads[best_agent]})")
            return best_agent
        except Exception as e:
            log.error(f"Failed to assign task: {e}")
            return None
    
    def balance_load(self, agents: List[str]) -> Dict[str, int]:
        """
        Balance workload across agents.
        
        Args:
            agents: List of agent IDs
            
        Returns:
            Dictionary of agent loads
        """
        loads = {}
        for agent_id in agents:
            loads[agent_id] = self.get_agent_load(agent_id)
        
        # Redistribute if imbalance detected
        max_load = max(loads.values()) if loads else 0
        min_load = min(loads.values()) if loads else 0
        
        if max_load - min_load > 2:  # Threshold for rebalancing
            log.info(f"Load imbalance detected: {loads}")
            # Could implement task reassignment here
        
        return loads


class ConflictDetector:
    """Detects conflicts between tasks"""
    
    def __init__(self):
        self.memory = MaatMemory()
    
    def detect_conflicts(self, task1: Dict[str, Any], task2: Dict[str, Any]) -> bool:
        """
        Detect if two tasks conflict.
        
        Args:
            task1: First task
            task2: Second task
            
        Returns:
            True if conflict detected
        """
        # Check for file conflicts
        files1 = set(task1.get('related_files', []))
        files2 = set(task2.get('related_files', []))
        
        if files1 & files2:  # Overlapping files
            # Check if both are write operations
            if task1.get('change_type') in ['create', 'update', 'delete'] and \
               task2.get('change_type') in ['create', 'update', 'delete']:
                return True
        
        # Check for dependency conflicts
        deps1 = set(task1.get('dependencies', []))
        deps2 = set(task2.get('dependencies', []))
        
        if task1.get('id') in deps2 or task2.get('id') in deps1:
            return True
        
        return False
    
    def check_conflicts(self, new_task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check new task against existing tasks for conflicts.
        
        Args:
            new_task: New task to check
            
        Returns:
            List of conflicting tasks
        """
        try:
            active_tasks = self.memory.get_tasks(status="in_progress")
            conflicts = []
            
            for task in active_tasks:
                if self.detect_conflicts(new_task, task):
                    conflicts.append(task)
            
            return conflicts
        except Exception as e:
            log.error(f"Failed to check conflicts: {e}")
            return []


class DependencyResolver:
    """Resolves task dependencies"""
    
    def __init__(self):
        self.memory = MaatMemory()
    
    def resolve_dependencies(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Resolve task dependencies.
        
        Args:
            task: Task with dependencies
            
        Returns:
            List of dependency tasks in order
        """
        deps = task.get('dependencies', [])
        if not deps:
            return []
        
        try:
            dependency_tasks = []
            for dep_id in deps:
                # Get dependency task
                tasks = self.memory.get_tasks(status="all")
                dep_task = next((t for t in tasks if t.get('id') == dep_id), None)
                if dep_task:
                    dependency_tasks.append(dep_task)
            
            # Sort by dependency chain
            resolved = []
            remaining = dependency_tasks.copy()
            
            while remaining:
                for task in remaining:
                    task_deps = set(task.get('dependencies', []))
                    resolved_ids = {t.get('id') for t in resolved}
                    
                    if not task_deps or task_deps.issubset(resolved_ids):
                        resolved.append(task)
                        remaining.remove(task)
                        break
                else:
                    # Circular dependency or missing dependency
                    log.warning(f"Could not resolve all dependencies for task {task.get('id')}")
                    break
            
            return resolved
        except Exception as e:
            log.error(f"Failed to resolve dependencies: {e}")
            return []


class MultiAgentCoordinator:
    """Coordinates multiple agents"""
    
    def __init__(self):
        self.memory = MaatMemory()
        self.distributor = TaskDistributor()
        self.conflict_detector = ConflictDetector()
        self.dependency_resolver = DependencyResolver()
    
    def coordinate_task(self, task: Dict[str, Any], available_agents: List[str]) -> Dict[str, Any]:
        """
        Coordinate a task across agents.
        
        Args:
            task: Task to coordinate
            available_agents: List of available agents
            
        Returns:
            Coordination result
        """
        # Check for conflicts
        conflicts = self.conflict_detector.check_conflicts(task)
        if conflicts:
            log.warning(f"Task conflicts detected: {conflicts}")
            return {
                "status": "conflict",
                "conflicts": conflicts,
                "task": task
            }
        
        # Resolve dependencies
        dependencies = self.dependency_resolver.resolve_dependencies(task)
        if dependencies:
            log.info(f"Task has {len(dependencies)} dependencies")
            # Wait for dependencies or schedule after them
        
        # Assign task
        assigned_agent = self.distributor.assign_task(task, available_agents)
        if assigned_agent:
            return {
                "status": "assigned",
                "agent": assigned_agent,
                "task": task
            }
        else:
            return {
                "status": "failed",
                "reason": "No available agents",
                "task": task
            }
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status."""
        try:
            tasks = self.memory.get_tasks(status="all")
            agents = set(t.get('agent') for t in tasks if t.get('agent'))
            
            status = {
                "total_tasks": len(tasks),
                "active_agents": len(agents),
                "agent_loads": {}
            }
            
            for agent_id in agents:
                status["agent_loads"][agent_id] = self.distributor.get_agent_load(agent_id)
            
            return status
        except Exception as e:
            log.error(f"Failed to get coordination status: {e}")
            return {}


if __name__ == "__main__":
    # Test coordination
    coordinator = MultiAgentCoordinator()
    status = coordinator.get_coordination_status()
    print(f"Coordination status: {status}")

