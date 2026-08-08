"""
Format session information for display.
Maat: Truth - Clear reporting of where data comes from.
"""

from typing import Dict, Any

def format_session_info(session: Dict[str, Any]) -> str:
    """Format session info for display with machine/terminal info."""
    metadata = session.get("metadata", {})
    
    lines = [
        f"Session ID: {session['id'][:8]}...",
        f"Agent: {session['agent']}",
        f"Machine: {metadata.get('hostname', 'unknown')} ({metadata.get('machine_id', 'unknown')})",
        f"Terminal: {metadata.get('terminal_id', 'unknown')}",
        f"Project: {metadata.get('project_path', 'unknown')}",
        f"Working Dir: {metadata.get('working_directory', 'unknown')}",
        f"Started: {session['started_at']}",
    ]
    
    if session.get('ended_at'):
        lines.append(f"Ended: {session['ended_at']}")
    
    if session.get('summary'):
        lines.append(f"Summary: {session['summary']}")
    
    return "\n".join(lines)

def format_conversation_info(conversation: Dict[str, Any]) -> str:
    """Format conversation info for display with machine/terminal info."""
    metadata = conversation.get("metadata", {})
    
    lines = [
        f"Conversation ID: {conversation['id'][:8]}...",
        f"Agent: {conversation['agent']}",
        f"Machine: {metadata.get('hostname', 'unknown')}",
        f"Terminal: {metadata.get('terminal_id', 'unknown')}",
        f"Timestamp: {conversation.get('timestamp', conversation.get('created_at', 'unknown'))}",
    ]
    
    if conversation.get('similarity'):
        lines.append(f"Similarity: {conversation['similarity']:.3f}")
    
    return "\n".join(lines)

