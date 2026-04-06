"""
Episodic Memory Handler

Time-stamped event memories with automatic decay.
"""

from datetime import datetime, timezone, timedelta


def should_consolidate(memory: dict, age_days: int = 7) -> bool:
    """Check if an episodic memory is old enough to consolidate."""
    ts = memory.get("timestamp", "")
    if not ts:
        return False
    try:
        created = datetime.fromisoformat(ts)
        age = datetime.now(timezone.utc) - created
        return age.days >= age_days
    except Exception:
        return False


def should_expire(memory: dict, retention_days: int = 90) -> bool:
    """Check if an episodic memory should be expired."""
    ts = memory.get("timestamp", "")
    if not ts:
        return False
    try:
        created = datetime.fromisoformat(ts)
        age = datetime.now(timezone.utc) - created
        return age.days >= retention_days
    except Exception:
        return False
