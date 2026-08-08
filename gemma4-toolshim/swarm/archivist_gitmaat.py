"""
Archivist → gitMaat persistence adapter.

Every expert turn produces one ArchivistRecord. This module writes it to:

1. An append-only JSONL stream at ``<workspace>/logs/archivist/records.jsonl``
   (always on; survives db outages; read by Sentinel).
2. gitMaat (``log_gitmaat_change`` + ``log_gitmaat_decision`` for research-grade,
   plus ``log_gitmaat_learning`` on scorecard fails) when Postgres is reachable.

If gitMaat is NOT_CONNECTED the adapter logs that fact and keeps writing the
JSONL stream — record-first behaviour per the operator doctrine in AGENTS.md
("If memory is unreachable, the agent states that plainly").

Stdlib only for the JSONL path. gitMaat import is lazy and tolerant.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gateway_contract import (
    ArchivistRecord,
    SCHEMA_RECORD,
    validate_record,
)


def _find_workspace_root() -> Path:
    here = Path(__file__).resolve()
    for p in (here, *here.parents):
        if (p / "maatlangchain").is_dir():
            return p
    return Path.cwd()


WORKSPACE_ROOT = _find_workspace_root()
DEFAULT_STREAM = WORKSPACE_ROOT / "logs" / "archivist" / "records.jsonl"


@dataclass
class PersistResult:
    record_id: str
    correlation_id: str
    jsonl_path: str
    gitmaat_status: str  # "ok" | "not_connected" | "failed"
    gitmaat_ids: dict[str, str]
    contract_errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.contract_errors and (
            self.gitmaat_status == "ok"
            or self.gitmaat_status.startswith("not_connected")
            or self.gitmaat_status == "disabled"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "correlation_id": self.correlation_id,
            "jsonl_path": self.jsonl_path,
            "gitmaat_status": self.gitmaat_status,
            "gitmaat_ids": dict(self.gitmaat_ids),
            "contract_errors": list(self.contract_errors),
            "ok": self.ok,
        }


class ArchivistGitMaatAdapter:
    """Thread-safe writer for archivist records."""

    def __init__(
        self,
        *,
        stream_path: Path | str | None = None,
        agent_id: str | None = None,
        enable_gitmaat: bool = True,
    ) -> None:
        self.stream_path = Path(stream_path) if stream_path else DEFAULT_STREAM
        self.stream_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._agent_id = agent_id
        self._enable_gitmaat = enable_gitmaat
        self._memory = None
        self._memory_probed = False
        self._memory_status: str = "unprobed"

    def _probe_memory(self) -> None:
        if self._memory_probed:
            return
        self._memory_probed = True
        if not self._enable_gitmaat:
            self._memory_status = "disabled"
            return
        try:
            import sys

            sys.path.insert(0, str(WORKSPACE_ROOT / "maatlangchain"))
            from maat_memory import MaatMemory, get_unique_agent_id

            if self._agent_id is None:
                self._agent_id = get_unique_agent_id("gateway")
            self._memory = MaatMemory()
            self._memory_status = "ok"
        except Exception as exc:  # noqa: BLE001 - surface a reason
            self._memory = None
            self._memory_status = f"not_connected:{type(exc).__name__}"

    @property
    def agent_id(self) -> str:
        if self._agent_id is None:
            self._probe_memory()
            if self._agent_id is None:
                self._agent_id = f"gateway_{os.uname().nodename}"
        return self._agent_id

    def persist(self, record: ArchivistRecord | dict[str, Any]) -> PersistResult:
        """Validate, append to JSONL, best-effort write to gitMaat."""
        record_dict = record.to_dict() if isinstance(record, ArchivistRecord) else dict(record)
        errors = validate_record(record_dict)

        with self._lock:
            with self.stream_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record_dict, ensure_ascii=False) + "\n")
                fh.flush()

        gitmaat_ids: dict[str, str] = {}
        if errors:
            gm_status = "skipped:contract_errors"
        elif not self._enable_gitmaat:
            gm_status = "disabled"
        else:
            self._probe_memory()
            if self._memory is not None:
                try:
                    gitmaat_ids = self._write_gitmaat(record_dict)
                    gm_status = "ok"
                except Exception as exc:  # noqa: BLE001
                    gm_status = f"failed:{type(exc).__name__}"
            else:
                gm_status = self._memory_status or "not_connected"

        return PersistResult(
            record_id=record_dict.get("record_id", ""),
            correlation_id=record_dict.get("correlation_id", ""),
            jsonl_path=str(self.stream_path),
            gitmaat_status=gm_status,
            gitmaat_ids=gitmaat_ids,
            contract_errors=errors,
        )

    def _write_gitmaat(self, record_dict: dict[str, Any]) -> dict[str, str]:
        mem = self._memory
        assert mem is not None
        agent = self.agent_id
        correlation_id = record_dict["correlation_id"]
        gateway_id = record_dict["gateway_id"]
        summary = record_dict.get("summary", "")

        out: dict[str, str] = {}

        change_file = (
            f"archivist-records/{correlation_id}.json"
            if "/" not in correlation_id
            else f"archivist-records/{correlation_id.replace(':', '_')}.json"
        )
        out["change_id"] = mem.log_change(
            agent=agent,
            file_path=change_file,
            change_type="archive",
            summary=summary[:500],
            reason=f"gateway={gateway_id} correlation_id={correlation_id}",
            diff_preview=json.dumps(
                {
                    "record_id": record_dict.get("record_id"),
                    "tags": record_dict.get("tags", []),
                    "sources": [
                        {"kind": s.get("kind"), "ref": s.get("ref")}
                        for s in record_dict.get("sources", [])
                    ],
                    "research_grade": record_dict.get("research_grade"),
                    "scorecard_total": (record_dict.get("maat_scorecard") or {}).get("total"),
                    "rbl_flags": record_dict.get("rbl_flags", []),
                    "forbidden_hits": record_dict.get("forbidden_hits", []),
                },
                ensure_ascii=False,
            )[:4000],
        )

        if record_dict.get("research_grade"):
            ka2 = record_dict.get("ka2") or {}
            decision = f"KA2 record persisted ({ka2.get('research_type', 'n/a')})"
            out["decision_id"] = mem.log_decision(
                agent=agent,
                context=f"gateway={gateway_id} correlation_id={correlation_id}",
                decision_made=decision,
                rationale=summary[:2000],
                options_considered=[
                    f"research_type:{ka2.get('research_type', 'n/a')}",
                    f"level_of_analysis:{ka2.get('level_of_analysis', 'n/a')}",
                    f"determination:{ka2.get('determination', 'undetermined')}",
                ],
                maat_alignment={
                    "truth": "Scored by KA2 scorecard axes.",
                    "balance": "Scorecard halt_flags enforced in code, not prose.",
                    "order": f"Schema: {SCHEMA_RECORD}",
                    "self_reflection": (
                        "correction_notes"
                        if (record_dict.get("maat_scorecard") or {}).get("correction_notes")
                        else "passed without correction"
                    ),
                },
            )

        scorecard = record_dict.get("maat_scorecard") or {}
        if scorecard and not scorecard.get("passed", False):
            # MaatMemoryPostgres.log_learning(agent, topic, insight, source, ...)
            out["learning_id"] = mem.log_learning(
                agent=agent,
                topic="scorecard",
                insight=(
                    scorecard.get("correction_notes")
                    or f"total={scorecard.get('total')} halt_flags={scorecard.get('halt_flags')}"
                ),
                source=f"gateway={gateway_id} correlation_id={correlation_id}",
                confidence=0.85,
                applied=False,
                application_context="archivist_gitmaat.persist",
            )

        return out


_default_adapter: ArchivistGitMaatAdapter | None = None
_default_lock = threading.Lock()


def get_default_adapter(**kwargs: Any) -> ArchivistGitMaatAdapter:
    """Process-wide adapter used by the shim and router tests."""
    global _default_adapter
    with _default_lock:
        if _default_adapter is None:
            _default_adapter = ArchivistGitMaatAdapter(**kwargs)
    return _default_adapter


def persist(record: ArchivistRecord | dict[str, Any]) -> PersistResult:
    return get_default_adapter().persist(record)


__all__ = [
    "ArchivistGitMaatAdapter",
    "PersistResult",
    "DEFAULT_STREAM",
    "WORKSPACE_ROOT",
    "get_default_adapter",
    "persist",
]
