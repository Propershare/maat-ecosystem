"""Portable artifact bank — Balance for agentic memory across machines.

Catalog rows in maat_artifacts used to point at host-only file:// URIs.
This bank promotes bytes into Postgres (maat_artifact_objects) and optional
HTTPS mirrors under ka-education/public/lab-artifacts/.

Agents resolve:
  maat://object/<sha256>
  maat://artifact/<slug>
  https://maatecosystem.com/lab-artifacts/...
  file://... (local or remapped via storage roots)
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import shutil
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

from . import db
from .registry import FleetRegistry
from .storage import StorageAwareness

MAX_PROMOTE_BYTES = int(os.getenv("MAAT_ARTIFACT_MAX_BYTES", str(4 * 1024 * 1024)))
PUBLIC_BASE = os.getenv(
    "MAAT_ARTIFACT_PUBLIC_BASE", "https://maatecosystem.com/lab-artifacts"
).rstrip("/")
PUBLIC_DIR = Path(
    os.getenv(
        "MAAT_ARTIFACT_PUBLIC_DIR",
        "/mnt/data_drive/ka-education/public/lab-artifacts",
    )
)
HERMES_ARTIFACT_ROOTS = (
    Path("/mnt/data_drive/hermes/research-artifacts"),
    Path("/mnt/data_drive/hermes/evidence-packs"),
)


def object_uri(sha256: str) -> str:
    return f"maat://object/{sha256}"


def artifact_uri(slug: str) -> str:
    return f"maat://artifact/{slug}"


def _sanitize_slug(s: str) -> str:
    s = (s or "").strip().lower().replace(" ", "-")
    s = re.sub(r"[^a-z0-9._/-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-/")
    return s[:96] or "artifact"


def _guess_type(path: Path) -> str:
    ctype, _ = mimetypes.guess_type(str(path))
    return ctype or "application/octet-stream"


class ArtifactBank:
    """Content-addressed artifact object store + catalog sync."""

    def __init__(
        self,
        registry: FleetRegistry | None = None,
        storage: StorageAwareness | None = None,
    ):
        self.registry = registry or FleetRegistry()
        self.storage = storage or StorageAwareness(self.registry)

    def promote_file(
        self,
        path: str | Path,
        *,
        slug: str | None = None,
        artifact_id: str | None = None,
        title: str | None = None,
        agent_id: str | None = None,
        machine_id: str | None = None,
        publish_https: bool = True,
        update_catalog_uri: bool = True,
        ring: str | None = None,
        audience: str | None = None,
    ) -> dict[str, Any]:
        p = Path(path).expanduser().resolve()
        if not p.is_file():
            return {"ok": False, "error": "not_a_file", "path": str(p)}
        # Never promote secrets into the fleet object store / public mirror
        blocked = {".env", ".env.local", ".env.production", ".env.development", "credentials.json", "secrets.json"}
        if p.name in blocked or p.name.startswith(".env.") or ".pem" in p.name or p.suffix in {".key", ".p12"}:
            return {
                "ok": False,
                "error": "refused_secret_path",
                "path": str(p),
                "hint": "Do not promote env/credential files into maat_artifact_objects",
            }

        # Capacity + ring gate before any BYTEA / public mirror
        ids = self.registry.ensure_local("cursor") if not machine_id else None
        mid = machine_id or (ids or {}).get("machine_id")
        aid = agent_id or (ids or {}).get("agent_id")
        ok_durable, reason = self.registry.assert_can_write_durable(str(aid or "unknown"))
        if not ok_durable:
            return {"ok": False, "error": "durable_write_refused", "reason": reason, "path": str(p)}
        try:
            from .guard_gate import should_write_artifact

            agent_row = self.registry.get_agent(str(aid)) if aid else None
            agent_ring = (agent_row or {}).get("ring") or "outer"
            art_ring = ring or "outer"
            gate = should_write_artifact(
                agent_ring=str(agent_ring),
                artifact_ring=str(art_ring),
                title=title or p.name,
            )
            if gate is False or (isinstance(gate, dict) and not gate.get("ok", True)):
                return {"ok": False, "error": "guard_refused_artifact", "gate": gate, "path": str(p)}
        except ImportError:
            pass
        except Exception:
            pass  # capacity already enforced; guard optional

        data = p.read_bytes()
        if len(data) > MAX_PROMOTE_BYTES:
            return {
                "ok": False,
                "error": "too_large",
                "bytes": len(data),
                "max": MAX_PROMOTE_BYTES,
                "hint": "Raise MAAT_ARTIFACT_MAX_BYTES or publish large payloads separately",
            }

        sha = hashlib.sha256(data).hexdigest()
        ctype = _guess_type(p)
        local_uri = p.as_uri()
        if slug:
            slug_f = _sanitize_slug(slug)
        elif p.name == "index.html":
            slug_f = _sanitize_slug(p.parent.name)
        else:
            slug_f = _sanitize_slug(p.stem)
        logical = self._logical_path(p)

        public_uri = None
        if publish_https:
            public_uri = self._mirror_public(slug_f, p, data)

        db.execute(
            """
            INSERT INTO maat_artifact_objects (
                sha256, content, content_type, byte_len, logical_path, slug,
                source_uri, machine_id, public_uri, metadata, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW())
            ON CONFLICT (sha256) DO UPDATE SET
                slug = COALESCE(EXCLUDED.slug, maat_artifact_objects.slug),
                public_uri = COALESCE(EXCLUDED.public_uri, maat_artifact_objects.public_uri),
                logical_path = COALESCE(EXCLUDED.logical_path, maat_artifact_objects.logical_path),
                metadata = maat_artifact_objects.metadata || EXCLUDED.metadata,
                updated_at = NOW()
            """,
            (
                sha,
                data,
                ctype,
                len(data),
                logical,
                slug_f,
                local_uri,
                mid,
                public_uri,
                json.dumps({"promoted_by": aid, "filename": p.name}),
            ),
        )

        portable = object_uri(sha)
        from .handoff import audience_to_ring

        ring_n = audience_to_ring(audience, ring)
        catalog = self._sync_catalog(
            portable_uri=portable,
            sha=sha,
            local_uri=local_uri,
            public_uri=public_uri,
            slug=slug_f,
            artifact_id=artifact_id,
            title=title or p.name,
            agent_id=aid or "artifact_bank",
            machine_id=mid,
            logical_path=logical,
            update_uri=update_catalog_uri,
            byte_len=len(data),
            content_type=ctype,
            ring=ring_n,
            audience=audience,
        )

        return {
            "ok": True,
            "sha256": sha,
            "portable_uri": portable,
            "slug": slug_f,
            "ring": ring_n,
            "public_uri": public_uri,
            "local_uri": local_uri,
            "bytes": len(data),
            "content_type": ctype,
            "catalog": catalog,
        }

    def fetch(self, uri_or_sha: str) -> dict[str, Any]:
        """Fetch bytes for maat://object|artifact, sha256, or via StorageAwareness."""
        key = (uri_or_sha or "").strip()
        if not key:
            return {"ok": False, "error": "empty_uri"}

        # Bare sha
        if re.fullmatch(r"[a-fA-F0-9]{64}", key):
            return self._fetch_sha(key.lower())

        parsed = urlparse(key)
        if parsed.scheme == "maat":
            # maat://object/<sha> or maat://artifact/<slug>
            kind = (parsed.netloc or "").lower()
            rest = unquote(parsed.path.lstrip("/"))
            if kind == "object" and rest:
                return self._fetch_sha(rest.lower())
            if kind == "artifact" and rest:
                return self._fetch_slug(rest)
            # maat:///object/sha form
            parts = [p for p in key.replace("maat://", "").split("/") if p]
            if len(parts) >= 2 and parts[0] == "object":
                return self._fetch_sha(parts[1].lower())
            if len(parts) >= 2 and parts[0] == "artifact":
                return self._fetch_slug(parts[1])
            return {"ok": False, "error": "bad_maat_uri", "uri": key}

        if parsed.scheme in ("http", "https"):
            # Prefer object store if we know this public_uri
            row = db.fetchone(
                "SELECT sha256 FROM maat_artifact_objects WHERE public_uri = %s",
                (key,),
            )
            if row:
                return self._fetch_sha(row["sha256"])
            return {
                "ok": False,
                "error": "https_not_in_object_store",
                "uri": key,
                "hint": "Promote the file so agents can fetch via Postgres without HTTP",
            }

        # No scheme — could be a bare slug ("refs/foo-2026-08-08") or a local path.
        # Detect slug shape: contains '/' OR is a single token matching the slug
        # sanitizer's output (lowercase + dots/dashes/underscores, no extension).
        # Local files almost always have a dot-extension or an absolute path;
        # bare slugs in this lab look like "refs/<name>-<date>" or "<category>/<name>".
        if (
            "/" in key
            and not key.startswith("/")
            and not key.startswith("./")
            and not key.startswith("file:")
            and not Path(key).is_file()
            and re.fullmatch(r"[a-z0-9._/-]+", key)
        ):
            return self._fetch_slug(key)

        # file:// or bare path — local first (no StorageAwareness call → avoid recursion)
        path = self._path_from_uri(key) if key.startswith("file:") else Path(key)
        if path is not None and path.is_file():
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            text = None
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                pass
            return {
                "ok": True,
                "path": str(path.resolve()),
                "sha256": sha,
                "bytes": len(data),
                "text": text,
                "source": "local_file",
            }
        abs_path = str(path) if path else unquote(urlparse(key).path if key.startswith("file:") else key)
        row = db.fetchone(
            """
            SELECT sha256 FROM maat_artifact_objects
            WHERE source_uri = %s OR logical_path = %s
            ORDER BY updated_at DESC LIMIT 1
            """,
            (key, abs_path),
        )
        if row:
            out = self._fetch_sha(row["sha256"])
            out["source"] = "object_store_via_source_uri"
            return out
        # Remap via storage roots without re-entering ArtifactBank
        remapped = self.storage._remap_via_roots(abs_path, None)
        if remapped and remapped.is_file():
            data = remapped.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            return {
                "ok": True,
                "path": str(remapped.resolve()),
                "sha256": sha,
                "bytes": len(data),
                "source": "local_or_remap",
            }
        return {
            "ok": False,
            "uri": key,
            "error": "not_found_on_this_host",
            "hint": "Promote with maat_memory_plane.py promote --path <file>",
        }

    def promote_catalog(
        self,
        *,
        only_missing: bool = True,
        roots: list[Path] | None = None,
        every_agent_only: bool = False,
        publish_https: bool = True,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Promote maat_artifacts whose local file:// path exists on this host."""
        rows = db.fetchall(
            """
            SELECT id::text AS id, title, uri, portable_uri, content_sha256,
                   metadata, artifact_type, status
            FROM maat_artifacts
            ORDER BY created_at DESC NULLS LAST
            LIMIT %s
            """,
            (limit,),
        )
        promoted = []
        skipped = []
        failed = []
        for row in rows:
            meta = row.get("metadata") or {}
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except json.JSONDecodeError:
                    meta = {}
            if every_agent_only and meta.get("audience") != "every_lab_agent":
                skipped.append({"id": row["id"], "reason": "not_every_lab_agent"})
                continue
            if only_missing and row.get("content_sha256") and row.get("portable_uri"):
                # Still verify object exists
                if db.fetchone(
                    "SELECT 1 FROM maat_artifact_objects WHERE sha256 = %s",
                    (row["content_sha256"],),
                ):
                    skipped.append({"id": row["id"], "reason": "already_promoted"})
                    continue

            uri = row.get("uri") or ""
            path = self._path_from_uri(uri)
            if path is None or not path.is_file():
                # try metadata.local_uri
                path = self._path_from_uri(meta.get("local_uri") or "")
            if path is None or not path.is_file():
                skipped.append({"id": row["id"], "reason": "bytes_not_on_this_host", "uri": uri})
                continue
            if roots:
                try:
                    if not any(path.resolve().is_relative_to(r.resolve()) for r in roots):
                        skipped.append({"id": row["id"], "reason": "outside_roots"})
                        continue
                except (ValueError, AttributeError):
                    # py<3.9 fallback
                    ok_root = False
                    rp = str(path.resolve())
                    for r in roots:
                        if rp.startswith(str(r.resolve())):
                            ok_root = True
                            break
                    if not ok_root:
                        skipped.append({"id": row["id"], "reason": "outside_roots"})
                        continue

            slug = meta.get("slug") or (path.parent.name if path.name == "index.html" else None)
            out = self.promote_file(
                path,
                slug=slug,
                artifact_id=row["id"],
                title=row.get("title"),
                publish_https=publish_https,
                update_catalog_uri=True,
            )
            if out.get("ok"):
                promoted.append({"id": row["id"], "sha256": out["sha256"], "portable_uri": out["portable_uri"]})
            else:
                failed.append({"id": row["id"], **out})

        self._write_bank_index()
        return {
            "ok": True,
            "promoted": len(promoted),
            "skipped": len(skipped),
            "failed": len(failed),
            "items": promoted,
            "skipped_items": skipped[:40],
            "failed_items": failed,
            "public_index": f"{PUBLIC_BASE}/",
        }

    def list_objects(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = db.fetchall(
            """
            SELECT sha256, content_type, byte_len, logical_path, slug,
                   source_uri, public_uri, created_at, updated_at
            FROM maat_artifact_objects
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return [
            {
                **dict(r),
                "portable_uri": object_uri(r["sha256"]),
                "artifact_uri": artifact_uri(r["slug"]) if r.get("slug") else None,
            }
            for r in rows
        ]

    def _fetch_sha(self, sha: str) -> dict[str, Any]:
        row = db.fetchone(
            """
            SELECT sha256, content, content_type, byte_len, logical_path, slug,
                   source_uri, public_uri, metadata
            FROM maat_artifact_objects WHERE sha256 = %s
            """,
            (sha,),
        )
        if not row:
            return {"ok": False, "error": "object_not_found", "sha256": sha}
        content = bytes(row["content"])
        text = None
        ctype = row["content_type"] or ""
        if ctype.startswith("text/") or ctype in (
            "application/json",
            "application/javascript",
            "application/xml",
        ) or (row.get("logical_path") or "").endswith((".md", ".html", ".json", ".txt", ".csv")):
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = None
        return {
            "ok": True,
            "sha256": row["sha256"],
            "portable_uri": object_uri(row["sha256"]),
            "slug": row.get("slug"),
            "public_uri": row.get("public_uri"),
            "source_uri": row.get("source_uri"),
            "logical_path": row.get("logical_path"),
            "content_type": ctype,
            "bytes": row["byte_len"],
            "content_b64": None,  # keep payloads lean unless requested
            "text": text,
            "source": "object_store",
        }

    def _fetch_slug(self, slug: str) -> dict[str, Any]:
        row = db.fetchone(
            """
            SELECT sha256 FROM maat_artifact_objects
            WHERE slug = %s
            ORDER BY updated_at DESC LIMIT 1
            """,
            (_sanitize_slug(slug),),
        )
        if not row:
            # try catalog metadata.slug
            cat = db.fetchone(
                """
                SELECT content_sha256, portable_uri FROM maat_artifacts
                WHERE metadata->>'slug' = %s OR portable_uri = %s
                ORDER BY updated_at DESC NULLS LAST LIMIT 1
                """,
                (_sanitize_slug(slug), artifact_uri(slug)),
            )
            if cat and cat.get("content_sha256"):
                return self._fetch_sha(cat["content_sha256"])
            return {"ok": False, "error": "slug_not_found", "slug": slug}
        return self._fetch_sha(row["sha256"])

    def _sync_catalog(
        self,
        *,
        portable_uri: str,
        sha: str,
        local_uri: str,
        public_uri: str | None,
        slug: str,
        artifact_id: str | None,
        title: str,
        agent_id: str,
        machine_id: str | None,
        logical_path: str | None,
        update_uri: bool,
        byte_len: int,
        content_type: str,
        ring: str = "outer",
        audience: str | None = None,
    ) -> dict[str, Any]:
        from .handoff import audience_to_ring, normalize_ring

        ring_n = normalize_ring(audience_to_ring(audience, ring))
        meta_patch = {
            "slug": slug,
            "local_uri": local_uri,
            "public_uri": public_uri,
            "sha256": sha,
            "logical_path": logical_path,
            "storage_class": "object_backed",
            "balance": "object_store_v0",
            "ring": ring_n,
            "content_origin": "agent_authored",
            "topic": "external_audit_handoff_2026_07",
        }
        if audience:
            meta_patch["audience"] = audience
        if artifact_id:
            if update_uri:
                db.execute(
                    """
                    UPDATE maat_artifacts SET
                        uri = %s,
                        portable_uri = %s,
                        content_sha256 = %s,
                        ring = %s,
                        content_origin = COALESCE(content_origin, 'agent_authored'),
                        storage_class = 'object_backed',
                        metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                        updated_at = NOW()
                    WHERE id = %s::uuid
                    """,
                    (portable_uri, portable_uri, sha, ring_n, json.dumps(meta_patch), artifact_id),
                )
            else:
                db.execute(
                    """
                    UPDATE maat_artifacts SET
                        portable_uri = %s,
                        content_sha256 = %s,
                        ring = %s,
                        content_origin = COALESCE(content_origin, 'agent_authored'),
                        storage_class = 'object_backed',
                        metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                        updated_at = NOW()
                    WHERE id = %s::uuid
                    """,
                    (portable_uri, sha, ring_n, json.dumps(meta_patch), artifact_id),
                )
            return {"updated_id": artifact_id, "uri": portable_uri, "ring": ring_n}

        # Match by local uri
        existing = db.fetchone(
            """
            SELECT id::text AS id FROM maat_artifacts
            WHERE uri = %s OR metadata->>'local_uri' = %s
               OR (metadata->>'slug' = %s AND %s <> '')
            ORDER BY created_at DESC NULLS LAST LIMIT 1
            """,
            (local_uri, local_uri, slug, slug),
        )
        if existing:
            return self._sync_catalog(
                portable_uri=portable_uri,
                sha=sha,
                local_uri=local_uri,
                public_uri=public_uri,
                slug=slug,
                artifact_id=existing["id"],
                title=title,
                agent_id=agent_id,
                machine_id=machine_id,
                logical_path=logical_path,
                update_uri=update_uri,
                byte_len=byte_len,
                content_type=content_type,
                ring=ring_n,
                audience=audience,
            )

        # Insert new catalog row
        import uuid

        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO maat_artifacts (
                id, agent, machine, artifact_type, title, description, uri,
                metrics, metadata, status, content_sha256, portable_uri, ring,
                content_origin, storage_class
            ) VALUES (
                %s::uuid, %s, %s, 'html_artifact', %s, %s, %s,
                %s::jsonb, %s::jsonb, 'active', %s, %s, %s,
                'agent_authored', 'object_backed'
            )
            """,
            (
                new_id,
                agent_id,
                machine_id or "unknown",
                title,
                f"Promoted to object store ({byte_len} bytes, {content_type})",
                portable_uri if update_uri else local_uri,
                json.dumps({"bytes": byte_len, "sha256": sha}),
                json.dumps(meta_patch),
                sha,
                portable_uri,
                ring_n,
            ),
        )
        return {"created_id": new_id, "uri": portable_uri, "ring": ring_n}

    def _mirror_public(self, slug: str, src: Path, data: bytes) -> str:
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        dest_dir = PUBLIC_DIR / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        dest.write_bytes(data)
        # If promoting index.html, also copy sibling assets? keep v0 to single file.
        return f"{PUBLIC_BASE}/{slug}/{src.name}"

    def _write_bank_index(self) -> Path:
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        rows = self.list_objects(limit=200)
        items = []
        for r in rows:
            title = r.get("slug") or r["sha256"][:12]
            href = r.get("public_uri") or r["portable_uri"]
            items.append(
                f'<li><a href="{href}">{title}</a> '
                f'<code>{r["sha256"][:12]}</code> · {r["byte_len"]} B</li>'
            )
        html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab Artifact Bank — Maat Memory Plane</title>
<meta name="maat-artifact" content="tehuti.lab-artifact-bank">
<style>
body{{margin:0;padding:48px 24px;background:#0c0f0e;color:#e6ebe8;
font-family:Palatino,Georgia,serif;max-width:840px;margin-inline:auto}}
h1{{color:#c4a35a}} a{{color:#c4a35a}} code{{font-size:.85em;color:#8a968f}}
.lede{{color:#8a968f}} ul{{line-height:1.7}}
</style></head><body>
<p style="color:#c4a35a;letter-spacing:.12em;text-transform:uppercase;font-size:.75rem">
Tehuti Lab · Memory Plane Balance</p>
<h1>Lab Artifact Bank</h1>
<p class="lede">Portable object store. Catalog URI is <code>maat://object/&lt;sha256&gt;</code>
— any agent with Postgres can fetch bytes. HTTPS mirrors are convenience, not the truth claim.</p>
<ul>
{"".join(items) if items else "<li>Empty — run <code>maat_memory_plane.py promote-bank</code></li>"}
</ul>
</body></html>
"""
        out = PUBLIC_DIR / "index.html"
        out.write_text(html, encoding="utf-8")
        return out

    @staticmethod
    def _path_from_uri(uri: str) -> Optional[Path]:
        if not uri:
            return None
        if uri.startswith("file://"):
            return Path(unquote(urlparse(uri).path))
        if uri.startswith("maat://") or uri.startswith("http"):
            return None
        p = Path(uri)
        return p if p.exists() else None

    @staticmethod
    def _logical_path(path: Path) -> str:
        s = str(path.resolve()).replace("\\", "/")
        for marker in (
            "/hermes/research-artifacts/",
            "/hermes/evidence-packs/",
            "/ka-education/public/",
        ):
            if marker in s:
                return s.split(marker, 1)[1]
        return path.name
