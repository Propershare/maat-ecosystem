"""
Maat Provenance (T1) — content origin + nonce-delimited quarantine.

Law: Absence is not compliance.
The frame is the control; pattern detection is only a tripwire.
No DEFAULT trust — writers must state provenance.
Legacy rows are legacy_unclassified (quarantined), never backfilled as agent_authored.
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class ProvenanceError(ValueError):
    """Refuse to guess when origin is missing or unknown."""


class ScopeViolation(ValueError):
    """Unscoped write attempted — absence is not compliance."""


class ContentOrigin(str, Enum):
    AGENT_AUTHORED = "agent_authored"
    HUMAN_AUTHORED = "human_authored"
    SYSTEM_GENERATED = "system_generated"
    EXTERNAL_UNTRUSTED = "external_untrusted"
    DERIVED_UNTRUSTED = "derived_untrusted"
    LEGACY_UNCLASSIFIED = "legacy_unclassified"


TRUSTED_ORIGINS = frozenset(
    {
        ContentOrigin.AGENT_AUTHORED,
        ContentOrigin.HUMAN_AUTHORED,
        ContentOrigin.SYSTEM_GENERATED,
    }
)

QUARANTINED_ORIGINS = frozenset(
    {
        ContentOrigin.EXTERNAL_UNTRUSTED,
        ContentOrigin.DERIVED_UNTRUSTED,
        ContentOrigin.LEGACY_UNCLASSIFIED,
    }
)

VALID_ORIGIN_VALUES = frozenset(o.value for o in ContentOrigin)


def parse_origin(value: str | ContentOrigin | None) -> ContentOrigin:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ProvenanceError("content_origin required — absence is not compliance")
    if isinstance(value, ContentOrigin):
        return value
    v = value.strip()
    if v not in VALID_ORIGIN_VALUES:
        raise ProvenanceError(f"unknown content_origin {value!r} — refusing to guess")
    return ContentOrigin(v)


def derive_origin(*, source: str | None, claimed: str | ContentOrigin | None = None) -> ContentOrigin:
    """Fail-closed origin derivation for writers.

    absent / unknown source -> derived_untrusted (never agent_authored).
    Explicit claimed origin must still be a known enum value.
    """
    if claimed is not None:
        return parse_origin(claimed)
    if source is None or not str(source).strip():
        return ContentOrigin.DERIVED_UNTRUSTED
    s = str(source).strip().lower()
    if s in {"absent", "unknown", "none", "null"}:
        return ContentOrigin.DERIVED_UNTRUSTED
    if s in {"agent", "agent_authored"}:
        return ContentOrigin.AGENT_AUTHORED
    if s in {"human", "human_authored"}:
        return ContentOrigin.HUMAN_AUTHORED
    if s in {"system", "system_generated"}:
        return ContentOrigin.SYSTEM_GENERATED
    if s in {"external", "external_untrusted", "web", "user_paste"}:
        return ContentOrigin.EXTERNAL_UNTRUSTED
    # Unknown label — do not promote
    return ContentOrigin.DERIVED_UNTRUSTED


def is_trusted(origin: str | ContentOrigin | None) -> bool:
    try:
        o = parse_origin(origin)
    except ProvenanceError:
        return False
    return o in TRUSTED_ORIGINS


def requires_quarantine(origin: str | ContentOrigin | None) -> bool:
    try:
        o = parse_origin(origin)
    except ProvenanceError:
        return True  # fail-closed: unknown → quarantine
    return o in QUARANTINED_ORIGINS


def _nonce() -> str:
    return secrets.token_hex(16)  # 128-bit


@dataclass(frozen=True)
class QuarantineFrame:
    nonce: str
    opener: str
    closer: str

    @classmethod
    def mint(cls) -> "QuarantineFrame":
        n = _nonce()
        return cls(
            nonce=n,
            opener=f"<<<MAAT_UNTRUSTED_BEGIN_{n}>>>",
            closer=f"<<<MAAT_UNTRUSTED_END_{n}>>>",
        )


def quarantine(text: str, *, frame: QuarantineFrame | None = None) -> str:
    """Wrap untrusted text so it cannot close its own frame (must guess 128-bit nonce)."""
    fr = frame or QuarantineFrame.mint()
    body = "" if text is None else str(text)
    # Neutralize accidental closer collisions by escaping the exact closer token if present
    # (still cannot forge the *real* closer without the nonce).
    safe = body.replace(fr.closer, fr.closer.replace("END", "END_ESCAPED"))
    return f"{fr.opener}\n{safe}\n{fr.closer}"


def render_memory_context(
    rows: Sequence[Mapping[str, Any]],
    *,
    text_keys: Sequence[str] = ("insight", "decision_made", "description", "summary", "content", "text"),
    origin_key: str = "content_origin",
) -> str:
    """Session bootstrap render: trusted plain, untrusted/legacy quarantined.

    Rows without content_origin are treated as legacy_unclassified (quarantined).
    """
    parts: list[str] = []
    for i, row in enumerate(rows):
        origin_raw = row.get(origin_key)
        if origin_raw is None or origin_raw == "":
            origin = ContentOrigin.LEGACY_UNCLASSIFIED
        else:
            try:
                origin = parse_origin(origin_raw)
            except ProvenanceError:
                origin = ContentOrigin.DERIVED_UNTRUSTED

        text = ""
        for k in text_keys:
            if row.get(k):
                text = str(row.get(k))
                break
        if not text:
            text = str(row.get("id") or f"row-{i}")

        header = f"[{origin.value}]"
        if requires_quarantine(origin):
            parts.append(f"{header}\n{quarantine(text)}")
        else:
            parts.append(f"{header}\n{text}")
    return "\n\n".join(parts)


def require_scoped_write(*, task_id: str | None, agent: str | None) -> None:
    if not agent or not str(agent).strip():
        raise ScopeViolation("agent required for write — absence is not compliance")
    if task_id is not None and not str(task_id).strip():
        raise ScopeViolation("empty task_id is not a scope — absence is not compliance")


def verify_legacy_debt(rows: Iterable[Mapping[str, Any]], *, origin_key: str = "content_origin") -> int:
    """Count legacy_unclassified / missing origin rows (debt until zero)."""
    n = 0
    for row in rows:
        o = row.get(origin_key)
        if o is None or o == "" or o == ContentOrigin.LEGACY_UNCLASSIFIED.value:
            n += 1
    return n


__all__ = [
    "ContentOrigin",
    "ProvenanceError",
    "ScopeViolation",
    "TRUSTED_ORIGINS",
    "QUARANTINED_ORIGINS",
    "parse_origin",
    "derive_origin",
    "is_trusted",
    "requires_quarantine",
    "QuarantineFrame",
    "quarantine",
    "render_memory_context",
    "require_scoped_write",
    "verify_legacy_debt",
]
