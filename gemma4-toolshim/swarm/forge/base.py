"""Forge base types + promotion engine shared by all candidate paths."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

_SWARM_DIR = Path(__file__).resolve().parent.parent
if str(_SWARM_DIR) not in sys.path:
    sys.path.insert(0, str(_SWARM_DIR))

from gateway_contract import now_iso  # noqa: E402
from guard_validator import (  # noqa: E402
    DEFAULT_GUARD_URL,
    GUARD_URL_ENV,
)


class CandidateKind(str, Enum):
    RETRIEVAL_PACK = "retrieval_pack"
    ROUTER_KEYWORD = "router_keyword"
    PROMPT_ENVELOPE = "prompt_envelope"
    LORA_ADAPTER = "lora_adapter"


@dataclass
class Candidate:
    """A proposed evolution change. Immutable once created."""

    kind: CandidateKind
    gateway_id: str
    description: str
    diff: dict[str, Any]
    created_at: str = field(default_factory=now_iso)
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            h = hashlib.sha256()
            h.update(self.kind.value.encode())
            h.update(self.gateway_id.encode())
            h.update(json.dumps(self.diff, sort_keys=True).encode())
            h.update(self.created_at.encode())
            self.id = h.hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d


@dataclass
class PromotionResult:
    candidate: Candidate
    bench_before: dict[str, Any]
    bench_after: dict[str, Any]
    delta: float
    margin: float
    bench_pass: bool
    guard_status: str  # "allow" | "deny" | "review" | "not_checked"
    guard_reason: str
    promoted: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "bench_before": self.bench_before,
            "bench_after": self.bench_after,
            "delta": round(self.delta, 4),
            "margin": round(self.margin, 4),
            "bench_pass": self.bench_pass,
            "guard_status": self.guard_status,
            "guard_reason": self.guard_reason,
            "promoted": self.promoted,
            "notes": list(self.notes),
        }


BenchFn = Callable[[str], dict[str, Any]]  # (gateway_id) -> {"score": float, ...}
ApplyFn = Callable[[Candidate], None]
RevertFn = Callable[[Candidate], None]
GuardFn = Callable[[Candidate, dict[str, Any], dict[str, Any]], tuple[str, str]]


def guard_promote(
    candidate: Candidate,
    bench_before: dict[str, Any],
    bench_after: dict[str, Any],
    *,
    guard_url: str | None = None,
) -> tuple[str, str]:
    """Ask Tehuti Guard whether to promote. Returns (status, reason).

    This is a thin wrapper around the Guard HTTP ``/decision`` endpoint used
    elsewhere in the lab. When Guard is unreachable we default to
    ``"review"`` so humans decide, never ``"allow"`` — a silent promotion is
    forbidden per docs/MAAT-EVOLUTION-LANES.md.
    """
    import os
    import urllib.error
    import urllib.request

    target = (
        guard_url or os.getenv(GUARD_URL_ENV) or DEFAULT_GUARD_URL
    ).rstrip("/")
    payload = {
        "schema": "maat.guard_promotion_request.v1",
        "candidate": candidate.to_dict(),
        "bench_before": bench_before,
        "bench_after": bench_after,
    }
    try:
        req = urllib.request.Request(
            f"{target}/decision",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            decision = body.get("decision", "review")
            if decision not in {"allow", "deny", "review"}:
                decision = "review"
            return decision, body.get("reason", "guard_responded")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return "review", "guard_unreachable_defaulting_to_review"
    except Exception as exc:  # noqa: BLE001
        return "review", f"guard_error:{type(exc).__name__}"


class Promoter:
    """Runs the universal proposal-to-registry cycle."""

    def __init__(
        self,
        *,
        bench_fn: BenchFn,
        apply_fn: ApplyFn,
        revert_fn: RevertFn,
        margin: float = 0.02,
        guard_fn: GuardFn | None = None,
        log_fn: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.bench_fn = bench_fn
        self.apply_fn = apply_fn
        self.revert_fn = revert_fn
        self.margin = float(margin)
        self.guard_fn = guard_fn or (
            lambda c, b1, b2: guard_promote(c, b1, b2)
        )
        self.log_fn = log_fn

    def evaluate(self, candidate: Candidate) -> PromotionResult:
        notes: list[str] = []
        before = self.bench_fn(candidate.gateway_id)
        notes.append(f"bench_before_score={before.get('score')}")

        try:
            self.apply_fn(candidate)
        except Exception as exc:  # noqa: BLE001
            result = PromotionResult(
                candidate=candidate,
                bench_before=before,
                bench_after={},
                delta=0.0,
                margin=self.margin,
                bench_pass=False,
                guard_status="not_checked",
                guard_reason=f"apply_failed:{type(exc).__name__}:{exc}",
                promoted=False,
                notes=notes + [f"apply raised: {exc!r}"],
            )
            self._log(result)
            return result

        try:
            after = self.bench_fn(candidate.gateway_id)
        except Exception as exc:  # noqa: BLE001
            self.revert_fn(candidate)
            result = PromotionResult(
                candidate=candidate,
                bench_before=before,
                bench_after={},
                delta=0.0,
                margin=self.margin,
                bench_pass=False,
                guard_status="not_checked",
                guard_reason=f"bench_failed:{type(exc).__name__}",
                promoted=False,
                notes=notes + [f"bench raised: {exc!r}"],
            )
            self._log(result)
            return result

        notes.append(f"bench_after_score={after.get('score')}")

        delta = float(after.get("score", 0.0)) - float(before.get("score", 0.0))
        bench_pass = delta >= self.margin
        notes.append(f"delta={delta:.4f} margin={self.margin:.4f} pass={bench_pass}")

        if not bench_pass:
            self.revert_fn(candidate)
            result = PromotionResult(
                candidate=candidate,
                bench_before=before,
                bench_after=after,
                delta=delta,
                margin=self.margin,
                bench_pass=False,
                guard_status="not_checked",
                guard_reason="bench_below_margin",
                promoted=False,
                notes=notes + ["reverted after bench fail"],
            )
            self._log(result)
            return result

        status, reason = self.guard_fn(candidate, before, after)
        notes.append(f"guard={status}:{reason}")
        if status != "allow":
            self.revert_fn(candidate)
            result = PromotionResult(
                candidate=candidate,
                bench_before=before,
                bench_after=after,
                delta=delta,
                margin=self.margin,
                bench_pass=True,
                guard_status=status,
                guard_reason=reason,
                promoted=False,
                notes=notes + ["reverted after guard non-allow"],
            )
            self._log(result)
            return result

        result = PromotionResult(
            candidate=candidate,
            bench_before=before,
            bench_after=after,
            delta=delta,
            margin=self.margin,
            bench_pass=True,
            guard_status=status,
            guard_reason=reason,
            promoted=True,
            notes=notes + ["promoted"],
        )
        self._log(result)
        return result

    def _log(self, result: PromotionResult) -> None:
        if self.log_fn is not None:
            try:
                self.log_fn(result.to_dict())
            except Exception:  # noqa: BLE001
                pass


__all__ = [
    "Candidate",
    "CandidateKind",
    "PromotionResult",
    "Promoter",
    "guard_promote",
]
