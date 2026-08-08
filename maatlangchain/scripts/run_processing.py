#!/usr/bin/env python3
"""
Direct execution wrapper for RBG library processing
Run this file directly to process PDFs
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))

# Import and run main processing
if __name__ == "__main__":
    # Import the processing function
    from process_rbg_library import main
    
    print("Starting RBG Library PDF Processing...")
    print("=" * 80)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

