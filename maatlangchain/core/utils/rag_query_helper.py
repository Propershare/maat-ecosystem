"""
RAG Query Helper for AI Assistant Integration
Provides easy-to-use functions for querying canon knowledge base via RAG
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

log = logging.getLogger(__name__)


def query_canon_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query canon knowledge base via RAG.
    
    Args:
        question: User question to answer
        top_k: Number of top documents to retrieve (default: 5)
    
    Returns:
        Dictionary with:
        {
            "answer": str,  # LLM-generated answer
            "sources": List[Dict],  # Source documents with metadata
            "confidence": str,  # Confidence level (high/medium/low)
            "metadata": Dict  # Additional metadata
        }
    """
    try:
        # Import here to avoid circular dependencies
        from api.main import get_rag_instance
        
        # Get RAG instance
        rag = get_rag_instance()
        
        # Query canon collection
        result = rag.query(
            question=question,
            collection_name="canon_kmt",
            top_k=top_k,
            llm_model="qwen2.5:14b",
            max_context_length=4000,
        )
        
        # Format response
        return {
            "answer": result.get("answer", "No answer generated"),
            "sources": result.get("sources", []),
            "confidence": result.get("metadata", {}).get("confidence", "unknown"),
            "metadata": result.get("metadata", {}),
        }
        
    except Exception as e:
        log.error(f"Error querying canon RAG: {e}")
        import traceback
        log.error(traceback.format_exc())
        return {
            "answer": f"I encountered an error while querying the canon knowledge base: {str(e)}",
            "sources": [],
            "confidence": "error",
            "metadata": {"error": str(e)},
        }


def search_canon_similar(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Search for similar documents in canon collection without LLM generation.
    
    Args:
        query: Search query
        top_k: Number of top results to return
    
    Returns:
        List of document dictionaries with content and metadata
    """
    try:
        from api.main import get_rag_instance
        
        rag = get_rag_instance()
        
        # Use search_similar for document retrieval only
        documents = rag.search_similar(
            query=query,
            collection_name="canon_kmt",
            top_k=top_k,
        )
        
        # Format documents
        results = []
        for i, doc in enumerate(documents, 1):
            results.append({
                "document_number": i,
                "content": doc.page_content,
                "metadata": doc.metadata,
                "file_name": doc.metadata.get("file_name", "unknown"),
                "title": doc.metadata.get("title", ""),
            })
        
        return results
        
    except Exception as e:
        log.error(f"Error searching canon: {e}")
        import traceback
        log.error(traceback.format_exc())
        return []


def get_canon_context(question: str, max_chars: int = 2000) -> str:
    """
    Get formatted context from canon for use in AI assistant responses.
    
    Args:
        question: Question to get context for
        max_chars: Maximum characters of context to return
    
    Returns:
        Formatted context string with sources
    """
    try:
        results = search_canon_similar(question, top_k=5)
        
        if not results:
            return "No relevant canon documents found."
        
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result["content"]
            file_name = result["file_name"]
            title = result.get("title", "")
            
            # Format source
            source_info = f"[Source: {file_name}"
            if title:
                source_info += f" - {title}"
            source_info += "]"
            
            doc_text = f"{content}\n{source_info}\n\n"
            
            if current_length + len(doc_text) > max_chars:
                # Truncate if needed
                remaining = max_chars - current_length - len(source_info) - 20
                if remaining > 100:
                    doc_text = f"{content[:remaining]}...\n{source_info}\n\n"
                else:
                    break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
            
            if current_length >= max_chars:
                break
        
        return "\n".join(context_parts)
        
    except Exception as e:
        log.error(f"Error getting canon context: {e}")
        return f"Error retrieving canon context: {str(e)}"

