"""
Memory Consolidation Engine

Promotes episodic → semantic when patterns emerge.
Always reversible. Keeps before_snapshot.
"""

from datetime import datetime, timezone


class Consolidator:
    """
    Scans episodic memories, identifies patterns, creates semantic memories.

    This is the "learning" loop for memory — distinct from model learning.
    """

    def __init__(self, memory_adapter):
        self.memory = memory_adapter

    def find_candidates(self, agent_id: str, age_days: int = 7) -> list[dict]:
        """Find episodic memories ready for consolidation."""
        all_episodic = self.memory.search(
            query="",
            agent_id=agent_id,
            memory_class="episodic",
            limit=200,
        )
        return [m for m in all_episodic if self._is_old_enough(m, age_days)]

    def consolidate(self, agent_id: str, age_days: int = 7) -> dict:
        """
        Run one consolidation cycle.

        Returns a learning record compatible with maat:learning:v1.
        """
        candidates = self.find_candidates(agent_id, age_days)

        if not candidates:
            return {"status": "nothing_to_consolidate"}

        # Group by similarity (simple text overlap — use embeddings in production)
        groups = self._group_memories(candidates)

        created = 0
        for group_key, memories in groups.items():
            if len(memories) >= 2:  # pattern = 2+ similar memories
                summary = f"Pattern: {group_key} (from {len(memories)} episodic memories)"
                self.memory.write({
                    "agent_id": agent_id,
                    "memory_class": "semantic",
                    "content": summary,
                    "source": "consolidation",
                    "tags": ["consolidated", group_key],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reversible": True,
                })
                created += 1

        return {
            "type": "memory_consolidation",
            "candidates": len(candidates),
            "patterns_found": len(groups),
            "semantic_created": created,
            "reversible": True,
            "before_snapshot": {"episodic_count": len(candidates)},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _is_old_enough(memory: dict, age_days: int) -> bool:
        ts = memory.get("timestamp", "")
        if not ts:
            return False
        try:
            created = datetime.fromisoformat(ts)
            age = datetime.now(timezone.utc) - created
            return age.days >= age_days
        except Exception:
            return False

    @staticmethod
    def _group_memories(memories: list[dict]) -> dict[str, list]:
        """Simple keyword grouping. Replace with embedding similarity in production."""
        groups = {}
        for m in memories:
            words = set(m.get("content", "").lower().split())
            significant = [w for w in words if len(w) > 6]
            for word in significant[:3]:
                groups.setdefault(word, []).append(m)
        return {k: v for k, v in groups.items() if len(v) >= 2}
