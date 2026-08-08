#!/usr/bin/env python3
"""Execute RBG processing immediately"""

import sys
import os
from pathlib import Path

# Change to maatlangchain root
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

# Import and execute main
from scripts.run_rbg_processing_direct import main

if __name__ == "__main__":
    main()

