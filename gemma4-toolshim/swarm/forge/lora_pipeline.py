"""Lane 5 — LoRA pipeline.

Wraps ``gemma4-toolshim/finetune.py`` with the constitutional dataset filter
from docs/MAAT-EVOLUTION-LANES.md Lane 5:

- every row comes from a real captured turn;
- the archivist record for that turn validated;
- the KA2 Maat scorecard passed (``total >= pass_at`` and ``halt_flags < 3``);
- zero RBL flags on that turn;
- the Archivist tag policy approved the row (``tag:archivist:approved``).

We never touch ``finetune.py`` itself — we just build the dataset and
shell out. The actual training process remains out-of-scope for this
module; ``run_finetune`` is a thin ``subprocess`` wrapper and is opt-in.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

_SWARM_DIR = Path(__file__).resolve().parent.parent
if str(_SWARM_DIR) not in sys.path:
    sys.path.insert(0, str(_SWARM_DIR))

from archivist_gitmaat import DEFAULT_STREAM, WORKSPACE_ROOT  # noqa: E402
from gateway_contract import HALT_AT_FLAGS, PASS_AT  # noqa: E402

from .base import Candidate, CandidateKind


APPROVAL_TAGS = ("tag:archivist:approved", "archivist:approved")


@dataclass
class DatasetFilterReport:
    total_seen: int = 0
    research_grade: int = 0
    scorecard_pass: int = 0
    rbl_clean: int = 0
    archivist_approved: int = 0
    kept: int = 0
    dropped_reasons: dict[str, int] = field(default_factory=dict)

    def drop(self, reason: str) -> None:
        self.dropped_reasons[reason] = self.dropped_reasons.get(reason, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_seen": self.total_seen,
            "research_grade": self.research_grade,
            "scorecard_pass": self.scorecard_pass,
            "rbl_clean": self.rbl_clean,
            "archivist_approved": self.archivist_approved,
            "kept": self.kept,
            "dropped_reasons": dict(self.dropped_reasons),
        }


def is_training_eligible(
    record: dict[str, Any], *, require_archivist_approval: bool = True
) -> tuple[bool, str]:
    """Apply the Lane 5 constitutional dataset filter."""
    if not record.get("research_grade"):
        return False, "not_research_grade"

    scorecard = record.get("maat_scorecard") or {}
    if not scorecard:
        return False, "no_scorecard"
    halt_flags = int(scorecard.get("halt_flags", 0))
    total = int(scorecard.get("total", 0))
    if halt_flags >= HALT_AT_FLAGS:
        return False, "halt_flags_over_threshold"
    if total < PASS_AT:
        return False, "scorecard_below_pass_at"

    if record.get("rbl_flags"):
        return False, "rbl_flags_present"
    if record.get("forbidden_hits"):
        return False, "forbidden_hits_present"

    if require_archivist_approval:
        tags = set(record.get("tags") or [])
        if not tags & set(APPROVAL_TAGS):
            return False, "missing_archivist_approval_tag"

    return True, "ok"


def build_dataset(
    *,
    stream_path: Path | str | None = None,
    out_path: Path | str | None = None,
    require_archivist_approval: bool = True,
    max_rows: int | None = None,
) -> tuple[Path, DatasetFilterReport, str]:
    """Scan the archivist JSONL stream, write an eligible-rows dataset.

    Returns ``(dataset_path, report, dataset_hash)``. ``dataset_hash`` is a
    sha256 of the emitted file and becomes the tag on the LoRA candidate.
    """
    stream_path = Path(stream_path) if stream_path else DEFAULT_STREAM
    out_path = Path(out_path) if out_path else (
        WORKSPACE_ROOT / "logs" / "forge" / "training_dataset.jsonl"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report = DatasetFilterReport()
    hasher = hashlib.sha256()

    kept_rows: list[str] = []

    if stream_path.exists():
        with stream_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                report.total_seen += 1
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    report.drop("invalid_json")
                    continue

                if record.get("research_grade"):
                    report.research_grade += 1
                scorecard = record.get("maat_scorecard") or {}
                if scorecard.get("passed"):
                    report.scorecard_pass += 1
                if not record.get("rbl_flags"):
                    report.rbl_clean += 1
                if set(record.get("tags") or []) & set(APPROVAL_TAGS):
                    report.archivist_approved += 1

                ok, reason = is_training_eligible(
                    record, require_archivist_approval=require_archivist_approval
                )
                if not ok:
                    report.drop(reason)
                    continue
                kept_rows.append(json.dumps(_dataset_row(record), ensure_ascii=False))
                if max_rows is not None and len(kept_rows) >= max_rows:
                    break

    for row in kept_rows:
        hasher.update((row + "\n").encode("utf-8"))

    with out_path.open("w", encoding="utf-8") as fh:
        for row in kept_rows:
            fh.write(row + "\n")

    report.kept = len(kept_rows)
    return out_path, report, hasher.hexdigest()


def _dataset_row(record: dict[str, Any]) -> dict[str, Any]:
    """Shape rows so ``finetune.py`` can consume them without ad-hoc parsing."""
    ka2 = record.get("ka2") or {}
    return {
        "correlation_id": record.get("correlation_id"),
        "gateway_id": record.get("gateway_id"),
        "research_type": ka2.get("research_type"),
        "level_of_analysis": ka2.get("level_of_analysis"),
        "summary": record.get("summary"),
        "scorecard_total": (record.get("maat_scorecard") or {}).get("total"),
        "tags": list(record.get("tags") or []),
        "sources": [
            {"kind": s.get("kind"), "ref": s.get("ref")}
            for s in record.get("sources") or []
        ],
    }


@dataclass
class LoRACandidate:
    """Narrow dataclass; use :meth:`to_candidate` for the Promoter cycle."""

    gateway_id: str
    expert_name: str
    base_model: str
    dataset_path: str
    dataset_hash: str
    adapter_out: str
    rationale: str = ""

    def to_candidate(self) -> Candidate:
        diff = {
            "expert_name": self.expert_name,
            "base_model": self.base_model,
            "dataset_path": self.dataset_path,
            "dataset_hash": self.dataset_hash,
            "adapter_out": self.adapter_out,
        }
        return Candidate(
            kind=CandidateKind.LORA_ADAPTER,
            gateway_id=self.gateway_id,
            description=(
                f"lora[{self.expert_name}] base={self.base_model} "
                f"dataset_hash={self.dataset_hash[:12]}: {self.rationale}"
            ),
            diff=diff,
        )


def propose_lora(
    *,
    gateway_id: str,
    expert_name: str,
    base_model: str,
    dataset_path: str | Path,
    dataset_hash: str,
    adapter_out: str | Path,
    rationale: str = "",
) -> Candidate:
    return LoRACandidate(
        gateway_id=gateway_id,
        expert_name=expert_name,
        base_model=base_model,
        dataset_path=str(dataset_path),
        dataset_hash=dataset_hash,
        adapter_out=str(adapter_out),
        rationale=rationale,
    ).to_candidate()


def run_finetune(
    candidate: Candidate,
    *,
    finetune_script: Path | str | None = None,
    dry_run: bool = True,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Opt-in wrapper around ``gemma4-toolshim/finetune.py``.

    Returns a result dict ``{"ok": bool, "cmd": [...], "returncode": int,
    "stdout": str, "stderr": str, "dataset_path": ..., "adapter_out": ...}``.
    With ``dry_run=True`` (default) the command is built and returned but not
    executed — tests and sandboxes use this path.
    """
    if candidate.kind is not CandidateKind.LORA_ADAPTER:
        raise ValueError("not a lora candidate")
    script = Path(finetune_script) if finetune_script else (
        WORKSPACE_ROOT / "gemma4-toolshim" / "finetune.py"
    )
    diff = candidate.diff
    cmd = [
        sys.executable,
        str(script),
        "--dataset",
        diff["dataset_path"],
        "--base-model",
        diff["base_model"],
        "--out",
        diff["adapter_out"],
    ]
    result: dict[str, Any] = {
        "ok": True,
        "cmd": cmd,
        "returncode": 0,
        "stdout": "",
        "stderr": "",
        "dataset_path": diff["dataset_path"],
        "adapter_out": diff["adapter_out"],
        "dry_run": bool(dry_run),
    }
    if dry_run:
        return result
    if not script.exists():
        result["ok"] = False
        result["returncode"] = -1
        result["stderr"] = f"finetune script missing: {script}"
        return result
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, check=False
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[-4000:]
        result["stderr"] = proc.stderr[-4000:]
        result["ok"] = proc.returncode == 0
    except Exception as exc:  # noqa: BLE001
        result["ok"] = False
        result["returncode"] = -1
        result["stderr"] = f"{type(exc).__name__}: {exc}"
    return result


__all__ = [
    "DatasetFilterReport",
    "is_training_eligible",
    "build_dataset",
    "LoRACandidate",
    "propose_lora",
    "run_finetune",
    "APPROVAL_TAGS",
]
