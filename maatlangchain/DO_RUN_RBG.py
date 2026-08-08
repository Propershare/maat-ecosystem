#!/usr/bin/env python3
"""Execute RBG processing - run this file"""

import subprocess
import sys
from pathlib import Path

script_path = Path(__file__).parent / "scripts" / "run_rbg_processing_direct.py"

print("=" * 80)
print("Starting RBG Library PDF Processing")
print("=" * 80)
print()

try:
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(Path(__file__).parent),
        capture_output=False,
        text=True
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error executing script: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

