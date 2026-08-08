"""Bind score ↔ tree ↔ machine. Absence of provenance is not a clean SHA."""

from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path
from typing import Any


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        return ""
    return (r.stdout or "").strip()


def find_git_root(start: Path) -> Path | None:
    cur = start.resolve()
    for path in [cur, *cur.parents]:
        if (path / ".git").exists():
            return path
    return None


def capture_provenance(
    runner_path: Path,
    *,
    allow_dirty: bool = False,
) -> dict[str, Any]:
    """Stamp git_sha, dirty, machine_id, runner_path. Fail-closed on dirty unless allowed."""
    root = find_git_root(runner_path) or runner_path
    sha_full = _git(root, "rev-parse", "HEAD")
    sha_short = _git(root, "rev-parse", "--short", "HEAD")
    porcelain = _git(root, "status", "--porcelain")
    dirty = bool(porcelain)
    machine_id = (
        os.environ.get("MAAT_MACHINE_ID")
        or os.environ.get("COMPUTERNAME")
        or socket.gethostname()
        or "unknown-machine"
    )
    prov = {
        "git_sha": sha_short or "unknown",
        "git_sha_full": sha_full or "unknown",
        "dirty": dirty,
        "allow_dirty": allow_dirty,
        "machine_id": machine_id,
        "runner_path": str(runner_path.resolve()),
        "repo_root": str(root.resolve()),
        "publishable": (not dirty) and bool(sha_full),
    }
    if dirty and not allow_dirty:
        prov["publishable"] = False
        prov["error"] = (
            "Dirty working tree — refusing to emit a publishable score. "
            "Commit/stash, or pass --allow-dirty (stamps dirty:true; not for public receipts)."
        )
    elif dirty and allow_dirty:
        prov["publishable"] = False
        prov["note"] = "dirty:true — score may not be published as a clean SHA claim."
    return prov
