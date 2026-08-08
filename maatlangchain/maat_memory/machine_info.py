"""
Auto-detect machine, workspace, and terminal information.
Maat: Truth — always know where data comes from.

Agent IDs must distinguish Cursor/OpenCode instances by workspace root,
not only hostname — e.g. data_drive vs .n8n vs another project dir.
"""

from __future__ import annotations

import os
import re
import socket
from pathlib import Path
from typing import Any, Dict, Optional


def get_machine_info() -> Dict[str, Any]:
    """
    Get machine, workspace, and terminal information.

    Returns keys include hostname, machine_id, terminal_id, working_directory,
    workspace_root, workspace_slug, project_path, user, platform.
    """
    workspace_root = _detect_workspace_root()
    return {
        "hostname": socket.gethostname(),
        "machine_id": _get_machine_id(),
        "terminal_id": _get_terminal_id(),
        "working_directory": str(Path.cwd()),
        "workspace_root": str(workspace_root) if workspace_root else None,
        "workspace_slug": _workspace_slug(workspace_root),
        "project_path": _detect_project_path(),
        "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
        "platform": os.name,
        "env": {
            "TERM": os.getenv("TERM", "unknown"),
            "SHELL": os.getenv("SHELL", "unknown"),
            "MAAT_AGENT_ID": os.getenv("MAAT_AGENT_ID", ""),
            "MAAT_WORKSPACE_SLUG": os.getenv("MAAT_WORKSPACE_SLUG", ""),
        },
    }


def _get_machine_id() -> str:
    """Get unique machine identifier (host-scoped, not workspace)."""
    hostname = socket.gethostname()
    try:
        import uuid

        mac = ":".join(
            [
                "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                for elements in range(0, 2 * 6, 2)
            ][::-1]
        )
        return f"{hostname}-{mac}"
    except Exception:
        return hostname


def _get_terminal_id() -> str:
    term_id = os.getenv("TERM_SESSION_ID")
    if term_id:
        return term_id
    return f"terminal-{os.getpid()}"


def _cursor_project_key() -> Optional[str]:
    """
    Cursor's opened-window id from ~/.cursor/projects/<key>/.

    AGENT_TRANSCRIPTS is set by Cursor agents to
    .../projects/<key>/agent-transcripts — that key is the opened folder,
    not the shell cwd (which may be anywhere).
    """
    at = os.getenv("AGENT_TRANSCRIPTS", "").strip()
    if at:
        p = Path(at)
        if p.name == "agent-transcripts":
            return p.parent.name
        # tolerate .../projects/<key>
        for parent in p.parents:
            if parent.parent.name == "projects" and parent.parent.parent.name == ".cursor":
                return parent.name
            if parent.name == "projects" and parent.parent.name == ".cursor":
                break

    # Fallback: CURSOR projects dir in common agent paths
    for key in ("AGENT_TRANSCRIPTS", "CURSOR_PROJECT_DIR"):
        raw = os.getenv(key, "").strip()
        if not raw:
            continue
        parts = Path(raw).parts
        if "projects" in parts:
            i = parts.index("projects")
            if i + 1 < len(parts):
                return parts[i + 1]
    return None


def _path_from_cursor_project_key(key: str) -> Optional[Path]:
    """
    Best-effort decode Cursor project key → filesystem path.

    Cursor encodes folder paths by replacing `/` with `-`
    (e.g. /mnt/data_drive → mnt-data-drive). Hyphens inside
    folder names make full reverse ambiguous, so we match known
    roots first, then try the remainder as a child path.
    """
    roots = [
        ("mnt-data-drive", Path("/mnt/data_drive")),
        ("home-suspect-n8n", Path.home() / ".n8n"),
        ("home-suspect-maat-ecosystem", Path.home() / "maat-ecosystem"),
        ("home-suspect-comfyui", Path.home() / "comfyui"),
        ("home-suspect-suspectcontent", Path.home() / "suspectcontent"),
    ]
    roots.sort(key=lambda x: len(x[0]), reverse=True)

    for prefix, base in roots:
        if not base.is_dir():
            continue
        if key == prefix:
            return base.resolve()
        if key.startswith(prefix + "-"):
            rest = key[len(prefix) + 1 :]
            # Prefer whole remainder as one directory name (ka-education)
            for cand in (base / rest, base / rest.replace("-", "_")):
                if cand.is_dir():
                    return cand.resolve()
            # Then try splitting on - as nested dirs
            nested = base.joinpath(*rest.split("-"))
            if nested.is_dir():
                return nested.resolve()
            return base.resolve()  # known window family; child may be renamed

    return None


def _slug_from_cursor_project_key(key: str) -> str:
    """Friendly slug from Cursor project key."""
    friendly = {
        "mnt-data-drive": "data_drive",
        "home-suspect-n8n": "n8n",
        "home-suspect-maat-ecosystem": "maat_ecosystem",
    }
    if key in friendly:
        return friendly[key]
    if key.startswith("mnt-data-drive-"):
        # Opened a subfolder under data_drive
        return _sanitize_slug("data_drive_" + key[len("mnt-data-drive-") :])
    if key.startswith("home-suspect-n8n-"):
        return _sanitize_slug("n8n_" + key[len("home-suspect-n8n-") :])
    if key.startswith("mnt-"):
        return _sanitize_slug(key[len("mnt-") :])
    if key.startswith("home-suspect-"):
        return _sanitize_slug(key[len("home-suspect-") :])
    return _sanitize_slug(key)


def _detect_workspace_root(start: Optional[Path] = None) -> Optional[Path]:
    """
    Detect the agent workspace root (Cursor window / project tree).

    Priority:
    1. MAAT_WORKSPACE_ROOT env
    2. Cursor opened folder (AGENT_TRANSCRIPTS → ~/.cursor/projects/<key>)
    3. Walk up for lab markers (memory-bank, .cursorrules, hermes+maatlangchain)
    4. Known roots: /mnt/data_drive, ~/.n8n
    5. cwd
    """
    override = os.getenv("MAAT_WORKSPACE_ROOT", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        if p.is_dir():
            return p

    # Cursor window beats shell cwd — you may cd into ~/.n8n while Window is data_drive
    cursor_key = _cursor_project_key()
    if cursor_key:
        cursor_root = _path_from_cursor_project_key(cursor_key)
        if cursor_root:
            return cursor_root

    try:
        from .paths import find_workspace_root

        found = find_workspace_root(start)
        if found:
            return found.resolve()
    except Exception:
        pass

    cur = (start or Path.cwd()).resolve()
    markers = ("memory-bank", ".cursorrules", "maatlangchain", "hermes")
    for path in [cur] + list(cur.parents):
        if any((path / m).exists() for m in markers):
            return path

    home_n8n = (Path.home() / ".n8n").resolve()
    data_drive = Path("/mnt/data_drive").resolve()
    for root in (data_drive, home_n8n):
        try:
            cur.relative_to(root)
            return root
        except ValueError:
            continue

    return cur


def _workspace_slug(workspace_root: Optional[Path]) -> str:
    """
    Short stable slug for agent_id.

    Examples:
      /mnt/data_drive              → data_drive
      /mnt/data_drive/ka-education → data_drive_ka_education
      ~/.n8n                       → n8n
      ~/.n8n/maat-ecosystem        → n8n_maat_ecosystem
    """
    env_slug = os.getenv("MAAT_WORKSPACE_SLUG", "").strip()
    if env_slug:
        return _sanitize_slug(env_slug)

    # Prefer Cursor project key (opened window), even if cwd differs
    cursor_key = _cursor_project_key()
    if cursor_key:
        return _slug_from_cursor_project_key(cursor_key)[:48]

    if workspace_root is None:
        return "unknown"

    root = workspace_root.resolve()
    home_n8n = (Path.home() / ".n8n").resolve()
    data_drive = Path("/mnt/data_drive").resolve()

    def rel_slug(base: Path, label: str) -> str:
        try:
            rel = root.relative_to(base)
        except ValueError:
            return ""
        if str(rel) in (".", ""):
            return label
        parts = [label] + [p for p in rel.parts if p not in (".",)]
        return _sanitize_slug("_".join(parts))

    for base, label in ((data_drive, "data_drive"), (home_n8n, "n8n")):
        slug = rel_slug(base, label)
        if slug:
            return slug[:48]

    # Fallback: last two path components
    parts = [p for p in root.parts if p and p != "/"]
    tail = parts[-2:] if len(parts) >= 2 else parts
    return _sanitize_slug("_".join(tail))[:48] or "workspace"


def _sanitize_slug(s: str) -> str:
    s = s.strip().lower().replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "workspace"


def _detect_project_path() -> Optional[str]:
    """Detect maatlangchain path if present."""
    try:
        from .paths import get_maatlangchain_path

        ml = get_maatlangchain_path()
        if ml and ml.is_dir():
            return str(ml.resolve())
    except Exception:
        pass

    cwd = Path.cwd()
    if "maatlangchain" in str(cwd):
        for path in [cwd] + list(cwd.parents):
            if (path / "maatlangchain").exists() or path.name == "maatlangchain":
                return str(
                    path / "maatlangchain" if path.name != "maatlangchain" else path
                )
    return None


def get_unique_agent_id(tool_type: str = "opencode") -> str:
    """
    Unique agent ID: tool + host + workspace (+ terminal for OpenCode).

    Format:
      Cursor:   cursor_<hostname>_<workspace_slug>
      OpenCode: opencode_<hostname>_<workspace_slug>_<terminal>

    Examples:
      cursor_staydangerous_data_drive
      cursor_staydangerous_n8n
      cursor_staydangerous_data_drive_ka_education
      opencode_staydangerous_n8n_12345

    Override entire id with MAAT_AGENT_ID.
    Override slug only with MAAT_WORKSPACE_SLUG.
    Override root detection with MAAT_WORKSPACE_ROOT.
    """
    explicit = os.getenv("MAAT_AGENT_ID", "").strip()
    if explicit:
        return explicit

    info = get_machine_info()
    hostname = str(info["hostname"]).lower()
    slug = info.get("workspace_slug") or "unknown"
    tool = tool_type.lower().strip() or "opencode"

    if tool == "cursor":
        return f"cursor_{hostname}_{slug}"

    terminal_id = str(info["terminal_id"]).replace("terminal-", "").replace("-", "_")
    terminal_id = _sanitize_slug(terminal_id)[:24]
    return f"opencode_{hostname}_{slug}_{terminal_id}"
