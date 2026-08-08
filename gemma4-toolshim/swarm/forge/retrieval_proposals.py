"""Lane 1 — Retrieval pack proposals.

A retrieval pack is a folder under ``data/retrieval_packs/<pack_id>/`` with a
``manifest.yaml`` describing provenance, gateways, and version. A proposal is
one of: ``add``, ``retire``, ``rerank``, ``version_bump``.

Applying a proposal writes a staged manifest under
``.forge_staged/retrieval_packs/<pack_id>/manifest.staged.yaml`` and, on
promotion, atomically moves it into the canonical manifest. Revert deletes
the staged file.

Stdlib only; YAML is emitted as a simple ``key: value`` dialect since the
manifest schema is flat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import Candidate, CandidateKind


def _find_lab_root() -> Path:
    here = Path(__file__).resolve()
    for p in (here, *here.parents):
        if (p / "maat-ecosystem").is_dir() and (p / "gemma4-toolshim").is_dir():
            return p
    return Path.cwd()


LAB_ROOT = _find_lab_root()
PACKS_ROOT = LAB_ROOT / "data" / "retrieval_packs"
STAGING_ROOT = LAB_ROOT / ".forge_staged" / "retrieval_packs"


def _emit_flat_yaml(data: dict[str, Any]) -> str:
    """Flat ``key: value`` YAML. Good enough for the manifest shape."""
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines) + "\n"


@dataclass
class RetrievalPackProposal:
    """Narrow dataclass convertible to :class:`Candidate`."""

    gateway_id: str
    pack_id: str
    operation: str  # "add" | "retire" | "rerank" | "version_bump"
    manifest: dict[str, Any] | None = None
    rationale: str = ""

    def to_candidate(self) -> Candidate:
        if self.operation not in {"add", "retire", "rerank", "version_bump"}:
            raise ValueError(f"unknown operation: {self.operation}")
        diff = {
            "pack_id": self.pack_id,
            "operation": self.operation,
            "manifest": self.manifest or {},
        }
        return Candidate(
            kind=CandidateKind.RETRIEVAL_PACK,
            gateway_id=self.gateway_id,
            description=f"retrieval[{self.operation}] {self.pack_id}: {self.rationale}",
            diff=diff,
        )


def propose_retrieval_pack(
    *,
    gateway_id: str,
    pack_id: str,
    operation: str,
    manifest: dict[str, Any] | None = None,
    rationale: str = "",
) -> Candidate:
    return RetrievalPackProposal(
        gateway_id=gateway_id,
        pack_id=pack_id,
        operation=operation,
        manifest=manifest,
        rationale=rationale,
    ).to_candidate()


def _staged_path(pack_id: str) -> Path:
    p = STAGING_ROOT / pack_id
    p.mkdir(parents=True, exist_ok=True)
    return p / "manifest.staged.yaml"


def _canonical_path(pack_id: str) -> Path:
    p = PACKS_ROOT / pack_id
    p.mkdir(parents=True, exist_ok=True)
    return p / "manifest.yaml"


def apply_retrieval(candidate: Candidate) -> None:
    """Stage the manifest. Promoter moves it on bench+guard success."""
    if candidate.kind is not CandidateKind.RETRIEVAL_PACK:
        raise ValueError("not a retrieval candidate")
    diff = candidate.diff
    pack_id = diff["pack_id"]
    staged = _staged_path(pack_id)
    if diff["operation"] == "retire":
        staged.write_text(_emit_flat_yaml({"pack_id": pack_id, "retired": "true"}))
        return
    manifest = dict(diff.get("manifest") or {})
    manifest.setdefault("pack_id", pack_id)
    manifest.setdefault("operation", diff["operation"])
    manifest.setdefault("candidate_id", candidate.id)
    staged.write_text(_emit_flat_yaml(manifest))


def revert_retrieval(candidate: Candidate) -> None:
    if candidate.kind is not CandidateKind.RETRIEVAL_PACK:
        return
    staged = _staged_path(candidate.diff["pack_id"])
    if staged.exists():
        staged.unlink()


def promote_retrieval(candidate: Candidate) -> Path:
    """Move staged manifest to canonical. Called by the registry, not Forge."""
    if candidate.kind is not CandidateKind.RETRIEVAL_PACK:
        raise ValueError("not a retrieval candidate")
    pack_id = candidate.diff["pack_id"]
    staged = _staged_path(pack_id)
    if not staged.exists():
        raise FileNotFoundError(f"no staged manifest for {pack_id}")
    canonical = _canonical_path(pack_id)
    canonical.write_text(staged.read_text())
    staged.unlink()
    return canonical


__all__ = [
    "RetrievalPackProposal",
    "propose_retrieval_pack",
    "apply_retrieval",
    "revert_retrieval",
    "promote_retrieval",
    "PACKS_ROOT",
    "STAGING_ROOT",
]
