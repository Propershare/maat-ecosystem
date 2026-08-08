#!/usr/bin/env python3
"""Test import to verify fix"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.chains.document_processor import DocumentProcessor, DATALAB_AVAILABLE
    print("✅ Import successful!")
    print(f"OCR Available: {DATALAB_AVAILABLE}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

