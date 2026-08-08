"""
Gateway output contract — maat.archivist_record.v1 + KA2 Maat scorecard.

Every expert gateway MUST emit an ArchivistRecord per turn. Sentinel, Bench,
Forge, and Guard read the structured fields; prose is confined to `summary`
and `notes`. Scorecard threshold (pass_at=40) and RBL halt rule (halt_flags>=3)
live here in code, not in prompt text, per docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md.

Sacred vs replaceable:
  sacred       = scorecard pass threshold, scorecard axes, RBL halt rule,
                 schema constants, forbidden-action vocabulary.
  replaceable  = weight of individual keyword heuristics, retrieval packs,
                 router vocabulary, gateway list, prompt envelopes.

This module is stdlib-only so the shim imports cleanly.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_RECORD = "maat.archivist_record.v1"
SCHEMA_SCORECARD = "maat.ka2_scorecard.v1"

PASS_AT = 40
HALT_AT_FLAGS = 3
SCORECARD_AXES = ("truth", "order", "balance", "justice", "self_reflection")

RESEARCH_TYPES = (
    "historical",
    "experimental",
    "theoretical",
    "descriptive",
    "applied",
    "comparative",
    "qualitative",
    "quantitative",
)

LEVELS_OF_ANALYSIS = ("cell", "group", "institution", "system")

# Forbidden vocabulary and motion-required signals live in code so prompt
# tweaks cannot silently erase them. Mirrors ka2_agent_system_prompt.md.
AI_TELL_VOCAB = frozenset({"delve", "tapestry", "vibrant"})

MOTION_REQUIRED_TRIGGERS = frozenset(
    {"history of", "trajectory of", "evolution of", "life cycle of"}
)

RBL_INDICATORS = (
    "individualism_over_systemic",
    "static_over_motion",
    "cultural_bias_as_universal",
    "omission_of_african_agency",
    "linear_progress_no_contradictions",
    "technical_jargon_masking_truth",
    "depoliticized_objectivity",
    "symptoms_over_structural_causes",
)

FORBIDDEN_HITS = (
    "ai_tell_vocabulary",
    "static_snapshot_required_motion",
    "omitted_contradictions",
    "eurocentric_source_not_validated",
    "missing_maat_scorecard",
    "missing_method_naming",
)


def now_iso() -> str:
    """UTC ISO 8601 timestamp with seconds precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def make_correlation_id(session_id: str, turn_index: int) -> str:
    """Bind a record to a replayable turn: ``{session_id}:{turn_index:04d}``."""
    if not session_id:
        raise ValueError("session_id is required")
    if turn_index < 0:
        raise ValueError("turn_index must be >= 0")
    return f"{session_id}:{turn_index:04d}"


def parse_correlation_id(correlation_id: str) -> tuple[str, int]:
    """Inverse of :func:`make_correlation_id`."""
    if ":" not in correlation_id:
        raise ValueError(f"malformed correlation_id: {correlation_id!r}")
    session_id, turn_str = correlation_id.rsplit(":", 1)
    return session_id, int(turn_str)


@dataclass
class MaatScorecard:
    """Constitutional scorecard. `passed` is derived, not trusted from the model."""

    scores: dict[str, int]
    halt_flags: int = 0
    correction_notes: str | None = None

    @property
    def total(self) -> int:
        return sum(int(self.scores.get(axis, 0)) for axis in SCORECARD_AXES)

    @property
    def passed(self) -> bool:
        return self.total >= PASS_AT and self.halt_flags < HALT_AT_FLAGS

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema": SCHEMA_SCORECARD,
            "scores": {axis: int(self.scores.get(axis, 0)) for axis in SCORECARD_AXES},
            "total": self.total,
            "pass_at": PASS_AT,
            "passed": self.passed,
            "halt_flags": int(self.halt_flags),
        }
        if self.correction_notes:
            out["correction_notes"] = self.correction_notes
        return out


@dataclass
class Source:
    kind: str
    ref: str
    line_start: int | None = None
    line_end: int | None = None
    retrieved_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"kind": self.kind, "ref": self.ref}
        if self.line_start is not None:
            d["line_start"] = int(self.line_start)
        if self.line_end is not None:
            d["line_end"] = int(self.line_end)
        if self.retrieved_at:
            d["retrieved_at"] = self.retrieved_at
        return d


@dataclass
class ArchivistRecord:
    """Structured-first persistence envelope."""

    correlation_id: str
    agent_id: str
    gateway_id: str
    summary: str
    sources: list[Source] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    research_grade: bool = False
    ka2: dict[str, Any] | None = None
    maat_scorecard: MaatScorecard | None = None
    rbl_flags: list[str] = field(default_factory=list)
    forbidden_hits: list[str] = field(default_factory=list)
    gateway_state: dict[str, Any] | None = None
    related_events: list[str] = field(default_factory=list)
    notes: str | None = None
    payload: dict[str, Any] | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schema": SCHEMA_RECORD,
            "record_id": self.record_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "agent_id": self.agent_id,
            "gateway_id": self.gateway_id,
            "research_grade": bool(self.research_grade),
            "tags": list(self.tags),
            "summary": self.summary,
            "sources": [s.to_dict() for s in self.sources],
            "rbl_flags": list(self.rbl_flags),
            "forbidden_hits": list(self.forbidden_hits),
            "related_events": list(self.related_events),
        }
        if self.ka2 is not None:
            d["ka2"] = dict(self.ka2)
        if self.maat_scorecard is not None:
            d["maat_scorecard"] = self.maat_scorecard.to_dict()
        if self.gateway_state is not None:
            d["gateway_state"] = dict(self.gateway_state)
        if self.notes:
            d["notes"] = self.notes
        if self.payload is not None:
            d["payload"] = dict(self.payload)
        return d

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)


class ContractError(ValueError):
    """Raised when a record violates the sacred parts of the contract."""


def validate_record(record: dict[str, Any] | ArchivistRecord) -> list[str]:
    """Return a list of contract violations. Empty list = valid.

    Only hard constraints are enforced here — schema-level JSON Schema checks
    belong to maatbench. This keeps the runtime validator cheap and
    dependency-free.
    """
    if isinstance(record, ArchivistRecord):
        record = record.to_dict()

    errors: list[str] = []

    if record.get("schema") != SCHEMA_RECORD:
        errors.append(f"schema must be {SCHEMA_RECORD!r}")
    for required in (
        "record_id",
        "correlation_id",
        "created_at",
        "agent_id",
        "gateway_id",
        "summary",
        "sources",
    ):
        if not record.get(required):
            errors.append(f"missing required field: {required}")

    if not isinstance(record.get("tags", []), list):
        errors.append("tags must be a list")

    sources = record.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be a list")
    else:
        for i, src in enumerate(sources):
            if not isinstance(src, dict):
                errors.append(f"sources[{i}] must be an object")
                continue
            if src.get("kind") not in {
                "file",
                "url",
                "gitmaat",
                "tool_result",
                "memory",
                "corpus",
            }:
                errors.append(f"sources[{i}].kind invalid: {src.get('kind')!r}")
            if not src.get("ref"):
                errors.append(f"sources[{i}].ref missing")

    research_grade = bool(record.get("research_grade"))
    ka2 = record.get("ka2")
    scorecard = record.get("maat_scorecard")

    if research_grade:
        if not ka2:
            errors.append("research_grade=true requires ka2 header")
        else:
            rt = ka2.get("research_type")
            if rt and rt not in RESEARCH_TYPES:
                errors.append(f"ka2.research_type invalid: {rt!r}")
            level = ka2.get("level_of_analysis")
            if level and level not in LEVELS_OF_ANALYSIS:
                errors.append(f"ka2.level_of_analysis invalid: {level!r}")
            if not ka2.get("problem"):
                errors.append("ka2.problem required")
            if not ka2.get("time_dimension"):
                errors.append("ka2.time_dimension required")
        if not scorecard:
            errors.append("research_grade=true requires maat_scorecard")

    if scorecard:
        if scorecard.get("schema") != SCHEMA_SCORECARD:
            errors.append(f"maat_scorecard.schema must be {SCHEMA_SCORECARD!r}")
        if scorecard.get("pass_at") != PASS_AT:
            errors.append(
                f"maat_scorecard.pass_at is sacred and must equal {PASS_AT}"
            )
        axes = scorecard.get("scores", {}) or {}
        for axis in SCORECARD_AXES:
            v = axes.get(axis)
            if not isinstance(v, int) or not 0 <= v <= 10:
                errors.append(f"maat_scorecard.scores.{axis} must be int in [0,10]")
        total_reported = scorecard.get("total")
        total_computed = sum(int(axes.get(a, 0)) for a in SCORECARD_AXES)
        if total_reported != total_computed:
            errors.append(
                f"maat_scorecard.total mismatch: reported {total_reported} "
                f"vs computed {total_computed}"
            )
        halt_flags = int(scorecard.get("halt_flags", 0))
        passed_reported = bool(scorecard.get("passed"))
        passed_truth = total_computed >= PASS_AT and halt_flags < HALT_AT_FLAGS
        if passed_reported != passed_truth:
            errors.append(
                f"maat_scorecard.passed mismatch: reported {passed_reported} "
                f"vs truth {passed_truth}"
            )
        if not passed_truth and not scorecard.get("correction_notes"):
            errors.append(
                "maat_scorecard.correction_notes required when passed=false"
            )

    for hit in record.get("forbidden_hits", []) or []:
        if hit not in FORBIDDEN_HITS:
            errors.append(f"unknown forbidden_hit: {hit!r}")
    for flag in record.get("rbl_flags", []) or []:
        if flag not in RBL_INDICATORS:
            errors.append(f"unknown rbl_flag: {flag!r}")

    return errors


def detect_forbidden_hits(
    text: str, *, research_grade: bool, ka2: dict[str, Any] | None
) -> list[str]:
    """Cheap validator — reads structured fields; never asks the model to self-grade."""
    hits: list[str] = []
    lowered = (text or "").lower()

    if any(w in lowered for w in AI_TELL_VOCAB):
        hits.append("ai_tell_vocabulary")

    if research_grade:
        if not ka2 or not ka2.get("research_type"):
            hits.append("missing_method_naming")

        if any(trigger in lowered for trigger in MOTION_REQUIRED_TRIGGERS):
            life = (ka2 or {}).get("life_cycle", {}) or {}
            has_motion = any(life.get(k) for k in ("periods", "phases", "transitions"))
            if not has_motion:
                hits.append("static_snapshot_required_motion")

        contradictions = ((ka2 or {}).get("life_cycle", {}) or {}).get("contradictions")
        findings = (ka2 or {}).get("dialectical_findings", {}) or {}
        if not contradictions and not findings.get("contradiction"):
            hits.append("omitted_contradictions")

    return sorted(set(hits))


_RBL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("individualism_over_systemic", re.compile(r"\b(?:personal choice|individual responsibility)\b", re.I)),
    ("static_over_motion", re.compile(r"\b(?:has always been|timeless|unchanging)\b", re.I)),
    ("cultural_bias_as_universal", re.compile(r"\b(?:universal (?:values|truth)|human nature dictates)\b", re.I)),
    ("linear_progress_no_contradictions", re.compile(r"\bprogress(?:ed)? steadily\b", re.I)),
    ("technical_jargon_masking_truth", re.compile(r"\b(?:leverage synerg|paradigm shift|stakeholder ecosystem)\b", re.I)),
    ("depoliticized_objectivity", re.compile(r"\bpurely (?:objective|neutral) (?:stance|view)\b", re.I)),
    ("symptoms_over_structural_causes", re.compile(r"\b(?:bad apples|isolated incident)\b", re.I)),
)


def detect_rbl_flags(text: str) -> list[str]:
    """Surface RBL indicators in the emitted text. Tight patterns; false-positive shy."""
    lowered = text or ""
    hits: list[str] = []
    for name, pattern in _RBL_PATTERNS:
        if pattern.search(lowered):
            hits.append(name)
    return sorted(set(hits))


def build_record(
    *,
    correlation_id: str,
    agent_id: str,
    gateway_id: str,
    summary: str,
    sources: Iterable[Source | dict[str, Any]] = (),
    tags: Iterable[str] = (),
    research_grade: bool = False,
    ka2: dict[str, Any] | None = None,
    scorecard: MaatScorecard | None = None,
    gateway_state: dict[str, Any] | None = None,
    related_events: Iterable[str] = (),
    notes: str | None = None,
    payload: dict[str, Any] | None = None,
    content_text: str = "",
) -> ArchivistRecord:
    """Build a record and run detectors. Caller still invokes ``validate_record``."""
    src_objs: list[Source] = []
    for s in sources:
        src_objs.append(s if isinstance(s, Source) else Source(**s))

    rbl_flags = detect_rbl_flags(content_text) if content_text else []
    forbidden_hits = detect_forbidden_hits(
        content_text, research_grade=research_grade, ka2=ka2
    )

    record = ArchivistRecord(
        correlation_id=correlation_id,
        agent_id=agent_id,
        gateway_id=gateway_id,
        summary=summary,
        sources=src_objs,
        tags=list(tags),
        research_grade=research_grade,
        ka2=ka2,
        maat_scorecard=scorecard,
        rbl_flags=rbl_flags,
        forbidden_hits=forbidden_hits,
        gateway_state=gateway_state,
        related_events=list(related_events),
        notes=notes,
        payload=payload,
    )
    return record


def load_example_record() -> dict[str, Any]:
    """Load the shipped example record from skeleton/schemas/examples/."""
    here = Path(__file__).resolve()
    candidate = (
        here.parent.parent.parent
        / "maat-ecosystem"
        / "skeleton"
        / "schemas"
        / "examples"
        / "archivist_record.example.json"
    )
    return json.loads(candidate.read_text())


__all__ = [
    "SCHEMA_RECORD",
    "SCHEMA_SCORECARD",
    "PASS_AT",
    "HALT_AT_FLAGS",
    "SCORECARD_AXES",
    "RESEARCH_TYPES",
    "LEVELS_OF_ANALYSIS",
    "RBL_INDICATORS",
    "FORBIDDEN_HITS",
    "AI_TELL_VOCAB",
    "MaatScorecard",
    "Source",
    "ArchivistRecord",
    "ContractError",
    "now_iso",
    "make_correlation_id",
    "parse_correlation_id",
    "validate_record",
    "detect_forbidden_hits",
    "detect_rbl_flags",
    "build_record",
    "load_example_record",
]
