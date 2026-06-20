"""Lived-truth maatbench suites.

Every fixture under :mod:`maatbench.suites` corresponds to a real captured
turn (archivist record), a real guard_case, or a real gitMaat event.
Synthetic-only fixtures do not belong here per docs/MAAT-EVOLUTION-LANES.md.

Suites live in subfolders:

    gateway_contract/   - ArchivistRecord conformance fixtures
    policy/             - Guard decision fixtures (mirrors ../../guard_cases/)
    memory/             - Memory-fidelity fixtures (placeholder)
    models/             - Per-gateway model behaviour fixtures (placeholder)
"""

from pathlib import Path

SUITES_ROOT = Path(__file__).resolve().parent
