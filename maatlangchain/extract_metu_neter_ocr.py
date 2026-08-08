#!/usr/bin/env python3
"""
Extract Metu Neter Volumes 1-3 word-for-word using OCR (Docling)
Preserves all text exactly as it appears in the PDFs.
"""

import os
import sys
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

# Load .env for database connection (if needed)
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

# Define PDF paths
pdfs = [
    {
        "path": maatlangchain_root / "docs" / "RBG_Library" / "M-2" / "Metu Neter Volume 1 by Ra Un Amen Nefer smaller.pdf",
        "output": maatlangchain_root / "extracted_files_review" / "metu_neter_volume_1_by_ra_un_amen_nefer_ocr.txt",
        "volume": 1
    },
    {
        "path": maatlangchain_root / "docs" / "RBG_Library" / "M-3" / "Metu Neter Volume 2  by Ra Un Amen Nefer SMALLER.pdf",
        "output": maatlangchain_root / "extracted_files_review" / "metu_neter_volume_2_by_ra_un_amen_nefer_ocr.txt",
        "volume": 2
    },
    {
        "path": maatlangchain_root / "docs" / "RBG_Library" / "M-3" / "Metu Neter Volume 3 by Ra Un Amen Nefer.pdf",
        "output": maatlangchain_root / "extracted_files_review" / "metu_neter_volume_3_by_ra_un_amen_nefer_ocr.txt",
        "volume": 3
    }
]

print("=" * 80)
print("METU NETER OCR EXTRACTION - WORD FOR WORD")
print("=" * 80)
print()

# Initialize processor with OCR enabled
try:
    vector_store, embeddings = get_vector_store()
    
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=10000,  # Large chunks to preserve full text
        min_chunk_size=0,  # Keep all content
        skip_front_pages=0,  # Don't skip any pages
        use_ocr=True,  # Enable OCR for word-for-word extraction
    )
    
    print("✅ Document processor initialized with OCR enabled")
    print()
    
except Exception as e:
    print(f"❌ ERROR initializing processor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Process each PDF
for pdf_info in pdfs:
    pdf_path = pdf_info["path"]
    output_path = pdf_info["output"]
    volume = pdf_info["volume"]
    
    print("=" * 80)
    print(f"PROCESSING VOLUME {volume}")
    print("=" * 80)
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_path}")
    print()
    
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found: {pdf_path}")
        continue
    
    try:
        # Extract with OCR
        print("Extracting with OCR (this may take a while)...")
        documents = processor.load_pdf(str(pdf_path), force_ocr=True)
        
        if not documents:
            print(f"❌ ERROR: No documents extracted from {pdf_path}")
            continue
        
        print(f"✅ Extracted {len(documents)} document chunks")
        
        # Combine all documents into single text file (word-for-word)
        print("Combining all chunks into single text file...")
        full_text = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            if content and content.strip():
                # Add page/chunk separator if multiple chunks
                if len(documents) > 1:
                    full_text.append(f"\n\n--- Chunk {i} (Page {doc.metadata.get('page', i)}) ---\n\n")
                full_text.append(content)
        
        # Join all text
        complete_text = "\n".join(full_text) if full_text else ""
        
        # Write to output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(complete_text)
        
        # Statistics
        word_count = len(complete_text.split())
        char_count = len(complete_text)
        
        print()
        print(f"✅ SUCCESS: Volume {volume} extracted!")
        print(f"   Output file: {output_path}")
        print(f"   Total chunks: {len(documents)}")
        print(f"   Total characters: {char_count:,}")
        print(f"   Total words: {word_count:,}")
        print()
        
    except Exception as e:
        print(f"❌ ERROR processing Volume {volume}: {e}")
        import traceback
        traceback.print_exc()
        print()
        continue

print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print("All extracted files saved to: extracted_files_review/")
print()

