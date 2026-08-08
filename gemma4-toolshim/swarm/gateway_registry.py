"""
Gateway registry.

A gateway is a named surface = ``{id, default_expert, archivist_schema,
retrieval_packs, tools, research_type_default, level_of_analysis_default,
model, preset_file}``. Adding a gateway is a data change — a registry entry
plus (optionally) a retrieval pack — not a router edit, per
docs/MAAT-EVOLUTION-LANES.md.

Registry source of truth lives at:

    maat-ecosystem/skeleton/gateways/registry.yaml

and, for runtime, is merged with OpenClaw presets under ``openclaw/presets/``
and (when live) Ka Discovery's ``/manifest``. The merge is:

    registry.yaml  >  OpenClaw preset (display fields)  >  Ka Discovery (liveness)

This module is stdlib-only; YAML is parsed via a narrow reader that accepts
the same flat dialect emitted by :mod:`forge.retrieval_proposals`. If the
workspace has PyYAML installed it will be used for richer inputs.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


def _find_lab_root() -> Path:
    here = Path(__file__).resolve()
    for p in (here, *here.parents):
        if (p / "maat-ecosystem").is_dir() and (p / "gemma4-toolshim").is_dir():
            return p
    return Path.cwd()


LAB_ROOT = _find_lab_root()
REGISTRY_PATH = LAB_ROOT / "maat-ecosystem" / "skeleton" / "gateways" / "registry.yaml"
PRESETS_ROOT = LAB_ROOT / "openclaw" / "presets"
PACKS_ROOT = LAB_ROOT / "data" / "retrieval_packs"


@dataclass
class GatewayEntry:
    id: str
    description: str = ""
    default_expert: str = ""
    archivist_schema: str = "maat.archivist_record.v1"
    research_type_default: str = "descriptive"
    level_of_analysis_default: str = "system"
    model: str = "ollama/gemma4:e4b"
    retrieval_packs: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    preset_file: str | None = None
    ka_discovery_organ: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _try_pyyaml_load(text: str) -> dict[str, Any] | None:
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    try:
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception:
        return None
    return None


def _simple_yaml_load(text: str) -> dict[str, Any]:
    """Very small YAML subset: top-level keys with indented mappings of
    ``key: value`` and ``- item`` lists. Matches what we emit ourselves.
    """
    out: dict[str, Any] = {}
    stack: list[tuple[int, Any, str | None]] = [(0, out, None)]
    lines = text.splitlines()
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        while stack and indent < stack[-1][0]:
            stack.pop()
        parent_indent, parent, parent_key = stack[-1]

        if line.startswith("- "):
            value = line[2:].strip()
            if parent_key is not None:
                if parent_key not in parent:
                    parent[parent_key] = []
                parent[parent_key].append(value)
            continue

        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            container: dict[str, Any] = {}
            parent[key] = container
            stack.append((indent + 2, container, key))
        else:
            parent[key] = _coerce_scalar(val)
    return out


def _coerce_scalar(val: str) -> Any:
    if val.lower() in {"true", "false"}:
        return val.lower() == "true"
    if val.lower() in {"null", "none", "~"}:
        return None
    try:
        if val.startswith("0") and val != "0" and not val.startswith("0."):
            return val
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val.strip("'\"")


def _parse_registry(text: str) -> list[dict[str, Any]]:
    """Accept either ``{gateways: [...]}`` (preferred) or a flat list."""
    parsed = _try_pyyaml_load(text) or _simple_yaml_load(text)
    if isinstance(parsed, dict):
        if "gateways" in parsed and isinstance(parsed["gateways"], list):
            return [g for g in parsed["gateways"] if isinstance(g, dict)]
        return [parsed]
    if isinstance(parsed, list):
        return [g for g in parsed if isinstance(g, dict)]
    return []


class GatewayRegistry:
    """In-memory view of registered gateways."""

    def __init__(self, entries: Iterable[GatewayEntry] | None = None) -> None:
        self._entries: dict[str, GatewayEntry] = {}
        for e in entries or []:
            self._entries[e.id] = e

    @property
    def entries(self) -> dict[str, GatewayEntry]:
        return dict(self._entries)

    def get(self, gateway_id: str) -> GatewayEntry | None:
        return self._entries.get(gateway_id)

    def add(self, entry: GatewayEntry) -> None:
        if entry.id in self._entries:
            raise KeyError(f"gateway already registered: {entry.id!r}")
        self._entries[entry.id] = entry

    def upsert(self, entry: GatewayEntry) -> None:
        self._entries[entry.id] = entry

    def list_ids(self) -> list[str]:
        return sorted(self._entries.keys())

    def to_dict(self) -> dict[str, Any]:
        return {"gateways": [e.to_dict() for e in self._entries.values()]}

    def snapshot(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def load(cls, path: Path | str | None = None) -> "GatewayRegistry":
        target = Path(path) if path else REGISTRY_PATH
        if not target.exists():
            return cls()
        entries: list[GatewayEntry] = []
        for raw in _parse_registry(target.read_text()):
            kwargs = dict(raw)
            known = set(GatewayEntry.__dataclass_fields__)
            kwargs = {k: v for k, v in kwargs.items() if k in known}
            for list_field in ("retrieval_packs", "tools"):
                v = kwargs.get(list_field)
                if isinstance(v, str):
                    kwargs[list_field] = [x.strip() for x in v.split(",") if x.strip()]
            entries.append(GatewayEntry(**kwargs))
        return cls(entries)

    def check_preset_files(self) -> list[tuple[str, str]]:
        """Return list of (gateway_id, missing_path) for any preset that
        points at a file that does not exist on disk."""
        missing: list[tuple[str, str]] = []
        for entry in self._entries.values():
            if not entry.preset_file:
                continue
            target = (LAB_ROOT / entry.preset_file).resolve()
            if not target.exists():
                missing.append((entry.id, str(target)))
        return missing

    def check_retrieval_packs(self) -> list[tuple[str, str]]:
        """Return list of (gateway_id, missing_pack) for any declared pack
        whose directory is not present under ``data/retrieval_packs``."""
        missing: list[tuple[str, str]] = []
        for entry in self._entries.values():
            for pack_id in entry.retrieval_packs:
                pack_dir = PACKS_ROOT / pack_id
                if not pack_dir.is_dir():
                    missing.append((entry.id, str(pack_dir)))
        return missing


def discovery_manifest_url() -> str:
    """Ka Discovery URL from env or default. Reads but does not call."""
    return os.getenv("KA_DISCOVERY_URL", "http://127.0.0.1:8010/manifest")


def fetch_discovery_manifest(url: str | None = None, *, timeout: float = 1.5) -> dict[str, Any]:
    """Best-effort Ka Discovery probe. Returns ``{}`` on any failure."""
    import urllib.error
    import urllib.request

    target = url or discovery_manifest_url()
    try:
        with urllib.request.urlopen(target, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, Exception):
        return {}


__all__ = [
    "GatewayEntry",
    "GatewayRegistry",
    "REGISTRY_PATH",
    "PRESETS_ROOT",
    "PACKS_ROOT",
    "discovery_manifest_url",
    "fetch_discovery_manifest",
]


if __name__ == "__main__":
    reg = GatewayRegistry.load()
    print(f"registry: {REGISTRY_PATH}")
    print(f"ids: {reg.list_ids()}")
    for gid in reg.list_ids():
        entry = reg.get(gid)
        if entry:
            print(f"  - {gid}: packs={entry.retrieval_packs} preset={entry.preset_file}")
    missing_presets = reg.check_preset_files()
    missing_packs = reg.check_retrieval_packs()
    if missing_presets:
        print("missing presets:")
        for gid, path in missing_presets:
            print(f"  {gid} -> {path}")
    if missing_packs:
        print("missing packs:")
        for gid, path in missing_packs:
            print(f"  {gid} -> {path}")
    sys.exit(0)
