"""
Autonomous Task Execution Agent
Maat: Order - Executes tasks from Maat Memory autonomously
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import Maat Memory
import sys
from pathlib import Path
maatlangchain_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(maatlangchain_root))
from maat_memory.memory_postgres import MaatMemoryPostgres as MaatMemory
try:
    from maat_memory.machine_info import get_unique_agent_id
except ImportError:
    import socket
    def get_unique_agent_id(prefix: str) -> str:
        return f"{prefix}_{socket.gethostname()}"
from core.agents.ocr_agent import OCRAgent
from core.governance.tehuti_guard import TehutiGuard

log = logging.getLogger(__name__)


class TaskState(dict):
    """State for task execution."""
    pass


class TaskExecutor:
    """
    Autonomous task execution agent.
    
    Reads tasks from Maat Memory and executes them autonomously
    using appropriate agent workflows.
    """
    
    def __init__(self, memory: Optional[MaatMemory] = None):
        """
        Initialize task executor.
        
        Args:
            memory: Maat Memory instance
        """
        self.memory = memory or MaatMemory()
        self.agent_id = get_unique_agent_id("task_executor")
        self.tehuti_guard = TehutiGuard()
        
        # Initialize specialized agents
        self.ocr_agent = OCRAgent(memory=self.memory)
        from core.agents.k2_agent import K2Agent
        self.k2_agent = K2Agent(memory=self.memory)
        
        # Build workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for task execution."""
        workflow = StateGraph(TaskState)
        
        # Add nodes
        workflow.add_node("fetch_task", self._fetch_task)
        workflow.add_node("classify_task", self._classify_task)
        workflow.add_node("execute_ocr", self._execute_ocr)
        workflow.add_node("execute_document", self._execute_document)
        workflow.add_node("execute_rag", self._execute_rag)
        workflow.add_node("execute_k2", self._execute_k2)
        workflow.add_node("update_status", self._update_status)
        workflow.add_node("log_completion", self._log_completion)
        
        # Set entry point
        workflow.set_entry_point("fetch_task")
        
        # Add edges
        workflow.add_edge("fetch_task", "classify_task")
        workflow.add_conditional_edges(
            "classify_task",
            self._route_to_agent,
            {
                "ocr": "execute_ocr",
                "document": "execute_document",
                "rag": "execute_rag",
                "k2": "execute_k2",
                "research": "execute_k2",  # Research tasks use K2
                "unknown": "update_status"
            }
        )
        workflow.add_edge("execute_ocr", "update_status")
        workflow.add_edge("execute_document", "update_status")
        workflow.add_edge("execute_rag", "update_status")
        workflow.add_edge("execute_k2", "update_status")
        workflow.add_edge("update_status", "log_completion")
        workflow.add_edge("log_completion", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _fetch_task(self, state: TaskState) -> TaskState:
        """Fetch pending task from Maat Memory."""
        try:
            tasks = self.memory.get_tasks(status="pending", limit=1)
            
            if not tasks:
                return {
                    **state,
                    "status": "no_tasks",
                    "message": "No pending tasks found"
                }
            
            task = tasks[0]
            return {
                **state,
                "task": task,
                "task_id": task.get("id"),
                "task_title": task.get("title"),
                "task_description": task.get("description"),
                "status": "fetched"
            }
            
        except Exception as e:
            log.error(f"Failed to fetch task: {e}")
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def _classify_task(self, state: TaskState) -> TaskState:
        """Classify task type."""
        task_description = state.get("task_description", "").lower()
        title = state.get("task_title", "").lower()
        
        # Simple classification based on keywords
        if any(keyword in task_description or keyword in title 
               for keyword in ["k2", "dialectical", "contradiction", "unity", "opposites", 
                              "revolutionary", "transformation", "dialectical analysis"]):
            task_type = "k2"
        elif any(keyword in task_description or keyword in title 
                 for keyword in ["research", "study", "analyze", "investigate", "methodology"]):
            task_type = "research"  # Routes to K2 for dialectical analysis
        elif any(keyword in task_description or keyword in title 
                 for keyword in ["ocr", "image", "extract text", "scan"]):
            task_type = "ocr"
        elif any(keyword in task_description or keyword in title 
                 for keyword in ["document", "pdf", "process", "ingest"]):
            task_type = "document"
        elif any(keyword in task_description or keyword in title 
                 for keyword in ["rag", "query", "search", "retrieve"]):
            task_type = "rag"
        else:
            task_type = "unknown"
        
        return {
            **state,
            "task_type": task_type,
            "status": "classified"
        }
    
    def _execute_ocr(self, state: TaskState) -> TaskState:
        """Execute OCR task."""
        try:
            task_description = state.get("task_description", "")
            
            # Extract image path from task description
            # In production, this would parse task metadata
            image_path = self._extract_image_path(task_description)
            
            if not image_path:
                return {
                    **state,
                    "status": "error",
                    "error": "No image path found in task"
                }
            
            # Execute OCR
            result = self.ocr_agent.process(image_path)
            
            return {
                **state,
                "execution_result": result,
                "status": result.get("status", "completed")
            }
            
        except Exception as e:
            log.error(f"OCR execution failed: {e}")
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def _execute_document(self, state: TaskState) -> TaskState:
        """Execute document processing task."""
        # TODO: Implement document processing agent
        return {
            **state,
            "status": "not_implemented",
            "message": "Document processing agent not yet implemented"
        }
    
    def _execute_rag(self, state: TaskState) -> TaskState:
        """Execute RAG query task."""
        # TODO: Implement RAG query agent
        return {
            **state,
            "status": "not_implemented",
            "message": "RAG query agent not yet implemented"
        }
    
    def _execute_k2(self, state: TaskState) -> TaskState:
        """Execute K2 dialectical analysis task."""
        try:
            task_description = state.get("task_description", "")
            
            # Extract unity description from task
            unity_description = self._extract_unity_description(task_description)
            
            if not unity_description:
                return {
                    **state,
                    "status": "error",
                    "error": "No unity/system description found in task"
                }
            
            # Execute K2 analysis
            result = self.k2_agent.analyze(unity_description)
            
            return {
                **state,
                "execution_result": result,
                "status": result.get("status", "completed")
            }
            
        except Exception as e:
            log.error(f"K2 execution failed: {e}")
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_unity_description(self, description: str) -> Optional[str]:
        """Extract unity/system description from task description."""
        # Simple extraction - in production, use LLM to extract
        # For now, return the description as-is if it contains relevant keywords
        if any(keyword in description.lower() for keyword in 
               ["system", "unity", "process", "relationship", "organization", "movement"]):
            return description
        return None
    
    def _update_status(self, state: TaskState) -> TaskState:
        """Update task status in Maat Memory."""
        try:
            task_id = state.get("task_id")
            execution_status = state.get("status")
            
            if task_id:
                # Update task status
                new_status = "completed" if execution_status == "completed" else "in_progress"
                # TODO: Update task status in database
                log.info(f"Task {task_id} status: {new_status}")
            
            return {
                **state,
                "status": "updated"
            }
            
        except Exception as e:
            log.error(f"Failed to update status: {e}")
            return state
    
    def _log_completion(self, state: TaskState) -> TaskState:
        """Log task completion to Maat Memory."""
        try:
            task_id = state.get("task_id")
            execution_result = state.get("execution_result", {})
            
            # Log completion
            self.memory.log_change(
                agent=self.agent_id,
                file_path=f"task_{task_id}",
                change_type="completed",
                summary=f"Task completed: {state.get('task_title', 'Unknown')}",
                reason=f"Autonomous task execution: {execution_result.get('status', 'unknown')}"
            )
            
            return {
                **state,
                "status": "completed"
            }
            
        except Exception as e:
            log.error(f"Failed to log completion: {e}")
            return state
    
    def _route_to_agent(self, state: TaskState) -> str:
        """Route to appropriate agent based on task type."""
        task_type = state.get("task_type", "unknown")
        return task_type
    
    def _extract_image_path(self, description: str) -> Optional[str]:
        """Extract image path from task description."""
        # Simple extraction - in production, use proper parsing
        import re
        # Look for file paths
        paths = re.findall(r'[\'"]([^\'"]+\.(png|jpg|jpeg|gif|webp|tiff))[\'"]', description, re.IGNORECASE)
        if paths:
            return paths[0][0]
        return None
    
    def execute_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Execute pending tasks from Maat Memory.
        
        Args:
            limit: Maximum number of tasks to execute
            
        Returns:
            List of execution results
        """
        results = []
        
        for _ in range(limit):
            initial_state = TaskState()
            config = {"configurable": {"thread_id": f"task_exec_{datetime.now().isoformat()}"}}
            
            try:
                final_state = self.workflow.invoke(initial_state, config)
                
                if final_state.get("status") == "no_tasks":
                    break
                
                results.append({
                    "task_id": final_state.get("task_id"),
                    "status": final_state.get("status"),
                    "result": final_state.get("execution_result")
                })
                
            except Exception as e:
                log.error(f"Task execution failed: {e}")
                results.append({
                    "status": "error",
                    "error": str(e)
                })
        
        return results

