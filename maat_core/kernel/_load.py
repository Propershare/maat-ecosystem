"""Load maat-core/kernel modules (hyphen dir) as maat_core.kernel.*."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_KERNEL_DIR = Path(__file__).resolve().parent.parent.parent / "maat-core" / "kernel"


def export_module(name: str):
    path = _KERNEL_DIR / f"{name}.py"
    if not path.is_file():
        raise ImportError(f"maat-core kernel module not found: {path}")
    spec = importlib.util.spec_from_file_location(f"_maat_kernel_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load kernel module: {name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
