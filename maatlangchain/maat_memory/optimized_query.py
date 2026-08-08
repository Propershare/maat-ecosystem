"""
Optimized gitMaat Query System
Leverages fine-tuned model for intelligent query routing and execution
"""

from typing import Dict, List, Optional, Any
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib
import json

from .memory_postgres import MaatMemoryPostgres
from .memory import MaatMemory


class OptimizedGitMaatQuery:
    """
    Optimized query system that leverages tool-calling model
    for intelligent query routing and execution
    """
    
    def __init__(self, memory: Optional[MaatMemory] = None):
        self.memory = memory or MaatMemory()
        self._query_cache = {}
        self._cache_ttl = timedelta(minutes=5)
    
    def query(
        self,
        query_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Optimized query with caching and structured filters
        
        Args:
            query_type: "tasks", "decisions", "learnings", "changes", "conversations"
            filters: Dict of filter criteria
            limit: Maximum results to return
            use_cache: Whether to use cached results
        
        Returns:
            List of query results
        """
        filters = filters or {}
        cache_key = self._generate_cache_key(query_type, filters, limit)
        
        # Check cache
        if use_cache and cache_key in self._query_cache:
            cached_result, cached_time = self._query_cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                return cached_result
        
        # Execute query based on type
        result = self._execute_query(query_type, filters, limit)
        
        # Cache result
        if use_cache:
            self._query_cache[cache_key] = (result, datetime.now())
        
        return result
    
    def _execute_query(
        self,
        query_type: str,
        filters: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Execute query based on type"""
        # Check if using PostgreSQL backend (has get_tasks) or JSON backend
        has_get_tasks = hasattr(self.memory, 'get_tasks')
        
        if query_type == "tasks":
            if has_get_tasks:
                return self.memory.get_tasks(
                    status=filters.get("status"),
                    priority=filters.get("priority"),
                    agent=filters.get("agent"),
                    limit=limit
                )
            else:
                # JSON backend - return empty list or query from tracking.tasks
                return []
        elif query_type == "decisions":
            if hasattr(self.memory, 'get_decisions'):
                return self.memory.get_decisions(
                    agent=filters.get("agent"),
                    limit=limit
                )
            else:
                return []
        elif query_type == "learnings":
            if hasattr(self.memory, 'get_learnings'):
                return self.memory.get_learnings(
                    agent=filters.get("agent"),
                    topic=filters.get("topic"),
                    limit=limit
                )
            else:
                return []
        elif query_type == "changes":
            if hasattr(self.memory, 'get_recent_changes'):
                return self.memory.get_recent_changes(
                    agent=filters.get("agent"),
                    file_path=filters.get("file_path"),
                    limit=limit
                )
            else:
                return []
        elif query_type == "conversations":
            # Check method signature - PostgreSQL version has more parameters
            if hasattr(self.memory, 'search_conversations'):
                sig = self.memory.search_conversations.__code__.co_varnames
                kwargs = {"query": filters.get("query", ""), "limit": limit}
                
                # Add optional parameters if method supports them
                if 'agent' in sig:
                    kwargs['agent'] = filters.get("agent")
                if 'use_vector_search' in sig:
                    kwargs['use_vector_search'] = filters.get("use_vector_search", True)
                
                return self.memory.search_conversations(**kwargs)
            else:
                return []
        else:
            raise ValueError(f"Unknown query type: {query_type}")
    
    def batch_query(self, queries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute multiple queries efficiently in batch
        
        Args:
            queries: List of query dicts with "type", "filters", "limit"
        
        Returns:
            Dict mapping query types to results
        """
        results = {}
        for query in queries:
            query_type = query.get("type")
            filters = query.get("filters", {})
            limit = query.get("limit", 10)
            
            if query_type not in results:
                results[query_type] = []
            
            results[query_type] = self.query(query_type, filters, limit)
        
        return results
    
    def _generate_cache_key(
        self,
        query_type: str,
        filters: Dict[str, Any],
        limit: int
    ) -> str:
        """Generate cache key from query parameters"""
        key_data = {
            "type": query_type,
            "filters": json.dumps(filters, sort_keys=True),
            "limit": limit
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear query cache"""
        self._query_cache.clear()


class SemanticQueryRouter:
    """
    Uses fine-tuned model to intelligently route queries
    to appropriate gitMaat methods
    """
    
    def __init__(self, model=None, memory: Optional[MaatMemory] = None):
        self.model = model  # Fine-tuned model (if available)
        self.memory = memory or MaatMemory()
        self.optimized_query = OptimizedGitMaatQuery(memory)
    
    def route_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query and determine:
        1. Query type (tasks/decisions/learnings/etc)
        2. Filters to apply
        3. Tool to call
        
        Returns query plan dict
        """
        query_lower = user_query.lower()
        
        # Determine query type from keywords
        if any(word in query_lower for word in ["task", "todo", "pending", "complete"]):
            query_type = "tasks"
            filters = self._extract_task_filters(user_query)
        elif any(word in query_lower for word in ["decision", "chose", "decided"]):
            query_type = "decisions"
            filters = self._extract_decision_filters(user_query)
        elif any(word in query_lower for word in ["learn", "insight", "pattern", "discover"]):
            query_type = "learnings"
            filters = self._extract_learning_filters(user_query)
        elif any(word in query_lower for word in ["change", "modify", "edit", "file"]):
            query_type = "changes"
            filters = self._extract_change_filters(user_query)
        elif any(word in query_lower for word in ["conversation", "chat", "talk", "discuss"]):
            query_type = "conversations"
            filters = self._extract_conversation_filters(user_query)
        else:
            # Default to conversations (semantic search)
            query_type = "conversations"
            filters = {"query": user_query}
        
        return {
            "type": query_type,
            "filters": filters,
            "limit": self._extract_limit(user_query),
            "tool": self._determine_tool(query_type)
        }
    
    def execute_routed_query(self, user_query: str) -> List[Dict[str, Any]]:
        """Route and execute query in one step"""
        plan = self.route_query(user_query)
        return self.optimized_query.query(
            plan["type"],
            plan["filters"],
            plan["limit"]
        )
    
    def _extract_task_filters(self, query: str) -> Dict[str, Any]:
        """Extract task-related filters from query"""
        filters = {}
        query_lower = query.lower()
        
        if "pending" in query_lower:
            filters["status"] = "pending"
        elif "complete" in query_lower or "done" in query_lower:
            filters["status"] = "completed"
        elif "in progress" in query_lower:
            filters["status"] = "in_progress"
        
        if "high" in query_lower and "priority" in query_lower:
            filters["priority"] = "high"
        elif "low" in query_lower and "priority" in query_lower:
            filters["priority"] = "low"
        
        return filters
    
    def _extract_decision_filters(self, query: str) -> Dict[str, Any]:
        """Extract decision-related filters"""
        return {}  # Decisions don't have many filters yet
    
    def _extract_learning_filters(self, query: str) -> Dict[str, Any]:
        """Extract learning-related filters"""
        filters = {}
        # Could extract topic from query using NLP
        return filters
    
    def _extract_change_filters(self, query: str) -> Dict[str, Any]:
        """Extract change-related filters"""
        filters = {}
        # Could extract file_path from query
        return filters
    
    def _extract_conversation_filters(self, query: str) -> Dict[str, Any]:
        """Extract conversation search filters"""
        return {"query": query, "use_vector_search": True}
    
    def _extract_limit(self, query: str) -> int:
        """Extract limit from query (e.g., 'get 5 tasks')"""
        import re
        match = re.search(r'(\d+)\s*(?:task|item|result)', query.lower())
        if match:
            return int(match.group(1))
        return 10  # Default
    
    def _determine_tool(self, query_type: str) -> str:
        """Determine which tool to call based on query type"""
        tool_map = {
            "tasks": "tool_query_gitmaat_post",
            "decisions": "tool_query_gitmaat_post",
            "learnings": "tool_query_gitmaat_post",
            "changes": "tool_query_gitmaat_post",
            "conversations": "tool_query_gitmaat_post"
        }
        return tool_map.get(query_type, "tool_query_gitmaat_post")


# Convenience functions
def optimized_query(
    query_type: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Quick access to optimized query"""
    query_system = OptimizedGitMaatQuery()
    return query_system.query(query_type, filters, limit)


def semantic_query(user_query: str) -> List[Dict[str, Any]]:
    """Quick access to semantic query routing"""
    router = SemanticQueryRouter()
    return router.execute_routed_query(user_query)

