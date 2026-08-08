#!/usr/bin/env python3
"""
Test Docling extraction on a problematic PDF
"""

import os
import sys
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

# Load .env
env_file = Path("/home/suspect/.n8n/tehuti-lab-webui/.env")
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL=") or line.startswith("PGVECTOR_DB_URL ="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ["PGVECTOR_DB_URL"] = value
                    break

from core.chains.document_processor import DocumentProcessor
from api.main import get_vector_store

# Test with a problematic PDF that was blank
test_pdf = maatlangchain_root / "docs" / "RBG_Library" / "R-2" / "Ra-Un-Nefer-Amen- The 11 Laws of Ma'at.pdf"

if not test_pdf.exists():
    print(f"Test PDF not found: {test_pdf}")
    sys.exit(1)

print("=" * 80)
print("TESTING DOCLING EXTRACTION")
print("=" * 80)
print(f"PDF: {test_pdf}")
print()

try:
    vector_store, embeddings = get_vector_store()
    
    # Test with Docling OCR enabled
    print("Testing with Docling OCR enabled...")
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=2500,
        min_chunk_size=200,
        skip_front_pages=0,
        use_ocr=True,  # Enable OCR
    )
    
    documents = processor.load_pdf(str(test_pdf))
    
    print(f"\nLoaded {len(documents)} documents")
    print()
    
    if documents:
        # Show first few documents
        print("First 5 documents:")
        for i, doc in enumerate(documents[:5], 1):
            content = doc.page_content
            print(f"\nDocument {i}:")
            print(f"  Length: {len(content)} chars")
            print(f"  Words: {len(content.split())}")
            print(f"  Metadata: {doc.metadata}")
            print(f"  Content preview (first 300 chars):")
            print(f"  {repr(content[:300])}")
            print()
        
        # Check for empty documents
        empty_count = sum(1 for doc in documents if not doc.page_content.strip())
        print(f"\nEmpty documents: {empty_count}/{len(documents)}")
        
        # Total content
        total_content = "\n\n".join([doc.page_content for doc in documents])
        print(f"\nTotal extracted content: {len(total_content)} chars")
        print(f"Total words: {len(total_content.split())}")
        
        if len(total_content.strip()) > 1000:
            print("\n✅ SUCCESS: Docling extracted substantial content!")
        else:
            print("\n⚠️  WARNING: Extracted content is still very small")
    else:
        print("❌ ERROR: No documents loaded!")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

