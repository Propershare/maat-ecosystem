"""
🧠 Expert Router — Picks the right expert for each message

Takes a user message, scores it against each expert's keywords
and description, returns the best match. Falls back to rag-expert.

Usage:
    from router import route_message
    expert = route_message("search the knowledge base for auth decisions")
    print(expert["name"])  # → "rag-expert"
"""

from typing import Dict, Any, Optional
from expert_config import EXPERTS, SETTINGS


def score_message(message: str, expert: Dict[str, Any]) -> float:
    """
    Score how well a message matches an expert.

    Keyword hit = 3 points each.
    Description word overlap = 1 point each.

    Args:
        message: The user's message (will be lowercased).
        expert: An expert config dict from expert_config.py.

    Returns:
        A float score. Higher = better match.
    """
    score = 0.0
    message_lower = message.lower()

    # Keyword matching (high weight — these are curated trigger words)
    for keyword in expert.get("keywords", []):
        if keyword.lower() in message_lower:
            score += 3.0

    # Description word overlap (lower weight — broader matching)
    desc_words = expert.get("description", "").lower().split()
    for word in desc_words:
        if len(word) > 3 and word in message_lower:
            score += 1.0

    return score


def route_message(message: str, experts: list = None, debug: bool = False) -> Dict[str, Any]:
    """
    Pick the best expert for a user message.

    Scores the message against all experts and returns the highest.
    If no expert scores above the confidence threshold, falls back
    to rag-expert (or the first expert if rag-expert doesn't exist).

    Args:
        message: What the user said.
        experts: List of expert configs (uses EXPERTS from config if None).
        debug: Print scoring details.

    Returns:
        The best matching expert config dict.
    """
    if experts is None:
        experts = EXPERTS

    if not experts:
        raise ValueError("No experts configured! Check expert_config.py")

    threshold = SETTINGS.get("routing_confidence_threshold", 20)
    best_score = -1.0
    best_expert = None

    for expert in experts:
        score = score_message(message, expert)
        if debug:
            print(f"  [{expert['name']}] score={score:.1f}")

        if score > best_score:
            best_score = score
            best_expert = expert

    # Fallback: if score is too low, use rag-expert (knowledge lookup is safest default)
    if best_score < threshold:
        fallback = next((e for e in experts if e["name"] == "rag-expert"), experts[0])
        if debug:
            print(f"  → Low confidence ({best_score:.1f} < {threshold}). Falling back to {fallback['name']}")
        return fallback

    if debug:
        print(f"  → Routed to {best_expert['name']} (score={best_score:.1f})")

    return best_expert


def route_with_context(message: str, memory_context: str = "", debug: bool = False) -> Dict[str, Any]:
    """
    Route with optional memory context for better accuracy.

    Combines the user message with any retrieved memory context
    before scoring, so experts match on richer information.

    Args:
        message: The user's message.
        memory_context: Optional context from gitMaat query.
        debug: Print scoring details.

    Returns:
        The best matching expert config dict.
    """
    combined = f"{message} {memory_context}" if memory_context else message
    return route_message(combined, debug=debug)


# ─── Quick Test ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧠 Router Test\n")

    test_messages = [
        "What did we decide about the API last week?",
        "Create a Python script that sorts numbers",
        "Check how much disk space we have",
        "Fix the bug in the login function",
        "Restart the nginx service",
        "Search for all files about Maat",
        "Hello, how are you?",
    ]

    for msg in test_messages:
        expert = route_message(msg, debug=False)
        print(f"  [{expert['name']:15}] ← {msg}")
