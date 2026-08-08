"""Storage awareness — resolve URIs via class + machine storage roots."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from . import db
from .registry import FleetRegistry


STORAGE_CLASSES = frozenset(
    {"constitutional", "coordination", "learning", "artifact", "ephemeral"}
)

# Default full threshold — unset env still applies this (absence ≠ skip check).
DEFAULT_STORAGE_FULL_PCT = 92.0


class StorageCapacityError(PermissionError):
    """Durable write refused — capacity not attested or disk too full."""


class StorageAwareness:
    def __init__(self, registry: FleetRegistry | None = None):
        self.registry = registry or FleetRegistry()

    def full_pct_threshold(self) -> float:
        raw = os.environ.get("MAAT_STORAGE_FULL_PCT")
        if raw is None or not str(raw).strip():
            return DEFAULT_STORAGE_FULL_PCT
        return float(raw)

    def check_capacity(
        self,
        machine_id: str | None = None,
        *,
        prefer_data_drive: bool = True,
    ) -> dict[str, Any]:
        """Fail-closed capacity attestation for durable writes.

        Measures only declared roots (maat_storage_roots ∪ machine.storage_roots).
        Prefer /mnt/data_drive when declared and under threshold.
        Unmeasured required roots → deny (absence ≠ compliance).
        """
        threshold = self.full_pct_threshold()
        mid = machine_id
        if not mid:
            info = self.registry.enroll_machine()
            mid = str(info.get("machine_id") or "")

        declared: list[dict[str, Any]] = []
        rows = db.fetchall(
            """
            SELECT root_id, storage_class, base_uri, machine_id
            FROM maat_storage_roots
            WHERE (%s IS NULL) OR machine_id = %s
            ORDER BY updated_at DESC
            """,
            (mid, mid),
        )
        for row in rows:
            path = self._uri_to_path(str(row.get("base_uri") or ""))
            declared.append(
                {
                    "root_id": row.get("root_id"),
                    "storage_class": row.get("storage_class"),
                    "path": str(path) if path else None,
                    "source": "maat_storage_roots",
                }
            )

        machine = self.registry.get_machine(mid) if mid else None
        soft = (machine or {}).get("storage_roots") or {}
        if isinstance(soft, str):
            try:
                soft = json.loads(soft)
            except Exception:
                soft = {}
        if isinstance(soft, dict):
            for key, val in soft.items():
                if not val:
                    continue
                p = Path(str(val))
                declared.append(
                    {
                        "root_id": f"machine:{key}",
                        "storage_class": "coordination",
                        "path": str(p),
                        "source": "maat_machines.storage_roots",
                    }
                )

        if not declared:
            return {
                "ok": False,
                "reason": "no_declared_roots",
                "machine_id": mid,
                "threshold_pct": threshold,
                "hint": "enroll + bootstrap_local_roots before durable writes",
                "roots": [],
            }

        measured: list[dict[str, Any]] = []
        failures: list[str] = []
        for item in declared:
            path_s = item.get("path")
            if not path_s:
                failures.append(f"{item.get('root_id')}:unmapped_uri")
                continue
            path = Path(path_s)
            probe = path if path.exists() else path.parent
            while not probe.exists() and probe != probe.parent:
                probe = probe.parent
            if not probe.exists():
                failures.append(f"{item.get('root_id')}:path_missing:{path_s}")
                continue
            try:
                usage = shutil.disk_usage(probe)
            except OSError as e:
                failures.append(f"{item.get('root_id')}:stat_failed:{e}")
                continue
            pct = (usage.used / usage.total) * 100.0 if usage.total else 100.0
            measured.append(
                {
                    **item,
                    "probe": str(probe.resolve()),
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "used_pct": round(pct, 2),
                    "under_threshold": pct < threshold,
                }
            )

        if not measured:
            return {
                "ok": False,
                "reason": "capacity_unmeasured",
                "machine_id": mid,
                "threshold_pct": threshold,
                "failures": failures,
                "roots": [],
                "hint": "declared roots could not be measured — refuse durable write",
            }

        preferred = None
        if prefer_data_drive:
            for m in measured:
                if "/mnt/data_drive" in (m.get("probe") or "") and m.get("under_threshold"):
                    preferred = m
                    break
        if preferred is None:
            under = [m for m in measured if m.get("under_threshold")]
            preferred = under[0] if under else None

        if preferred is None:
            return {
                "ok": False,
                "reason": "all_roots_full",
                "machine_id": mid,
                "threshold_pct": threshold,
                "preferred_root": None,
                "roots": measured,
                "failures": failures,
                "hint": f"all measured roots at or above {threshold}% — refuse durable write",
            }

        return {
            "ok": True,
            "machine_id": mid,
            "threshold_pct": threshold,
            "preferred_root": preferred,
            "roots": measured,
            "failures": failures,
        }

    def assert_capacity(self, machine_id: str | None = None) -> dict[str, Any]:
        result = self.check_capacity(machine_id)
        if not result.get("ok"):
            raise StorageCapacityError(
                result.get("reason")
                or "storage capacity check failed — absence is not compliance"
            )
        return result

    @staticmethod
    def _uri_to_path(uri: str) -> Path | None:
        if not uri:
            return None
        if uri.startswith("file://"):
            return Path(unquote(urlparse(uri).path))
        return Path(uri)

    def register_root(
        self,
        *,
        root_id: str,
        storage_class: str,
        base_uri: str,
        machine_id: str,
        scheme: str = "file",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if storage_class not in STORAGE_CLASSES:
            raise ValueError(f"invalid storage_class: {storage_class}")
        db.execute(
            """
            INSERT INTO maat_storage_roots (
                root_id, storage_class, scheme, base_uri, machine_id, metadata, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
            ON CONFLICT (root_id) DO UPDATE SET
                storage_class = EXCLUDED.storage_class,
                scheme = EXCLUDED.scheme,
                base_uri = EXCLUDED.base_uri,
                machine_id = EXCLUDED.machine_id,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            """,
            (
                root_id,
                storage_class,
                scheme,
                base_uri,
                machine_id,
                json.dumps(metadata or {}),
            ),
        )

    def bootstrap_local_roots(self, machine_id: str, workspace: str | None = None) -> list[str]:
        """Register common lab roots for this machine — prefer data_drive."""
        roots = []
        data_drive = Path("/mnt/data_drive")
        if workspace is None:
            workspace = (
                str(data_drive)
                if data_drive.is_dir()
                else str(Path.home() / ".n8n")
            )
        candidates = {
            "artifact_hermes": (
                "artifact",
                "/mnt/data_drive/hermes/research-artifacts"
                if data_drive.is_dir()
                else f"{workspace}/hermes/research-artifacts",
            ),
            "artifact_evidence": (
                "artifact",
                "/mnt/data_drive/hermes/evidence-packs"
                if data_drive.is_dir()
                else f"{workspace}/hermes/evidence-packs",
            ),
            "coordination_maatlangchain": (
                "coordination",
                "/mnt/data_drive/maatlangchain"
                if (data_drive / "maatlangchain").is_dir()
                else f"{workspace}/maatlangchain",
            ),
        }
        if data_drive.is_dir():
            candidates["artifact_lab"] = ("artifact", "/mnt/data_drive/hermes")
        for root_id, (cls, path) in candidates.items():
            p = Path(path)
            if p.exists():
                self.register_root(
                    root_id=f"{root_id}:{machine_id[:32]}",
                    storage_class=cls,
                    base_uri=p.resolve().as_uri(),
                    machine_id=machine_id,
                    scheme="file",
                )
                roots.append(root_id)
        return roots

    def resolve(
        self, uri: str, *, prefer_machine_id: str | None = None
    ) -> dict[str, Any]:
        parsed = urlparse(uri)

        if parsed.scheme == "maat" or (
            parsed.scheme in ("http", "https") and "lab-artifacts" in uri
        ):
            from .artifact_bank import ArtifactBank

            out = ArtifactBank(self.registry, self).fetch(uri)
            if out.get("ok"):
                return {
                    "ok": True,
                    "uri": uri,
                    "sha256": out.get("sha256"),
                    "bytes": out.get("bytes"),
                    "content_type": out.get("content_type"),
                    "text": out.get("text"),
                    "public_uri": out.get("public_uri"),
                    "portable_uri": out.get("portable_uri"),
                    "storage_class": "artifact",
                    "source": out.get("source", "object_store"),
                }

        if parsed.scheme in ("", "file"):
            path = Path(unquote(parsed.path if parsed.scheme == "file" else uri))
            if path.exists() and path.is_file():
                return self._file_result(uri, path, "artifact")
            remapped = self._remap_via_roots(str(path), prefer_machine_id)
            if remapped and remapped.exists():
                return self._file_result(uri, remapped, "artifact")
            from .artifact_bank import ArtifactBank

            bank = ArtifactBank(self.registry, self)
            obj = bank.fetch(uri)
            if obj.get("ok") and obj.get("source") != "local_or_remap":
                return {
                    "ok": True,
                    "uri": uri,
                    "sha256": obj.get("sha256"),
                    "bytes": obj.get("bytes"),
                    "text": obj.get("text"),
                    "portable_uri": obj.get("portable_uri"),
                    "public_uri": obj.get("public_uri"),
                    "storage_class": "artifact",
                    "source": "object_store_fallback",
                    "hint": "file:// missing locally; served from maat_artifact_objects",
                }
            return {
                "ok": False,
                "uri": uri,
                "error": "not_found_on_this_host",
                "hint": "Promote with: maat_memory_plane.py promote --path <file>",
            }

        if parsed.scheme in ("http", "https"):
            from .artifact_bank import ArtifactBank

            out = ArtifactBank(self.registry, self).fetch(uri)
            if out.get("ok"):
                return {
                    "ok": True,
                    "uri": uri,
                    "sha256": out.get("sha256"),
                    "bytes": out.get("bytes"),
                    "text": out.get("text"),
                    "storage_class": "artifact",
                    "source": out.get("source", "object_store"),
                }
            return {
                "ok": False,
                "uri": uri,
                "error": "https_unresolved",
                "hint": "Promote artifact into object store for fleet fetch",
            }

        return {
            "ok": False,
            "uri": uri,
            "error": f"unsupported_scheme:{parsed.scheme}",
            "hint": "Supported: file://, maat://object/<sha>, maat://artifact/<slug>, https lab-artifacts",
        }

    def _remap_via_roots(
        self, abs_path: str, prefer_machine_id: str | None
    ) -> Path | None:
        rows = db.fetchall(
            "SELECT * FROM maat_storage_roots ORDER BY updated_at DESC"
        )
        if prefer_machine_id:
            rows = sorted(
                rows,
                key=lambda r: 0 if r.get("machine_id") == prefer_machine_id else 1,
            )
        for row in rows:
            base = row.get("base_uri") or ""
            if not base.startswith("file://"):
                continue
            base_path = Path(unquote(urlparse(base).path))
            name = Path(abs_path).name
            candidate = base_path / name
            if candidate.exists():
                return candidate
            norm = abs_path.replace("\\", "/")
            for marker in ("research-artifacts/", "evidence-packs/", "maatlangchain/"):
                if marker in norm:
                    tail = norm.split(marker, 1)[1]
                    cand = base_path / tail
                    if cand.exists():
                        return cand
        return None

    def _file_result(self, uri: str, path: Path, storage_class: str) -> dict[str, Any]:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        return {
            "ok": True,
            "uri": uri,
            "path": str(path.resolve()),
            "sha256": digest,
            "bytes": len(data),
            "storage_class": storage_class,
        }

    def content_hash_file(self, path: str | Path) -> str:
        data = Path(path).read_bytes()
        return hashlib.sha256(data).hexdigest()
