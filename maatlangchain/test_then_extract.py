#!/usr/bin/env python3
"""
Test Docling extraction, then proceed with full re-extraction if successful
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

print("=" * 80)
print("TESTING DOCLING EXTRACTION")
print("=" * 80)

try:
    from core.chains.document_processor import DocumentProcessor
    from api.main import get_vector_store
    
    # Test with a problematic PDF that was blank
    test_pdf = maatlangchain_root / "docs" / "RBG_Library" / "R-2" / "Ra-Un-Nefer-Amen- The 11 Laws of Ma'at.pdf"
    
    if not test_pdf.exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        sys.exit(1)
    
    print(f"Testing PDF: {test_pdf.name}")
    print()
    
    vector_store, embeddings = get_vector_store()
    
    # Test with Docling OCR enabled
    print("Initializing DocumentProcessor with OCR enabled...")
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=2500,
        min_chunk_size=200,
        skip_front_pages=0,
        use_ocr=True,  # Enable OCR
    )
    
    print("Loading PDF with Docling...")
    documents = processor.load_pdf(str(test_pdf))
    
    print(f"\n✅ Loaded {len(documents)} documents")
    print()
    
    if documents:
        # Show first few documents
        print("First 3 documents:")
        for i, doc in enumerate(documents[:3], 1):
            content = doc.page_content
            print(f"\nDocument {i}:")
            print(f"  Length: {len(content)} chars")
            print(f"  Words: {len(content.split())}")
            print(f"  Method: {doc.metadata.get('extraction_method', 'unknown')}")
            if len(content) > 0:
                preview = content[:200].replace('\n', ' ')
                print(f"  Preview: {preview}...")
            print()
        
        # Check for empty documents
        empty_count = sum(1 for doc in documents if not doc.page_content.strip())
        print(f"Empty documents: {empty_count}/{len(documents)}")
        
        # Total content
        total_content = "\n\n".join([doc.page_content for doc in documents])
        total_chars = len(total_content)
        total_words = len(total_content.split())
        
        print(f"\nTotal extracted content: {total_chars:,} chars, {total_words:,} words")
        
        if total_chars > 1000:
            print("\n✅ SUCCESS: Docling extracted substantial content!")
            print(f"   Previous extraction: ~162 chars (mostly blank)")
            print(f"   Docling extraction: {total_chars:,} chars")
            print(f"   Improvement: {total_chars / 162:.1f}x more content")
            print("\n" + "=" * 80)
            print("PROCEEDING WITH FULL RE-EXTRACTION")
            print("=" * 80)
            print()
            
            # Import and run the re-extraction
            import subprocess
            result = subprocess.run(
                [sys.executable, str(maatlangchain_root / "enhanced_re_extract.py")],
                cwd=str(maatlangchain_root)
            )
            
            if result.returncode == 0:
                print("\n✅ Re-extraction completed successfully!")
            else:
                print("\n⚠️  Re-extraction had issues, check logs")
        else:
            print("\n⚠️  WARNING: Extracted content is still small")
            print("   May need to check PDF format or Docling configuration")
            print("   Not proceeding with full re-extraction")
    else:
        print("❌ ERROR: No documents loaded!")
        
except ImportError as e:
    print(f"\n❌ ERROR: Could not import required modules")
    print(f"   {e}")
    print("\nPlease ensure all dependencies are installed")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

