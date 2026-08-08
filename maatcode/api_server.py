"""
MaatCode OpenAPI Server for WebUI Integration
Maat: Order - Unified tool access via OpenAPI
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

# Add maatlangchain to path
workspace_root = Path(__file__).parent.parent
maatlangchain_path = workspace_root / "maatlangchain"
if str(maatlangchain_path) not in sys.path:
    sys.path.insert(0, str(maatlangchain_path))

from maat_memory import MaatMemory, get_unique_agent_id
from maat_memory.project_discovery import discover_project

log = logging.getLogger(__name__)

# Web search integration
workspace_root = Path(__file__).parent.parent
openwebui_path = workspace_root / "open-webui" / "backend"
if str(openwebui_path) not in sys.path:
    sys.path.insert(0, str(openwebui_path))

try:
    from open_webui.retrieval.web.searxng import search_searxng
    from open_webui.config import SEARXNG_QUERY_URL, WEB_SEARCH_RESULT_COUNT, WEB_SEARCH_DOMAIN_FILTER_LIST
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    WEB_SEARCH_AVAILABLE = False
    log.warning(f"Web search not available - {str(e)}")

# Initialize FastAPI app
app = FastAPI(
    title="MaatCode Tool Server",
    description="MaatCode tools for WebUI integration",
    version="1.0.0"
)

# Initialize Maat Memory
memory = MaatMemory()
agent_id = get_unique_agent_id("maatcode_api")


# Request/Response models
class GetTasksRequest(BaseModel):
    status: Optional[str] = "pending"
    limit: Optional[int] = 10
    agent: Optional[str] = None


class LogChangeRequest(BaseModel):
    file_path: str
    change_type: str
    description: str
    reason: Optional[str] = ""


class LogDecisionRequest(BaseModel):
    context: str
    decision: str
    rationale: str
    alternatives: Optional[List[str]] = []


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class AskQuestionRequest(BaseModel):
    question: str
    context: Optional[str] = ""


class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Search query to find information on the web")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return")


# Tool endpoints
@app.post("/tools/get_tasks")
async def get_tasks(request: GetTasksRequest):
    """Query tasks from gitMaat."""
    try:
        tasks = memory.get_tasks(
            status=request.status,
            limit=request.limit,
            agent=request.agent
        )
        return {
            "success": True,
            "count": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/log_change")
async def log_change(request: LogChangeRequest):
    """Log a file change to gitMaat."""
    try:
        memory.log_change(
            agent=agent_id,
            file_path=request.file_path,
            change_type=request.change_type,
            summary=request.description,
            reason=request.reason
        )
        return {
            "success": True,
            "message": f"Logged {request.change_type} to {request.file_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/log_decision")
async def log_decision(request: LogDecisionRequest):
    """Log a decision to gitMaat."""
    try:
        memory.log_decision(
            agent=agent_id,
            context=request.context,
            decision_made=request.decision,
            rationale=request.rationale,
            options_considered=request.alternatives
        )
        return {
            "success": True,
            "message": f"Logged decision: {request.decision}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/search_conversations")
async def search_conversations(request: SearchRequest):
    """Search past conversations in gitMaat."""
    try:
        results = memory.search_conversations(
            query=request.query,
            limit=request.limit
        )
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_recent_changes")
async def get_recent_changes(limit: int = 20, agent: Optional[str] = None):
    """Get recent file changes from gitMaat."""
    try:
        changes = memory.get_recent_changes(limit=limit, agent=agent)
        return {
            "success": True,
            "count": len(changes),
            "changes": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/discover_project")
async def discover_project_tool(project_path: Optional[str] = None):
    """Discover project structure and suggest builds."""
    try:
        discovery = discover_project(project_path)
        return {
            "success": True,
            "discovery": discovery
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/ask_question")
async def ask_question(request: AskQuestionRequest):
    """Ask a question to gitMaat for coordination."""
    try:
        # Log question as task
        memory.log_task(
            agent=agent_id,
            title=f"Question: {request.question[:50]}",
            description=f"{request.question}\n\nContext: {request.context}",
            status="pending",
            priority="normal"
        )
        
        # Log as conversation
        memory.log_conversation(
            agent=agent_id,
            user_query=f"QUESTION: {request.question}",
            agent_response="Question logged to gitMaat. Other agents can answer.",
            metadata={"type": "question", "context": request.context}
        )
        
        return {
            "success": True,
            "message": "Question logged to gitMaat. Other agents will see it and can answer.",
            "question": request.question
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openapi.json")
async def openapi():
    """Return OpenAPI spec for WebUI integration."""
    return get_openapi(
        title="MaatCode Tool Server",
        version="1.0.0",
        description="MaatCode tools for WebUI integration - gitMaat coordination, project discovery, and Maat governance",
        routes=app.routes
    )


@app.post("/tools/web_search")
async def web_search_endpoint(request: WebSearchRequest):
    """Search the web using SearXNG and return formatted results."""
    if not WEB_SEARCH_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Web search not available - open-webui dependencies not found"
        )
    
    try:
        searxng_url = SEARXNG_QUERY_URL.value if SEARXNG_QUERY_URL.value else "http://localhost:8080/search"
        result_count = request.max_results if request.max_results else WEB_SEARCH_RESULT_COUNT.value
        
        # Perform search
        results = search_searxng(
            searxng_url,
            request.query,
            result_count,
            WEB_SEARCH_DOMAIN_FILTER_LIST.value if WEB_SEARCH_DOMAIN_FILTER_LIST.value else []
        )
        
        # Format results
        if not results:
            return {
                "success": True,
                "query": request.query,
                "results": [],
                "message": f"No results found for query: {request.query}"
            }
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.title or "No title",
                "url": result.link,
                "snippet": result.snippet or ""
            })
        
        return {
            "success": True,
            "query": request.query,
            "count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        log.error(f"Web search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web search failed: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "maatcode_api",
        "agent_id": agent_id,
        "web_search_available": WEB_SEARCH_AVAILABLE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8025)

