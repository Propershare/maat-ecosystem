"""
Maat Memory System - Cross-Session Memory for Cursor and OpenCode

Auto-setup on import - agents configure themselves automatically.
"""

import logging
import os
from pathlib import Path

# Set up logging
log = logging.getLogger(__name__)

# Auto-setup on first import
_auto_setup_done = False

def _run_auto_setup():
    """Run auto-setup on first import."""
    global _auto_setup_done
    
    if _auto_setup_done:
        return
    
    try:
        from .auto_setup import run_auto_setup
        
        # Detect tool type from environment or default to opencode
        tool_type = os.getenv("MAAT_TOOL_TYPE", "opencode")
        
        # Run auto-setup (silent by default to avoid spam)
        report = run_auto_setup(tool_type, verbose=False)
        
        # Log critical issues only
        if report["status"] == "warning":
            if report["structure"]["issues"]:
                log.warning(f"Maat Auto-Setup: {len(report['structure']['issues'])} issues detected")
            if report["conflicts"]["conflicts"]:
                log.warning(f"Maat Auto-Setup: {len(report['conflicts']['conflicts'])} conflicts detected")
        
        _auto_setup_done = True
        
    except Exception as e:
        log.warning(f"Maat Auto-Setup failed: {e}")
        _auto_setup_done = True  # Don't retry

# Run auto-setup
_run_auto_setup()

# Export main classes - Auto-select backend
import os
from .machine_info import get_machine_info, get_unique_agent_id
from .auto_setup import MaatAutoSetup, run_auto_setup
from .standards import MaatStandards
from .project_discovery import ProjectDiscovery, discover_project
from .maat_provenance import (
    ContentOrigin,
    ProvenanceError,
    ScopeViolation,
    quarantine,
    render_memory_context,
    parse_origin,
    verify_legacy_debt,
)

# Auto-select backend:
# 1) Mediated write client when WRITE_URL + AGENT_TOKEN (agents — no DSN)
# 2) PostgreSQL if PGVECTOR_DB_URL is set (organs / broker)
# 3) JSON only with explicit opt-in
from .paths import find_workspace_root, get_pgvector_db_url

_pgvector_url = get_pgvector_db_url()
_allow_json = os.getenv("MAAT_MEMORY_ALLOW_JSON", "").strip().lower() in ("1", "true", "yes")
_require_postgres = os.getenv("MAAT_MEMORY_REQUIRE_POSTGRES", "").strip().lower() in ("1", "true", "yes")
_in_lab = find_workspace_root() is not None
_mediated = (
    os.getenv("MAAT_MEMORY_MEDIATED", "").strip().lower() in ("1", "true", "yes")
    or (
        bool(os.getenv("MAAT_MEMORY_WRITE_URL", "").strip())
        and bool(os.getenv("MAAT_MEMORY_AGENT_TOKEN", "").strip())
    )
)
_allow_dsn = os.getenv("MAAT_MEMORY_ALLOW_DSN", "").strip().lower() in ("1", "true", "yes")
_role = (os.getenv("MAAT_CREDENTIAL_ROLE") or "").strip().lower()

if _mediated and not _allow_dsn:
    from .mediated_client import MediatedMemoryClient as MaatMemory
elif _pgvector_url:
    if _role == "agent" and not _allow_dsn:
        raise RuntimeError(
            "Maat Memory: agent role must not hold PGVECTOR_DB_URL. "
            "Set MAAT_MEMORY_WRITE_URL + MAAT_MEMORY_AGENT_TOKEN (mediated writes), "
            "or MAAT_MEMORY_ALLOW_DSN=1 only on the memory organ/broker."
        )
    from .memory_postgres import MaatMemoryPostgres as MaatMemory
elif _require_postgres or (_in_lab and not _allow_json):
    raise RuntimeError(
        "Maat Memory: set MAAT_MEMORY_WRITE_URL + MAAT_MEMORY_AGENT_TOKEN (agents), "
        "or PGVECTOR_DB_URL on the memory organ, or MAAT_MEMORY_ALLOW_JSON=1 for offline JSON."
    )
else:
    from .memory import MaatMemory

# Memory Plane (fleet registry / learning loop / storage / presence) — optional import
try:
    from .memory_plane import (
        FleetRegistry,
        LearningLoop,
        SessionPresence,
        StorageAwareness,
        run_preflight,
    )
except Exception:  # noqa: BLE001 — plane may be absent on older checkouts
    FleetRegistry = None  # type: ignore
    LearningLoop = None  # type: ignore
    SessionPresence = None  # type: ignore
    StorageAwareness = None  # type: ignore
    run_preflight = None  # type: ignore

__all__ = [
    "MaatMemory",
    "get_machine_info",
    "get_unique_agent_id",
    "MaatAutoSetup",
    "run_auto_setup",
    "MaatStandards",
    "ProjectDiscovery",
    "discover_project",
    "FleetRegistry",
    "LearningLoop",
    "SessionPresence",
    "StorageAwareness",
    "run_preflight",
    "ContentOrigin",
    "ProvenanceError",
    "ScopeViolation",
    "quarantine",
    "render_memory_context",
    "parse_origin",
    "verify_legacy_debt",
]
