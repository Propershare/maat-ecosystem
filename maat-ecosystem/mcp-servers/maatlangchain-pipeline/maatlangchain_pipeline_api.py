#!/usr/bin/env python3
"""
MaatLangChain Pipeline API Server
FastAPI server exposing pipeline tools as OpenAPI endpoints
Connects to Tehuti Core and integrates with n8n workflows
"""

import logging
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

# Add maatlangchain to path
workspace_root = Path(__file__).parent.parent.parent
maatlangchain_path = workspace_root / "maatlangchain"
if str(maatlangchain_path) not in sys.path:
    sys.path.insert(0, str(maatlangchain_path))

log = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MaatLangChain Pipeline API",
    description="RAG, agents, and knowledge base pipeline - connects to Tehuti Core and n8n workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load database URL from environment
PGVECTOR_DB_URL = os.getenv("PGVECTOR_DB_URL")
if not PGVECTOR_DB_URL:
    env_file = workspace_root / "tehuti-lab-webui" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("PGVECTOR_DB_URL="):
                    PGVECTOR_DB_URL = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

if PGVECTOR_DB_URL:
    os.environ["PGVECTOR_DB_URL"] = PGVECTOR_DB_URL
    log.info("✅ Database URL loaded from environment")
else:
    log.warning("⚠️  PGVECTOR_DB_URL not found")

# Initialize MaatMemory (lazy)
_memory = None

def get_memory():
    """Get MaatMemory instance."""
    global _memory
    if _memory is None:
        try:
            from maat_memory import MaatMemory
            _memory = MaatMemory()
            log.info("✅ MaatMemory initialized")
        except Exception as e:
            log.warning(f"MaatMemory not available: {e}")
            _memory = None
    return _memory


# Request/Response models
class SearchKnowledgeBaseRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(10, description="Maximum results")
    use_rag: Optional[bool] = Field(True, description="Use RAG for semantic search")


class QueryGitMaatRequest(BaseModel):
    query_type: str = Field("tasks", description="Type: tasks, changes, learnings, decisions, conversations")
    query: Optional[str] = Field(None, description="Semantic search query (for conversations)")
    status: Optional[str] = Field(None, description="Status filter (for tasks)")
    limit: Optional[int] = Field(10, description="Maximum results")
    agent: Optional[str] = Field(None, description="Filter by agent ID")


class ExecutePipelineRequest(BaseModel):
    topic: str = Field(..., description="Research topic")
    steps: Optional[List[str]] = Field(None, description="Pipeline steps to execute")
    use_gitmaat: Optional[bool] = Field(True, description="Query gitMaat first (Sankofa)")
    working_directory: Optional[str] = Field(None, description="Working directory")


class CreatePipelineTaskRequest(BaseModel):
    task_description: str = Field(..., description="Task description")
    pipeline_type: str = Field("research", description="Type: research, document, curriculum, etc.")
    priority: str = Field("normal", description="Priority: low, normal, high")
    working_directory: Optional[str] = Field(None, description="Working directory")


class TriggerN8nWorkflowRequest(BaseModel):
    workflow_id: str = Field(..., description="n8n workflow ID")
    parameters: Dict[str, Any] = Field(..., description="Workflow parameters")


# Tool endpoints
@app.post("/tools/search_knowledge_base")
async def search_knowledge_base(request: SearchKnowledgeBaseRequest):
    """Search MaatLangChain knowledge base using RAG."""
    try:
        memory = get_memory()
        if not memory:
            raise HTTPException(status_code=500, detail="MaatMemory not available. Check PGVECTOR_DB_URL.")
        
        results = memory.search_conversations(
            query=request.query,
            limit=request.limit,
            use_vector_search=request.use_rag
        )
        
        return {
            "success": True,
            "query": request.query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        log.exception(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/query_gitmaat_advanced")
async def query_gitmaat_advanced(request: QueryGitMaatRequest):
    """Advanced gitMaat query with semantic search support."""
    try:
        memory = get_memory()
        if not memory:
            raise HTTPException(status_code=500, detail="MaatMemory not available.")
        
        if request.query_type == "tasks":
            results = memory.get_tasks(status=request.status, limit=request.limit, agent=request.agent)
        elif request.query_type == "changes":
            results = memory.get_recent_changes(limit=request.limit, agent=request.agent)
        elif request.query_type == "learnings":
            results = memory.get_learnings(limit=request.limit)
        elif request.query_type == "decisions":
            results = memory.get_decisions(limit=request.limit)
        elif request.query_type == "conversations" and request.query:
            results = memory.search_conversations(
                query=request.query,
                limit=request.limit,
                agent=request.agent,
                use_vector_search=True
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown query_type: {request.query_type}")
        
        return {
            "success": True,
            "query_type": request.query_type,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        log.exception(f"Error querying gitMaat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/execute_research_pipeline")
async def execute_research_pipeline(request: ExecutePipelineRequest):
    """Execute full research pipeline using MaatLangChain + Tehuti Core."""
    try:
        memory = get_memory()
        results = {
            "topic": request.topic,
            "steps_completed": [],
            "results": {},
            "errors": []
        }
        
        # Default steps
        steps = request.steps or ["query_gitmaat", "search_knowledge_base", "synthesize"]
        
        # Step 1: Query gitMaat (Sankofa)
        if request.use_gitmaat and "query_gitmaat" in steps and memory:
            try:
                past_work = memory.search_conversations(
                    query=request.topic,
                    limit=5,
                    use_vector_search=True
                )
                results["results"]["past_work"] = past_work
                results["steps_completed"].append("query_gitmaat")
            except Exception as e:
                results["errors"].append(f"query_gitmaat: {str(e)}")
        
        # Step 2: Search knowledge base
        if "search_knowledge_base" in steps and memory:
            try:
                kb_results = memory.search_conversations(
                    query=request.topic,
                    limit=10,
                    use_vector_search=True
                )
                results["results"]["knowledge_base"] = kb_results
                results["steps_completed"].append("search_knowledge_base")
            except Exception as e:
                results["errors"].append(f"search_knowledge_base: {str(e)}")
        
        # Step 3: Synthesize (placeholder)
        if "synthesize" in steps:
            results["results"]["synthesis"] = {
                "status": "completed",
                "note": "Synthesis step - would use RAG/LLM here"
            }
            results["steps_completed"].append("synthesize")
        
        # Log to gitMaat
        if memory:
            try:
                from maat_memory import get_unique_agent_id
                agent_id = get_unique_agent_id("maatlangchain_pipeline")
                memory.log_task(
                    agent=agent_id,
                    title=f"Research Pipeline: {request.topic[:50]}",
                    description=f"Executed research pipeline on topic: {request.topic}",
                    status="completed" if not results["errors"] else "in_progress",
                    metadata={
                        "steps": results["steps_completed"],
                        "errors": results["errors"]
                    }
                )
            except Exception as e:
                log.warning(f"Failed to log to gitMaat: {e}")
        
        return {
            "success": True,
            **results
        }
    except Exception as e:
        log.exception(f"Error executing pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/create_pipeline_task")
async def create_pipeline_task(request: CreatePipelineTaskRequest):
    """Create a task in gitMaat for pipeline execution."""
    try:
        memory = get_memory()
        if not memory:
            raise HTTPException(status_code=500, detail="MaatMemory not available.")
        
        from maat_memory import get_unique_agent_id
        agent_id = get_unique_agent_id("maatlangchain_pipeline")
        
        task_id = memory.log_task(
            agent=agent_id,
            title=request.task_description[:100],
            description=request.task_description,
            status="pending",
            priority=request.priority,
            metadata={
                "pipeline_type": request.pipeline_type,
                "working_directory": request.working_directory,
                "source": "webui",
                "requires_pipeline": True
            }
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task created for {request.pipeline_type} pipeline",
            "status": "pending"
        }
    except Exception as e:
        log.exception(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/trigger_n8n_workflow")
async def trigger_n8n_workflow(request: TriggerN8nWorkflowRequest):
    """Trigger an n8n workflow (connects to Tehuti Integration)."""
    try:
        import aiohttp
        
        # Use Tehuti Integration server (port 8013)
        integration_url = "http://127.0.0.1:8013"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{integration_url}/tools/tehuti-integration/trigger-workflow",
                json={
                    "workflow_id": request.workflow_id,
                    "parameters": request.parameters
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return {
                        "success": True,
                        **result
                    }
                else:
                    error_text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=error_text)
                    
    except ImportError:
        raise HTTPException(status_code=500, detail="aiohttp not installed")
    except Exception as e:
        log.exception(f"Error triggering workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openapi.json")
async def openapi():
    """Return OpenAPI spec for WebUI integration."""
    return get_openapi(
        title="MaatLangChain Pipeline API",
        version="1.0.0",
        description="RAG, agents, and knowledge base pipeline - connects to Tehuti Core and n8n workflows",
        routes=app.routes
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    memory = get_memory()
    return {
        "status": "healthy",
        "service": "maatlangchain_pipeline_api",
        "memory_available": memory is not None,
        "pgvector_db_url": "set" if PGVECTOR_DB_URL else "not set"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)

