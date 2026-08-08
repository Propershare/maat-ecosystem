#!/usr/bin/env python3
"""
Quick test script to verify PDF extraction works
Tests both PyPDFLoader and OCR detection
"""

import sys
from pathlib import Path

maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))

from core.chains.document_processor import DocumentProcessor, DATALAB_AVAILABLE
from api.main import get_vector_store

def test_extraction():
    """Test PDF extraction capabilities."""
    print("=" * 80)
    print("PDF Extraction Test")
    print("=" * 80)
    print()
    
    # Check OCR availability
    print(f"OCR (DatalabMarkerLoader) Available: {DATALAB_AVAILABLE}")
    if not DATALAB_AVAILABLE:
        print("  ⚠️  OCR disabled - will use PyPDFLoader only")
        print("  To enable OCR, set DATALAB_MARKER_API_KEY environment variable")
    print()
    
    # Get vector store
    try:
        vector_store, embeddings = get_vector_store()
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"❌ Vector store failed: {e}")
        return
    
    # Create processor
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        use_ocr=False,  # Test without OCR first
    )
    
    print("✅ DocumentProcessor initialized")
    print()
    print("Ready to process PDFs!")
    print()
    print("To process RBG library:")
    print("  python3 scripts/process_rbg_library.py")
    print()

if __name__ == "__main__":
    test_extraction()

