"""
Maat Write Mediation (T1 integrity) — server stamps content_origin.

Law: The thing that mints trust does not live in the process that could be compromised.
An agent holding a DSN can set content_origin='human_authored' on poisoned text —
every CHECK satisfied, quarantine bypassed. Provenance is only as strong as the write
path is mediated.

Clients may not declare their own trust level. Authenticated identity stamps origin.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional

from maat_memory.maat_provenance import ContentOrigin, ProvenanceError, parse_origin


class MediationError(PermissionError):
    """Refuse unauthenticated or elevating write."""


class PrincipalKind(str, Enum):
    AGENT = "agent"
    HUMAN = "human"
    SYSTEM = "system"


@dataclass(frozen=True)
class Principal:
    agent_id: str
    kind: PrincipalKind
    auth_method: str = "memory_token"

    def stamped_origin(self) -> ContentOrigin:
        if self.kind == PrincipalKind.AGENT:
            return ContentOrigin.AGENT_AUTHORED
        if self.kind == PrincipalKind.HUMAN:
            return ContentOrigin.HUMAN_AUTHORED
        if self.kind == PrincipalKind.SYSTEM:
            return ContentOrigin.SYSTEM_GENERATED
        raise MediationError(f"unknown principal kind {self.kind!r}")


def stamp_origin(principal: Principal) -> ContentOrigin:
    """Server-side only. Never derived from client-supplied content_origin."""
    if not principal.agent_id or not str(principal.agent_id).strip():
        raise MediationError("principal.agent_id required — absence is not identity")
    return principal.stamped_origin()


def refuse_client_origin(
    claimed: str | ContentOrigin | None,
    stamped: ContentOrigin,
) -> ContentOrigin:
    """Client must not supply origin. Any claim that differs from stamp → refuse.

    Matching claim is still refused: the client is not the mint. Stamp wins only
    when claim is absent. If claim is present at all → ProvenanceError
    (defense against 'I pinky-promise I'm human').
    """
    if claimed is None or (isinstance(claimed, str) and not claimed.strip()):
        return stamped
    raise ProvenanceError(
        f"client claimed content_origin={claimed!r} but only the mediator may stamp "
        f"(identity → {stamped.value}) — refusing"
    )


def resolve_write_origin(
    principal: Principal,
    *,
    claimed_origin: str | ContentOrigin | None = None,
) -> ContentOrigin:
    stamped = stamp_origin(principal)
    return refuse_client_origin(claimed_origin, stamped)


# ── Token registry (broker-held) ─────────────────────────────────────────────

def _hash_token(token: str, *, pepper: str) -> str:
    return hmac.new(
        pepper.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


@dataclass
class TokenRegistry:
    """Maps bearer tokens → Principal. Lives only on the mediator host."""

    path: Path
    pepper: str
    _by_hash: dict[str, Principal]

    @classmethod
    def load(cls, path: Path, *, pepper: str | None = None) -> "TokenRegistry":
        pepper = pepper or os.environ.get("MAAT_MEMORY_TOKEN_PEPPER") or "maat-memory-token-v1"
        path = path.expanduser()
        data: dict[str, Any] = {"tokens": {}}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        by_hash: dict[str, Principal] = {}
        for th, meta in (data.get("tokens") or {}).items():
            by_hash[th] = Principal(
                agent_id=str(meta["agent_id"]),
                kind=PrincipalKind(meta.get("kind", "agent")),
                auth_method=str(meta.get("auth_method", "memory_token")),
            )
        return cls(path=path, pepper=pepper, _by_hash=by_hash)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "maat.memory_tokens.v1",
            "tokens": {
                th: {
                    "agent_id": p.agent_id,
                    "kind": p.kind.value,
                    "auth_method": p.auth_method,
                }
                for th, p in self._by_hash.items()
            },
        }
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.path.chmod(0o600)

    def issue(self, agent_id: str, *, kind: PrincipalKind = PrincipalKind.AGENT) -> str:
        raw = secrets.token_urlsafe(32)
        th = _hash_token(raw, pepper=self.pepper)
        self._by_hash[th] = Principal(
            agent_id=agent_id.strip(),
            kind=kind,
            auth_method="memory_token",
        )
        self.save()
        return raw

    def resolve(self, bearer: str | None) -> Principal:
        if not bearer or not str(bearer).strip():
            raise MediationError("bearer token required — absence is not authentication")
        token = bearer.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        th = _hash_token(token, pepper=self.pepper)
        principal = self._by_hash.get(th)
        if principal is None:
            raise MediationError("invalid memory token")
        return principal


class MediatedWriter:
    """Wraps MaatMemoryPostgres (or compatible) — stamps origin, ignores client claim."""

    def __init__(self, memory: Any, principal: Principal):
        self._memory = memory
        self._principal = principal
        self._origin = stamp_origin(principal)

    @property
    def principal(self) -> Principal:
        return self._principal

    @property
    def origin(self) -> ContentOrigin:
        return self._origin

    def _assert_capacity(self) -> None:
        """Durable coordination writes require measured storage capacity."""
        try:
            from maat_memory.memory_plane.storage import StorageAwareness, StorageCapacityError
            from maat_memory.memory_plane.registry import FleetRegistry

            reg = FleetRegistry()
            agent = reg.get_agent(self._principal.agent_id)
            mid = (agent or {}).get("machine_id")
            StorageAwareness(reg).assert_capacity(str(mid) if mid else None)
        except StorageCapacityError:
            raise
        except Exception as e:
            # Fail closed if plane unavailable for capacity — unless explicitly skipped
            import os

            if os.environ.get("MAAT_STORAGE_CAPACITY_OPTIONAL", "").strip() in (
                "1",
                "true",
                "yes",
            ):
                return
            from maat_memory.memory_plane.storage import StorageCapacityError

            raise StorageCapacityError(
                f"capacity_unmeasured:{type(e).__name__}"
            ) from e

    def log_task(self, title: str, description: str, **kwargs: Any) -> str:
        kwargs.pop("origin", None)
        kwargs.pop("agent", None)
        self._assert_capacity()
        return self._memory.log_task(
            self._principal.agent_id,
            title,
            description,
            origin=self._origin.value,
            **kwargs,
        )

    def log_decision(
        self,
        context: str,
        decision_made: str,
        rationale: str,
        **kwargs: Any,
    ) -> str:
        kwargs.pop("origin", None)
        kwargs.pop("agent", None)
        self._assert_capacity()
        return self._memory.log_decision(
            self._principal.agent_id,
            context,
            decision_made,
            rationale,
            origin=self._origin.value,
            **kwargs,
        )


__all__ = [
    "MediationError",
    "PrincipalKind",
    "Principal",
    "stamp_origin",
    "refuse_client_origin",
    "resolve_write_origin",
    "TokenRegistry",
    "MediatedWriter",
]
