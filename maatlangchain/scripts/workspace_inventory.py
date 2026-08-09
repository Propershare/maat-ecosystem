#!/usr/bin/env python3
"""
Workspace Inventory — list top-level directories/files in a workspace root
with size, file count, last-modified, and git status (if applicable).

Usage:
    python3 workspace_inventory.py <root> [--format tsv|markdown|json] [--depth 1] [--exclude PATTERN]

Examples:
    # TSV (default) — pipe to less, awk, or spreadsheet
    python3 workspace_inventory.py /home/suspect/.n8n > inventory-n8n.tsv

    # Markdown table for an artifact
    python3 workspace_inventory.py /home/suspect/.n8n --format markdown > section.md

    # JSON for downstream tooling
    python3 workspace_inventory.py /mnt/data_drive --format json --depth 2

Output columns (TSV/MD):
    depth       0 = file, 1 = top-level dir, 2 = nested
    path        absolute path
    type        file | dir | symlink
    bytes       size in bytes (0 for unreadable)
    file_count  for dirs: number of files inside
    last_mod    ISO 8601 date (YYYY-MM-DD) of mtime
    git_status  tracked | untracked | embedded-git | external | root-owned

Why this exists:
    Per refs/workspace-inventory-bom-2026-08-08 §6 (Accountability pillar),
    the inventory script must be reproducible from the repo, not just exist
    as /tmp/workspace-inventory.sh. This file is the canonical form.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

# Skip these at any depth — they're either noise (node_modules) or
# dangerous to recurse into (proc, sys).
DEFAULT_EXCLUDE = {
    "node_modules",
    "__pycache__",
    ".git",
    ".cache",
    "venv",
    ".venv",
    ".venvs",
    "site-packages",
    "dist",
    "build",
}


@dataclass
class Entry:
    depth: int
    path: str
    type: str  # file | dir | symlink
    bytes: int
    file_count: int
    last_mod: str  # ISO date
    git_status: str  # tracked | untracked | embedded-git | external | root-owned

    def to_tsv(self) -> str:
        return "\t".join(
            str(getattr(self, f))
            for f in ("depth", "path", "type", "bytes", "file_count", "last_mod", "git_status")
        )

    def to_markdown_row(self) -> str:
        size_h = _humanize(self.bytes)
        return (
            f"| `{self.path}` | {self.type} | {size_h} | "
            f"{self.file_count} | {self.last_mod} | {self.git_status} |"
        )


def _humanize(n: int) -> str:
    """Return size with unit suffix."""
    if n < 1024:
        return f"{n}B"
    for unit, scale in [("K", 1024), ("M", 1024**2), ("G", 1024**3), ("T", 1024**4)]:
        if n < scale * 1024:
            return f"{n / scale:.1f}{unit}"
    return f"{n / (1024**4):.1f}T"


def _detect_git_status(path: Path, root: Path) -> str:
    """Classify the path's git status relative to the nearest .git/."""
    try:
        if (path / ".git").is_dir():
            return "embedded-git"
    except (PermissionError, OSError):
        return "root-owned"

    # Walk up to find the nearest .git/
    cur = path if path.is_dir() else path.parent
    while cur != cur.parent:
        try:
            if (cur / ".git").is_dir():
                repo_root = cur
                try:
                    rel = str(path.relative_to(repo_root))
                except ValueError:
                    return "external"

                result = subprocess.run(
                    ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", rel],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return "tracked"
                return "untracked"
        except (PermissionError, OSError):
            pass
        cur = cur.parent

    return "external"


def _safe_du(path: Path) -> tuple[int, int]:
    """Return (size_bytes, file_count) for a directory. Handles permission errors.

    Symlinks are not followed (counts only the symlink itself).
    """
    total = 0
    count = 0
    try:
        for entry in path.rglob("*"):
            try:
                # is_file() follows symlinks by default — guard with lstat
                st = entry.stat()
                if stat.S_ISLNK(st.st_mode):
                    continue  # don't follow symlinks
                if stat.S_ISREG(st.st_mode):
                    total += st.st_size
                    count += 1
                elif stat.S_ISDIR(st.st_mode):
                    count += 1
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass
    return total, count


def _last_mod(p: Path) -> str:
    try:
        mtime = p.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except (PermissionError, OSError):
        return "unreadable"


def _walk(root: Path, depth: int, excludes: set[str]) -> Iterator[Entry]:
    """Yield entries up to `depth` levels deep. depth=1 means top-level only."""
    yield from _walk_at(root, root, 0, depth, excludes)


def _walk_at(
    root: Path, current: Path, current_depth: int, max_depth: int, excludes: set[str]
) -> Iterator[Entry]:
    """Recursive helper."""
    if current_depth > max_depth:
        return

    try:
        items = sorted(current.iterdir(), key=lambda p: p.name)
    except (PermissionError, OSError):
        return

    for p in items:
        if p.name in excludes:
            continue

        # Stat
        try:
            st = p.stat()
        except (PermissionError, OSError):
            yield Entry(
                depth=current_depth,
                path=str(p),
                type="dir" if p.is_dir() else "file",
                bytes=0,
                file_count=0,
                last_mod="unreadable",
                git_status="root-owned",
            )
            continue

        if p.is_symlink():
            yield Entry(
                depth=current_depth,
                path=str(p),
                type="symlink",
                bytes=0,
                file_count=0,
                last_mod=_last_mod(p),
                git_status=_detect_git_status(p, root),
            )
            continue

        if p.is_dir():
            size, count = _safe_du(p)
            yield Entry(
                depth=current_depth,
                path=str(p),
                type="dir",
                bytes=size,
                file_count=count,
                last_mod=_last_mod(p),
                git_status=_detect_git_status(p, root),
            )
            if current_depth < max_depth:
                yield from _walk_at(root, p, current_depth + 1, max_depth, excludes)
        elif p.is_file():
            yield Entry(
                depth=current_depth,
                path=str(p),
                type="file",
                bytes=st.st_size,
                file_count=1,
                last_mod=_last_mod(p),
                git_status=_detect_git_status(p, root),
            )


def render_tsv(entries: list[Entry]) -> str:
    lines = ["depth\tpath\ttype\tbytes\tfile_count\tlast_mod\tgit_status"]
    lines.extend(e.to_tsv() for e in entries)
    return "\n".join(lines) + "\n"


def render_markdown(entries: list[Entry]) -> str:
    lines = [
        "| path | type | size | files | last_mod | git_status |",
        "|------|------|------|-------|----------|------------|",
    ]
    lines.extend(e.to_markdown_row() for e in entries)
    return "\n".join(lines) + "\n"


def render_json(entries: list[Entry]) -> str:
    return json.dumps(
        {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "count": len(entries),
            "entries": [asdict(e) for e in entries],
        },
        indent=2,
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a structured inventory of a workspace root.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("root", type=Path, help="Workspace root to inventory")
    parser.add_argument(
        "--format",
        choices=("tsv", "markdown", "json"),
        default="tsv",
        help="Output format (default: tsv)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Recursion depth: 1 = top-level only, 2 = one level deeper, etc.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Additional directory names to exclude (may be repeated)",
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        print(f"error: {args.root} is not a directory", file=sys.stderr)
        return 2

    excludes = DEFAULT_EXCLUDE | set(args.exclude)
    entries = list(_walk(args.root.resolve(), args.depth, excludes))

    if args.format == "tsv":
        print(render_tsv(entries), end="")
    elif args.format == "markdown":
        print(render_markdown(entries), end="")
    elif args.format == "json":
        print(render_json(entries), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))