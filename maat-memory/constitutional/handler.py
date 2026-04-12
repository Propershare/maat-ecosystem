"""
Constitutional Memory Handler

Identity. Values. Core beliefs. The soul of the agent.

Constitutional memory is:
- Append-only (never silently overwritten)
- Versioned (every change creates a new version)
- Supersedable (new version can replace old, but old is preserved)
- Auditable (full amendment trail)

Constitutional memory is NEVER:
- Silently edited
- Deleted
- Lost in migration
"""

from datetime import datetime, timezone
from typing import Optional
import uuid


def validate_constitutional(memory: dict) -> dict:
    """
    Validate and enforce constitutional memory constraints.
    """
    memory["reversible"] = False
    memory["memory_class"] = "constitutional"
    memory.setdefault("version", 1)
    memory.setdefault("amendments", [])
    memory.setdefault("supersedes", None)

    if not memory.get("content"):
        raise ValueError("Constitutional memory must have content")

    return memory


def amend_constitutional(original: dict, amendment: str, reason: str,
                         amended_by: str = "unknown") -> dict:
    """
    Amend a constitutional memory.

    Does NOT delete or silently overwrite.
    Creates a new version with full audit trail.

    The original is preserved in the amendment history.
    The old version is superseded, not erased.
    """
    new_version = original.get("version", 1) + 1

    amendment_record = {
        "version": new_version,
        "previous_content": original.get("content"),
        "new_content": amendment,
        "reason": reason,
        "amended_by": amended_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    amended = original.copy()
    amendments = list(original.get("amendments", []))
    amendments.append(amendment_record)

    amended["content"] = amendment
    amended["version"] = new_version
    amended["amendments"] = amendments
    amended["last_amended"] = datetime.now(timezone.utc).isoformat()
    amended["last_amended_by"] = amended_by

    return amended


def get_amendment_history(memory: dict) -> list[dict]:
    """
    Get the full amendment history of a constitutional memory.
    Every version, every reason, every author.
    """
    return memory.get("amendments", [])


def supersede_constitutional(old: dict, new_content: str, reason: str,
                             created_by: str = "unknown") -> dict:
    """
    Create a new constitutional memory that supersedes an old one.

    The old memory is NOT deleted. It is marked as superseded.
    The new memory references what it replaced.
    """
    new_memory = {
        "id": str(uuid.uuid4()),
        "agent_id": old.get("agent_id"),
        "memory_class": "constitutional",
        "content": new_content,
        "version": 1,
        "supersedes": old.get("id"),
        "reason": reason,
        "created_by": created_by,
        "amendments": [],
        "reversible": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return new_memory
