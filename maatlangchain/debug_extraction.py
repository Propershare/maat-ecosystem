#!/usr/bin/env python3
"""
Debug script to see what's actually being extracted from PDFs
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

# Test with a problematic PDF
test_pdf = maatlangchain_root / "docs" / "RBG_Library" / "R-2" / "Ra-Un-Nefer-Amen- The 11 Laws of Ma'at.pdf"

if not test_pdf.exists():
    print(f"Test PDF not found: {test_pdf}")
    sys.exit(1)

print("=" * 80)
print("DEBUGGING PDF EXTRACTION")
print("=" * 80)
print(f"PDF: {test_pdf}")
print()

vector_store, embeddings = get_vector_store()

# Test with OCR enabled
print("Testing with OCR enabled...")
processor = DocumentProcessor(
    embeddings=embeddings,
    vector_store=vector_store,
    max_chunk_size=2500,
    min_chunk_size=200,
    skip_front_pages=0,
    use_ocr=True,
)

documents = processor.load_pdf(str(test_pdf))

print(f"\nLoaded {len(documents)} documents")
print()

if documents:
    print("First 5 documents:")
    for i, doc in enumerate(documents[:5], 1):
        content = doc.page_content
        print(f"\nDocument {i}:")
        print(f"  Length: {len(content)} chars")
        print(f"  Metadata: {doc.metadata}")
        print(f"  Content preview (first 200 chars):")
        print(f"  {repr(content[:200])}")
        print()
    
    # Check for empty documents
    empty_count = sum(1 for doc in documents if not doc.page_content.strip())
    print(f"\nEmpty documents: {empty_count}/{len(documents)}")
    
    # Total content
    total_content = "\n\n".join([doc.page_content for doc in documents])
    print(f"\nTotal extracted content: {len(total_content)} chars")
    print(f"Total words: {len(total_content.split())}")
else:
    print("No documents loaded!")

# Test with OCR disabled (PyPDFLoader only)
print("\n" + "=" * 80)
print("Testing with OCR disabled (PyPDFLoader only)...")
print("=" * 80)

processor2 = DocumentProcessor(
    embeddings=embeddings,
    vector_store=vector_store,
    max_chunk_size=2500,
    min_chunk_size=200,
    skip_front_pages=0,
    use_ocr=False,
)

documents2 = processor2.load_pdf(str(test_pdf))

print(f"\nLoaded {len(documents2)} documents")
print()

if documents2:
    print("First 5 documents:")
    for i, doc in enumerate(documents2[:5], 1):
        content = doc.page_content
        print(f"\nDocument {i}:")
        print(f"  Length: {len(content)} chars")
        print(f"  Metadata: {doc.metadata}")
        print(f"  Content preview (first 200 chars):")
        print(f"  {repr(content[:200])}")
        print()
    
    # Check for empty documents
    empty_count2 = sum(1 for doc in documents2 if not doc.page_content.strip())
    print(f"\nEmpty documents: {empty_count2}/{len(documents2)}")
    
    # Total content
    total_content2 = "\n\n".join([doc.page_content for doc in documents2])
    print(f"\nTotal extracted content: {len(total_content2)} chars")
    print(f"Total words: {len(total_content2.split())}")
else:
    print("No documents loaded!")

