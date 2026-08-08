#!/usr/bin/env python3
"""
Quick run - Execute RBG processing directly
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and run
from scripts.execute_rbg_processing import main

if __name__ == "__main__":
    main()

