"""Resolve lab root, manifest, and profile paths."""

from __future__ import annotations

import os
from pathlib import Path


def discover_lab_root() -> Path | None:
    """Prefer MAAT_LAB_ROOT; else walk up from cwd for maat-ecosystem + .cursorrules."""
    env = os.environ.get("MAAT_LAB_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p
    p = Path.cwd().resolve()
    for _ in range(10):
        if (p / "maat-ecosystem").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def default_manifest_paths() -> list[Path]:
    """Search order for machine manifest."""
    paths: list[Path] = []
    if os.environ.get("MAAT_MACHINE_MANIFEST"):
        paths.append(Path(os.environ["MAAT_MACHINE_MANIFEST"]).expanduser().resolve())
    home = Path.home()
    paths.extend(
        [
            home / ".maat" / "config" / "machine.yaml",
            home / ".maat" / "config" / "machine.yml",
            home / ".maat" / "config" / "machine.json",
            Path("/etc/maat/machine.yaml"),
            Path("/etc/maat/machine.json"),
        ],
    )
    return paths


def default_profile_paths() -> list[Path]:
    paths: list[Path] = []
    if os.environ.get("MAAT_PROFILE"):
        paths.append(Path(os.environ["MAAT_PROFILE"]).expanduser().resolve())
    home = Path.home()
    paths.extend(
        [
            home / ".maat" / "config" / "profile.yaml",
            home / ".maat" / "config" / "profile.yml",
            home / ".maat" / "config" / "profile.json",
        ],
    )
    return paths


def find_first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None
