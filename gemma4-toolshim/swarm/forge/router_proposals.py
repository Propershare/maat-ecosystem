"""Lane 2 — Router keyword / vocabulary proposals.

A router proposal touches the data inside
``gemma4-toolshim/swarm/expert_config.py`` (``keywords`` lists for experts)
or the keyword tables inside ``ka2_router.py``
(``RESEARCH_GRADE_SIGNALS`` etc.). No prose changes — just the vocabulary
tables per docs/MAAT-EVOLUTION-LANES.md Lane 2.

Applying a proposal edits an in-memory snapshot so the sandbox gateway can
bench the change without mutating the shipped file. On promotion the
registry (not Forge) is responsible for persisting to disk.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Iterable

from .base import Candidate, CandidateKind


ROUTER_TABLES = (
    "RESEARCH_GRADE_SIGNALS",
    "CASUAL_SIGNALS",
)

LEVEL_DIMENSIONS = ("cell", "group", "institution", "system")


@dataclass
class RouterKeywordProposal:
    gateway_id: str
    expert_name: str | None
    table: str  # "expert_keywords" | "research_grade_signals" | "casual_signals" | "level:<level>" | "research_type:<type>"
    add: list[str] = field(default_factory=list)
    remove: list[str] = field(default_factory=list)
    rationale: str = ""

    def to_candidate(self) -> Candidate:
        diff = {
            "expert_name": self.expert_name,
            "table": self.table,
            "add": [w.strip().lower() for w in self.add],
            "remove": [w.strip().lower() for w in self.remove],
        }
        return Candidate(
            kind=CandidateKind.ROUTER_KEYWORD,
            gateway_id=self.gateway_id,
            description=f"router[{self.table}] +{len(self.add)} -{len(self.remove)}: {self.rationale}",
            diff=diff,
        )


def propose_add_keyword(
    *,
    gateway_id: str,
    expert_name: str | None,
    table: str,
    words: Iterable[str],
    rationale: str = "",
) -> Candidate:
    return RouterKeywordProposal(
        gateway_id=gateway_id,
        expert_name=expert_name,
        table=table,
        add=list(words),
        rationale=rationale,
    ).to_candidate()


def propose_remove_keyword(
    *,
    gateway_id: str,
    expert_name: str | None,
    table: str,
    words: Iterable[str],
    rationale: str = "",
) -> Candidate:
    return RouterKeywordProposal(
        gateway_id=gateway_id,
        expert_name=expert_name,
        table=table,
        remove=list(words),
        rationale=rationale,
    ).to_candidate()


def apply_router(
    candidate: Candidate,
    *,
    experts: list[dict[str, Any]],
    tables: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    """Return (experts_after, tables_after). Callers operate on the copies."""
    if candidate.kind is not CandidateKind.ROUTER_KEYWORD:
        raise ValueError("not a router candidate")

    experts_copy = copy.deepcopy(experts)
    tables_copy = {k: list(v) for k, v in tables.items()}

    diff = candidate.diff
    table = diff["table"]
    add = list(diff.get("add") or [])
    remove = set(diff.get("remove") or [])

    if table == "expert_keywords":
        expert_name = diff.get("expert_name")
        if not expert_name:
            raise ValueError("expert_keywords change requires expert_name")
        target = next((e for e in experts_copy if e["name"] == expert_name), None)
        if target is None:
            raise KeyError(f"expert not found: {expert_name!r}")
        keywords = [k for k in target.get("keywords", []) if k not in remove]
        for kw in add:
            if kw not in keywords:
                keywords.append(kw)
        target["keywords"] = keywords
    elif table in tables_copy:
        current = [k for k in tables_copy[table] if k not in remove]
        for kw in add:
            if kw not in current:
                current.append(kw)
        tables_copy[table] = current
    else:
        raise KeyError(f"unknown router table: {table!r}")

    return experts_copy, tables_copy


__all__ = [
    "RouterKeywordProposal",
    "propose_add_keyword",
    "propose_remove_keyword",
    "apply_router",
    "ROUTER_TABLES",
]
