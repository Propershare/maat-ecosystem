"""
KA2-aware router — thin wrapper around expert_config.route_message.

Adds three tags to every dispatch decision before the model is called:

- ``research_grade`` — boolean; true when the turn is method-bearing research.
- ``level_of_analysis`` — one of cell / group / institution / system.
- ``research_type``    — one of RESEARCH_TYPES (KA2 ten-step methods).

This keeps keyword routing in ``expert_config.py`` as the starter surface
(Lane 2 per docs/MAAT-EVOLUTION-LANES.md) while letting Sentinel, Bench, and
Forge index on KA2 fields instead of prose. The wrapper never rewrites the
existing router; it decorates its output.

Stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from gateway_contract import (
    LEVELS_OF_ANALYSIS,
    RESEARCH_TYPES,
    make_correlation_id,
    now_iso,
)
import expert_config


# Keyword tables are data, not code. Forge is allowed to propose edits here
# under Lane 2 (router tables & keyword weights).
RESEARCH_GRADE_SIGNALS: tuple[str, ...] = (
    "research",
    "dissertation",
    "literature review",
    "analyze",
    "analyse",
    "analysis",
    "framework",
    "methodology",
    "historical",
    "cite",
    "citation",
    "argue that",
    "thesis",
    "synthesis",
    "contradiction",
    "dialectic",
    "life cycle",
    "trajectory",
    "evolution of",
    "structural cause",
    "why did",
    "what is the history of",
)

CASUAL_SIGNALS: tuple[str, ...] = (
    "hey",
    "thanks",
    "thank you",
    "lol",
    "please",  # weak signal but useful with no research signals
    "can you just",
    "ping",
    "status",
    "how are you",
)

LEVEL_SIGNALS: dict[str, tuple[str, ...]] = {
    "cell": ("individual", "one person", "single actor"),
    "group": ("team", "group", "community", "household", "family", "cohort"),
    "institution": (
        "institution",
        "organization",
        "organisation",
        "company",
        "agency",
        "court",
        "ministry",
        "university",
    ),
    "system": (
        "system",
        "society",
        "civilization",
        "civilisation",
        "state",
        "empire",
        "economy",
        "global",
        "ecosystem",
    ),
}

RESEARCH_TYPE_SIGNALS: dict[str, tuple[str, ...]] = {
    "historical": ("history", "historical", "over time", "through the years", "evolution of"),
    "experimental": ("experiment", "trial", "ablation", "a/b test", "controlled"),
    "theoretical": ("theory", "theoretical", "model of", "framework", "conceptual"),
    "descriptive": ("describe", "profile", "survey of", "overview of"),
    "applied": ("apply", "applied", "deploy", "implement", "operationalize"),
    "comparative": ("compare", "versus", " vs ", "contrast", "relative to"),
    "qualitative": ("interview", "narrative", "testimony", "case study", "ethnograph"),
    "quantitative": ("measure", "quantify", "statistic", "dataset", "sample size", "p-value", "benchmark"),
}


@dataclass
class RouteDecision:
    """Tagged dispatch decision. Fed directly into the gateway runtime."""

    correlation_id: str
    session_id: str
    turn_index: int
    timestamp: str
    message: str
    expert_name: str
    expert_model: str
    expert: dict[str, Any]
    research_grade: bool
    level_of_analysis: str
    research_type: str
    tags: list[str] = field(default_factory=list)
    route_score: int = 0
    signals: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "timestamp": self.timestamp,
            "message": self.message,
            "expert_name": self.expert_name,
            "expert_model": self.expert_model,
            "research_grade": bool(self.research_grade),
            "level_of_analysis": self.level_of_analysis,
            "research_type": self.research_type,
            "tags": list(self.tags),
            "route_score": int(self.route_score),
            "signals": {k: list(v) for k, v in self.signals.items()},
        }


def _hit_words(text: str, vocab: Iterable[str]) -> list[str]:
    lowered = f" {text.lower()} "
    return [w for w in vocab if f" {w} " in lowered or w in text.lower()]


def detect_research_grade(message: str, *, expert_name: str | None = None) -> tuple[bool, list[str]]:
    hits = _hit_words(message, RESEARCH_GRADE_SIGNALS)
    casual_hits = _hit_words(message, CASUAL_SIGNALS)

    if expert_name in {"scout", "analyst", "archivist", "rag-expert"}:
        return True, hits
    if len(hits) >= 1 and len(casual_hits) == 0:
        return True, hits
    if len(hits) >= 2:
        return True, hits
    return False, hits


def detect_level_of_analysis(message: str) -> tuple[str, list[str]]:
    best: tuple[str, int, list[str]] = ("system", 0, [])
    lowered = message.lower()
    for level, vocab in LEVEL_SIGNALS.items():
        hits = [w for w in vocab if w in lowered]
        if len(hits) > best[1]:
            best = (level, len(hits), hits)
    if best[1] == 0:
        return "system", []
    if best[0] not in LEVELS_OF_ANALYSIS:
        return "system", best[2]
    return best[0], best[2]


def detect_research_type(message: str) -> tuple[str, list[str]]:
    lowered = message.lower()
    best: tuple[str, int, list[str]] = ("descriptive", 0, [])
    for rtype, vocab in RESEARCH_TYPE_SIGNALS.items():
        hits = [w for w in vocab if w in lowered]
        if len(hits) > best[1]:
            best = (rtype, len(hits), hits)
    if best[0] not in RESEARCH_TYPES:
        return "descriptive", []
    return best[0], best[2]


def _score_expert(expert: dict[str, Any], message: str) -> int:
    lowered = message.lower()
    score = 0
    for kw in expert.get("keywords", []):
        if kw in lowered:
            score += 1
    return score


def route(
    message: str,
    *,
    session_id: str,
    turn_index: int,
    experts: list[dict[str, Any]] | None = None,
    override_expert: str | None = None,
) -> RouteDecision:
    """Tag a request with KA2 metadata and select an expert.

    ``override_expert`` — force an expert name, bypassing keyword scoring.
    Useful when a gateway preset mandates a specific expert (e.g.
    ``ka2-research`` preset always uses the KA2 research expert).
    """
    pool = experts or expert_config.EXPERTS
    if not pool:
        raise RuntimeError("no experts configured")

    selected: dict[str, Any] | None = None
    score = 0
    if override_expert:
        for e in pool:
            if e["name"] == override_expert:
                selected = e
                score = max(1, _score_expert(e, message))
                break
        if selected is None:
            raise KeyError(f"override_expert not found: {override_expert!r}")
    else:
        best = None
        best_score = 0
        for e in pool:
            s = _score_expert(e, message)
            if s > best_score:
                best = e
                best_score = s
        selected = best or pool[0]
        score = best_score

    research_grade, rg_hits = detect_research_grade(message, expert_name=selected["name"])
    level, level_hits = detect_level_of_analysis(message)
    rtype, rtype_hits = detect_research_type(message)

    tags = [f"expert:{selected['name']}", f"level:{level}", f"research_type:{rtype}"]
    if research_grade:
        tags.append("research_grade:true")
    else:
        tags.append("research_grade:false")
    if override_expert:
        tags.append("route:override")
    if score >= 2:
        tags.append("route:confident")
    elif score == 0 and not override_expert:
        tags.append("route:fallback")

    return RouteDecision(
        correlation_id=make_correlation_id(session_id, turn_index),
        session_id=session_id,
        turn_index=turn_index,
        timestamp=now_iso(),
        message=message,
        expert_name=selected["name"],
        expert_model=selected.get("model", "gemma4:e4b"),
        expert=selected,
        research_grade=research_grade,
        level_of_analysis=level,
        research_type=rtype,
        tags=tags,
        route_score=score,
        signals={
            "research_grade_hits": rg_hits,
            "level_hits": level_hits,
            "research_type_hits": rtype_hits,
        },
    )


__all__ = [
    "RouteDecision",
    "detect_research_grade",
    "detect_level_of_analysis",
    "detect_research_type",
    "route",
    "RESEARCH_GRADE_SIGNALS",
    "CASUAL_SIGNALS",
    "LEVEL_SIGNALS",
    "RESEARCH_TYPE_SIGNALS",
]


if __name__ == "__main__":
    examples = [
        "Hey can you just ping the status of the nginx service?",
        "Archivist: persist this decision as a structured JSON record with tags.",
        "Analyze the history of Kemetic institutions and their life cycle through the dynasties.",
        "Compare Florida trust law cases with New York cases on trustee liability.",
        "What is the structural cause of the disparity across this economy?",
    ]
    for i, msg in enumerate(examples):
        d = route(msg, session_id="demo", turn_index=i)
        print(
            f"[{d.expert_name:<12}] rg={str(d.research_grade):<5} "
            f"level={d.level_of_analysis:<12} type={d.research_type:<12} score={d.route_score}  :: {msg}"
        )
