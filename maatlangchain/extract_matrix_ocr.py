#!/usr/bin/env python3
"""
Rescan Matrix-of-Power-related books with Docling OCR (word-for-word) into new text files.
"""

import os
import sys
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

# Load .env for DB connection (if needed)
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

pdfs = [
    {
        "path": maatlangchain_root / "docs" / "RBG_Library" / "M-2" / "Matrix of Power. How the World Has Been Controlled by Jordan Maxwell.pdf",
        "output": maatlangchain_root / "extracted_files_review" / "matrix_of_power._how_the_world_has_been_controlled_by_jordan_maxwell_ocr.txt",
        "label": "Matrix of Power",
    },
    {
        "path": maatlangchain_root / "docs" / "RBG_Library" / "T-2" / "The Code to the Matrix.pdf",
        "output": maatlangchain_root / "extracted_files_review" / "the_code_to_the_matrix_ocr.txt",
        "label": "The Code to the Matrix",
    },
]

print("=" * 80)
print("MATRIX BOOKS OCR RESCAN - WORD FOR WORD")
print("=" * 80)
print()

try:
    vector_store, embeddings = get_vector_store()
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=10000,
        min_chunk_size=0,
        skip_front_pages=0,
        use_ocr=True,
    )
    print("✅ Document processor initialized with OCR enabled")
    print()
except Exception as e:
    print(f"❌ ERROR initializing processor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

for info in pdfs:
    pdf_path = info["path"]
    output_path = info["output"]
    label = info["label"]

    print("=" * 80)
    print(f"PROCESSING: {label}")
    print("=" * 80)
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_path}")
    print()

    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found: {pdf_path}")
        continue

    try:
        print("Extracting with OCR (this may take a while)...")
        documents = processor.load_pdf(str(pdf_path), force_ocr=True)

        if not documents:
            print(f"❌ ERROR: No documents extracted from {pdf_path}")
            continue

        print(f"✅ Extracted {len(documents)} document chunks")

        print("Combining all chunks into single text file...")
        full_text = []

        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            if content and content.strip():
                if len(documents) > 1:
                    full_text.append(f"\n\n--- Chunk {i} (Page {doc.metadata.get('page', i)}) ---\n\n")
                full_text.append(content)

        complete_text = "\n".join(full_text) if full_text else ""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(complete_text)

        word_count = len(complete_text.split())
        char_count = len(complete_text)

        print()
        print(f"✅ SUCCESS: {label} extracted!")
        print(f"   Output file: {output_path}")
        print(f"   Total chunks: {len(documents)}")
        print(f"   Total characters: {char_count:,}")
        print(f"   Total words: {word_count:,}")
        print()

    except Exception as e:
        print(f"❌ ERROR processing {label}: {e}")
        import traceback
        traceback.print_exc()
        print()
        continue

print("=" * 80)
print("MATRIX BOOKS OCR RESCAN COMPLETE")
print("=" * 80)
