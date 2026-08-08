#!/usr/bin/env python3
"""Legacy entrypoint — delegates to canonical maat-ecosystem/maatbench (O-1)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_CANON = Path(__file__).resolve().parent.parent / "maat-ecosystem" / "maatbench" / "run.py"
if not _CANON.is_file():
    print(f"Canonical runner missing: {_CANON}", file=sys.stderr)
    raise SystemExit(2)
print(
    "NOTE: root maatbench/ is legacy — running canonical maat-ecosystem/maatbench/run.py",
    file=sys.stderr,
)
sys.argv[0] = str(_CANON)
runpy.run_path(str(_CANON), run_name="__main__")
