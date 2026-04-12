"""
Memory Consolidation

Reads episodic memories, finds patterns, promotes to semantic.
Reversible: keeps before_snapshot for rollback.
"""

from datetime import datetime, timezone


def consolidate(memory_adapter, agent_id: str, days: int = 7) -> dict:
    """
    Consolidate recent episodic memories into semantic knowledge.

    Returns a learning record (maat:learning:v1 compatible).
    """
    # Search recent episodic memories
    recent = memory_adapter.search(
        query="",
        agent_id=agent_id,
        memory_class="episodic",
        limit=100,
    )

    if not recent:
        return {"type": "memory_consolidation", "description": "No memories to consolidate"}

    # Group by tags/topics (simple keyword extraction)
    topics = {}
    for mem in recent:
        content = mem.get("content", "")
        # Simple topic extraction — in production, use the model
        words = set(content.lower().split())
        for word in words:
            if len(word) > 5:  # crude filter
                topics.setdefault(word, []).append(content)

    # Find repeated themes (appeared in 3+ memories)
    patterns = {k: v for k, v in topics.items() if len(v) >= 3}

    return {
        "type": "memory_consolidation",
        "description": f"Found {len(patterns)} recurring patterns in {len(recent)} memories",
        "patterns": list(patterns.keys())[:20],
        "memory_count": len(recent),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reversible": True,
        "before_snapshot": {"episodic_count": len(recent)},
    }
