"""
Semantic Memory Handler

Stable knowledge. Facts. Domain info.
Created by consolidation or explicit write.
"""


def merge_semantics(existing: dict, new_content: str) -> dict:
    """
    Merge new knowledge into existing semantic memory.
    Keeps both if conflicting, marks for human review.
    """
    existing_content = existing.get("content", "")

    if new_content in existing_content:
        return existing  # already known

    merged = existing.copy()
    merged["content"] = f"{existing_content}\n\n[Updated] {new_content}"
    merged["tags"] = list(set(existing.get("tags", []) + ["merged"]))
    return merged
