"""Bootstrap Tehuti Lab paths so MaatBench runners resolve local packages."""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parent
_ECO_ROOT = _BENCH_DIR.parent
_LAB_ROOT = _ECO_ROOT.parent
_BOOTSTRAPPED = False


def lab_root() -> Path:
    return _LAB_ROOT


def bootstrap() -> Path:
    """Add lab root, maatlangchain, and maat-ecosystem to sys.path once."""
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return _LAB_ROOT

    for path in (_LAB_ROOT, _LAB_ROOT / "maatlangchain", _ECO_ROOT):
        s = str(path)
        if s not in sys.path:
            sys.path.insert(0, s)

    adapters_link = _LAB_ROOT / "maat_adapters"
    adapters_src = _LAB_ROOT / "maat-adapters"
    if adapters_src.is_dir() and not adapters_link.exists():
        adapters_link.symlink_to("maat-adapters")

    _BOOTSTRAPPED = True
    return _LAB_ROOT
