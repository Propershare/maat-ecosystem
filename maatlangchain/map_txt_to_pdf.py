#!/usr/bin/env python3
"""
Map problematic .txt files back to their source PDFs
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

# Setup paths
maatlangchain_root = Path(__file__).parent
review_folder = maatlangchain_root / "extracted_files_review"
rbg_library = maatlangchain_root / "docs" / "RBG_Library"
scan_report = maatlangchain_root / "scan_quality_report.txt"

def normalize_filename(name: str) -> str:
    """Normalize filename for matching."""
    # Remove common prefixes/suffixes
    name = name.replace('extracted_', '').replace('.txt', '').lower()
    # Normalize separators
    name = name.replace('___', '_').replace('__', '_')
    name = name.replace('~', '_').replace('-', '_')
    # Remove common suffixes
    name = name.replace('_smaller', '').replace('_1', '')
    return name.strip('_')

def find_source_pdf(txt_filename: str) -> Optional[Path]:
    """Try to find the source PDF for a txt file."""
    # Normalize the txt filename
    base_name = normalize_filename(txt_filename)
    
    # Search locations - ONLY RBG_Library (tehuti_library is off-limits)
    search_locations = []
    if rbg_library.exists():
        search_locations.append(rbg_library)
    
    # Try exact match first
    for location in search_locations:
        for pdf_file in location.rglob("*.pdf"):
            pdf_stem = normalize_filename(pdf_file.stem)
            if base_name == pdf_stem:
                return pdf_file
    
    # Try partial match (base_name is substring of PDF name)
    for location in search_locations:
        for pdf_file in location.rglob("*.pdf"):
            pdf_stem = normalize_filename(pdf_file.stem)
            # Check if base_name is contained in PDF name or vice versa
            if base_name in pdf_stem or pdf_stem in base_name:
                # Prefer longer matches
                if len(base_name) > 20 or len(pdf_stem) > 20:
                    return pdf_file
    
    # Try fuzzy match - check if significant words match
    base_words = set(base_name.split('_'))
    base_words = {w for w in base_words if len(w) > 3}  # Only meaningful words
    
    best_match = None
    best_score = 0
    
    for location in search_locations:
        for pdf_file in location.rglob("*.pdf"):
            pdf_stem = normalize_filename(pdf_file.stem)
            pdf_words = set(pdf_stem.split('_'))
            pdf_words = {w for w in pdf_words if len(w) > 3}
            
            # Calculate match score
            if base_words and pdf_words:
                common_words = base_words.intersection(pdf_words)
                score = len(common_words) / max(len(base_words), len(pdf_words))
                if score > best_score and score > 0.3:  # At least 30% word match
                    best_score = score
                    best_match = pdf_file
    
    return best_match

def parse_scan_report() -> Dict[str, List[str]]:
    """Parse the scan quality report to get problematic files."""
    problematic = {
        'HIGH_OCR_ERRORS': [],
        'HIGHLY_REPETITIVE': [],
        'TOO_SHORT': [],
    }
    
    if not scan_report.exists():
        print(f"Scan report not found: {scan_report}")
        return problematic
    
    current_category = None
    with open(scan_report, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Detect category
            if 'HIGH_OCR_ERRORS' in line:
                current_category = 'HIGH_OCR_ERRORS'
            elif 'HIGHLY_REPETITIVE' in line:
                current_category = 'HIGHLY_REPETITIVE'
            elif 'TOO_SHORT' in line:
                current_category = 'TOO_SHORT'
            
            # Extract filename
            if line.startswith('File: ') and current_category:
                filename = line.replace('File: ', '').strip()
                problematic[current_category].append(filename)
    
    return problematic

def main():
    """Main mapping function."""
    print("=" * 80)
    print("MAPPING PROBLEMATIC FILES TO SOURCE PDFs")
    print("=" * 80)
    print()
    
    # Parse scan report
    problematic = parse_scan_report()
    
    total_problematic = sum(len(files) for files in problematic.values())
    print(f"Found {total_problematic} problematic files:")
    for category, files in problematic.items():
        print(f"  {category}: {len(files)} files")
    print()
    
    # Map files to PDFs
    mapping = {}
    found_count = 0
    not_found = []
    
    for category, files in problematic.items():
        print(f"Mapping {category} files...")
        for txt_file in files:
            pdf_path = find_source_pdf(txt_file)
            if pdf_path:
                mapping[txt_file] = {
                    'category': category,
                    'pdf_path': str(pdf_path),
                    'pdf_exists': True
                }
                found_count += 1
            else:
                mapping[txt_file] = {
                    'category': category,
                    'pdf_path': None,
                    'pdf_exists': False
                }
                not_found.append(txt_file)
        
        if found_count % 20 == 0 and found_count > 0:
            print(f"  Mapped {found_count} files...")
    
    print()
    print("=" * 80)
    print("MAPPING RESULTS")
    print("=" * 80)
    print(f"Total problematic files: {total_problematic}")
    print(f"PDFs found: {found_count}")
    print(f"PDFs not found: {len(not_found)}")
    print()
    
    # Save mapping
    mapping_file = maatlangchain_root / "txt_to_pdf_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"Mapping saved to: {mapping_file}")
    print()
    
    if not_found:
        print(f"Files without source PDFs ({len(not_found)}):")
        for filename in not_found[:10]:
            print(f"  - {filename}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

