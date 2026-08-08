#!/usr/bin/env python3
"""
Search UKMT RAG knowledge base for Clawdbot
Usage: python3 search-rag-clawdbot.py "query" [limit] [use_rag]
"""
import sys
import json
import os
from pathlib import Path

# Set workspace root
workspace_root = Path("/home/suspect/.n8n")
sys.path.insert(0, str(workspace_root / "maatlangchain"))

# Set database URL
os.environ["PGVECTOR_DB_URL"] = "postgresql://suspect:disdick@localhost:5432/maat_memory"

try:
    from maat_memory import MaatMemory
    
    memory = MaatMemory()
    
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    use_rag = sys.argv[3].lower() != "false" if len(sys.argv) > 3 else True
    
    if not query:
        print(json.dumps({"error": "No query provided", "count": 0, "results": []}))
        sys.exit(1)
    
    # Search knowledge base using RAG
    results = memory.search_conversations(
        query=query,
        limit=limit,
        use_vector_search=use_rag
    )
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "content": result.get("content", result.get("text", "")),
            "source": result.get("source", result.get("file", "Unknown")),
            "score": result.get("score", 0.0),
            "metadata": result.get("metadata", {})
        })
    
    print(json.dumps({
        "success": True,
        "query": query,
        "count": len(formatted_results),
        "results": formatted_results
    }, indent=2))
    
except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e),
        "count": 0,
        "results": []
    }))
