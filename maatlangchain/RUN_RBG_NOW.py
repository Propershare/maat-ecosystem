#!/usr/bin/env python3
"""
Direct execution - Run RBG processing now
"""

import sys
import os
from pathlib import Path

# Set working directory
os.chdir(Path(__file__).parent)

# Import and execute
sys.path.insert(0, str(Path(__file__).parent))

# Execute the processing script
exec(compile(open('scripts/execute_rbg_processing.py').read(), 'scripts/execute_rbg_processing.py', 'exec'))

