#!/usr/bin/env python3
"""Execute RBG library processing - direct execution"""

import sys
import os
from pathlib import Path

# Change to script directory
os.chdir(Path(__file__).parent)

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and execute
exec(open('scripts/process_rbg_library.py').read())

