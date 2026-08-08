#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# Run the test script
test_script = Path(__file__).parent / "test_maatcode_integration.py"
result = subprocess.run([sys.executable, str(test_script)], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)
sys.exit(result.returncode)

