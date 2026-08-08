#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

script_path = Path(__file__).parent / "map_txt_to_pdf.py"
result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, cwd=str(Path(__file__).parent))
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)
sys.exit(result.returncode)

