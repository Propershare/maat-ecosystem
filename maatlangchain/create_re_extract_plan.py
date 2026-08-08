#!/usr/bin/env python3
"""
Create a plan for re-extracting problematic files from source PDFs
"""

import json
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
mapping_file = maatlangchain_root / "txt_to_pdf_mapping.json"

if not mapping_file.exists():
    print("Error: Mapping file not found. Run map_txt_to_pdf.py first!")
    exit(1)

# Load mapping
with open(mapping_file, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Categorize
files_with_pdfs = []
files_without_pdfs = []

for txt_file, info in mapping.items():
    if info.get('pdf_exists'):
        files_with_pdfs.append({
            'txt_file': txt_file,
            'pdf_path': info['pdf_path'],
            'category': info['category']
        })
    else:
        files_without_pdfs.append(txt_file)

print("=" * 80)
print("RE-EXTRACTION PLAN")
print("=" * 80)
print()
print(f"Total problematic files: {len(mapping)}")
print(f"Files with source PDFs: {len(files_with_pdfs)}")
print(f"Files without source PDFs: {len(files_without_pdfs)}")
print()

if files_with_pdfs:
    print("FILES READY FOR RE-EXTRACTION:")
    print("-" * 80)
    
    by_category = {}
    for item in files_with_pdfs:
        cat = item['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    for category, items in sorted(by_category.items()):
        print(f"\n{category} ({len(items)} files with PDFs):")
        for item in items[:5]:
            print(f"  - {item['txt_file']}")
            print(f"    PDF: {item['pdf_path']}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    
    # Save re-extraction list
    re_extract_file = maatlangchain_root / "re_extract_list.json"
    with open(re_extract_file, 'w', encoding='utf-8') as f:
        json.dump(files_with_pdfs, f, indent=2)
    
    print()
    print(f"Re-extraction list saved to: {re_extract_file}")
    print()
    print("NEXT STEPS:")
    print("1. Create enhanced re-extraction script")
    print("2. Process files with source PDFs")
    print("3. For files without PDFs, use post-processing (deduplication/OCR cleanup)")

if files_without_pdfs:
    print()
    print(f"FILES WITHOUT SOURCE PDFs ({len(files_without_pdfs)}):")
    print("These will need post-processing (deduplication/OCR cleanup)")
    print("-" * 80)
    for filename in files_without_pdfs[:10]:
        print(f"  - {filename}")
    if len(files_without_pdfs) > 10:
        print(f"  ... and {len(files_without_pdfs) - 10} more")

print()
print("=" * 80)

