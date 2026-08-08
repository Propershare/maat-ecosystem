#!/usr/bin/env python3
"""
Remove duplicate content from highly repetitive files
"""

import json
from pathlib import Path
from typing import List, Set
from collections import Counter

# Setup paths
maatlangchain_root = Path(__file__).parent
review_folder = maatlangchain_root / "extracted_files_review"
scan_report = maatlangchain_root / "scan_quality_report.txt"

def get_repetitive_files() -> List[str]:
    """Get list of highly repetitive files from scan report."""
    repetitive_files = []
    
    if not scan_report.exists():
        return repetitive_files
    
    in_repetitive_section = False
    with open(scan_report, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if 'HIGHLY_REPETITIVE' in line:
                in_repetitive_section = True
                continue
            elif line.startswith('---') and in_repetitive_section:
                continue
            elif line.startswith('HIGH_OCR_ERRORS') or line.startswith('TOO_SHORT'):
                in_repetitive_section = False
                continue
            
            if in_repetitive_section and line.startswith('File: '):
                filename = line.replace('File: ', '').strip()
                repetitive_files.append(filename)
    
    return repetitive_files

def deduplicate_file(file_path: Path) -> tuple[str, int, int]:
    """
    Remove duplicate lines from a file.
    Returns: (deduplicated_content, original_lines, unique_lines)
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    original_count = len(lines)
    
    # Method 1: Remove exact duplicate lines
    seen_lines: Set[str] = set()
    unique_lines = []
    duplicate_count = 0
    
    for line in lines:
        # Normalize line (strip whitespace for comparison)
        normalized = line.strip()
        
        # Skip empty lines in duplicate check
        if not normalized:
            unique_lines.append(line)
            continue
        
        # Check if we've seen this line before
        if normalized not in seen_lines:
            seen_lines.add(normalized)
            unique_lines.append(line)
        else:
            duplicate_count += 1
    
    # Method 2: If still too repetitive, remove duplicate paragraphs
    if duplicate_count / original_count > 0.3:
        # Group into paragraphs (lines separated by blank lines)
        paragraphs = []
        current_para = []
        
        for line in unique_lines:
            if line.strip():
                current_para.append(line)
            else:
                if current_para:
                    paragraphs.append(''.join(current_para))
                    current_para = []
                paragraphs.append(line)  # Keep blank lines
        
        if current_para:
            paragraphs.append(''.join(current_para))
        
        # Remove duplicate paragraphs
        seen_paras: Set[str] = set()
        unique_paras = []
        
        for para in paragraphs:
            normalized_para = para.strip()
            if not normalized_para or normalized_para not in seen_paras:
                seen_paras.add(normalized_para)
                unique_paras.append(para)
        
        unique_lines = unique_paras
    
    deduplicated_content = ''.join(unique_lines)
    unique_count = len([l for l in unique_lines if l.strip()])
    
    return deduplicated_content, original_count, unique_count

def main():
    """Main deduplication function."""
    print("=" * 80)
    print("DEDUPLICATING REPETITIVE FILES")
    print("=" * 80)
    print()
    
    # Get repetitive files
    repetitive_files = get_repetitive_files()
    
    if not repetitive_files:
        print("No repetitive files found in scan report!")
        return
    
    print(f"Found {len(repetitive_files)} repetitive files to process")
    print()
    
    results = []
    processed = 0
    errors = []
    
    for filename in repetitive_files:
        file_path = review_folder / filename
        
        if not file_path.exists():
            errors.append((filename, "File not found"))
            continue
        
        try:
            print(f"Processing: {filename}")
            deduplicated, original_lines, unique_lines = deduplicate_file(file_path)
            
            # Calculate improvement
            reduction = ((original_lines - unique_lines) / original_lines * 100) if original_lines > 0 else 0
            
            # Only save if we removed significant duplicates
            if reduction > 10:  # At least 10% reduction
                # Backup original
                backup_path = file_path.with_suffix('.txt.backup')
                if not backup_path.exists():
                    file_path.rename(backup_path)
                
                # Write deduplicated version
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(deduplicated)
                
                results.append({
                    'file': filename,
                    'original_lines': original_lines,
                    'unique_lines': unique_lines,
                    'reduction': f"{reduction:.1f}%",
                    'status': 'DEDUPLICATED'
                })
                processed += 1
                print(f"  ✓ Removed {reduction:.1f}% duplicates ({original_lines} → {unique_lines} lines)")
            else:
                results.append({
                    'file': filename,
                    'original_lines': original_lines,
                    'unique_lines': unique_lines,
                    'reduction': f"{reduction:.1f}%",
                    'status': 'MINIMAL_DUPLICATES'
                })
                print(f"  - Minimal duplicates ({reduction:.1f}% reduction)")
                
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(repetitive_files)}")
    print(f"Successfully deduplicated: {processed}")
    print(f"Errors: {len(errors)}")
    print()
    
    # Save results
    results_file = maatlangchain_root / "deduplication_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for filename, error in errors[:5]:
            print(f"  - {filename}: {error}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

