#!/usr/bin/env python3
"""
Analyze extracted files to identify which ones didn't scan properly
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Setup paths
maatlangchain_root = Path(__file__).parent
review_folder = maatlangchain_root / "extracted_files_review"

if not review_folder.exists():
    print(f"Error: Folder {review_folder} does not exist!")
    exit(1)

# Quality thresholds
MIN_FILE_SIZE = 500  # Minimum characters for a valid scan
MIN_WORDS = 50  # Minimum words for a valid scan
MAX_OCR_ERROR_RATIO = 0.3  # Max ratio of suspicious OCR patterns

# Common OCR error patterns
OCR_ERROR_PATTERNS = [
    r'[^\w\s]{3,}',  # Multiple consecutive special chars
    r'\b\w{1}\b',  # Single character words (often OCR errors)
    r'[a-z][A-Z][a-z]',  # Mixed case in middle of word
    r'\d{10,}',  # Very long number sequences (often OCR artifacts)
]

def analyze_file(file_path: Path) -> Dict:
    """Analyze a single file for scan quality."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_size = len(content)
        word_count = len(content.split())
        
        # Check for empty or very short files
        if file_size < MIN_FILE_SIZE:
            return {
                'file': file_path.name,
                'status': 'TOO_SHORT',
                'size': file_size,
                'words': word_count,
                'reason': f'File too short ({file_size} chars, minimum {MIN_FILE_SIZE})'
            }
        
        if word_count < MIN_WORDS:
            return {
                'file': file_path.name,
                'status': 'TOO_FEW_WORDS',
                'size': file_size,
                'words': word_count,
                'reason': f'Too few words ({word_count} words, minimum {MIN_WORDS})'
            }
        
        # Check for OCR error patterns
        error_count = 0
        for pattern in OCR_ERROR_PATTERNS:
            matches = re.findall(pattern, content)
            error_count += len(matches)
        
        error_ratio = error_count / max(word_count, 1)
        
        if error_ratio > MAX_OCR_ERROR_RATIO:
            return {
                'file': file_path.name,
                'status': 'HIGH_OCR_ERRORS',
                'size': file_size,
                'words': word_count,
                'error_ratio': error_ratio,
                'reason': f'High OCR error ratio ({error_ratio:.2%}, max {MAX_OCR_ERROR_RATIO:.2%})'
            }
        
        # Check for mostly whitespace or special characters
        alphanumeric_ratio = len(re.findall(r'[a-zA-Z0-9]', content)) / max(file_size, 1)
        if alphanumeric_ratio < 0.3:
            return {
                'file': file_path.name,
                'status': 'LOW_TEXT_CONTENT',
                'size': file_size,
                'words': word_count,
                'alphanumeric_ratio': alphanumeric_ratio,
                'reason': f'Low text content ({alphanumeric_ratio:.2%} alphanumeric)'
            }
        
        # Check for very repetitive content (likely OCR stuck)
        lines = content.split('\n')
        if len(lines) > 10:
            unique_lines = len(set(lines))
            repetition_ratio = 1 - (unique_lines / len(lines))
            if repetition_ratio > 0.5:
                return {
                    'file': file_path.name,
                    'status': 'HIGHLY_REPETITIVE',
                    'size': file_size,
                    'words': word_count,
                    'repetition_ratio': repetition_ratio,
                    'reason': f'Highly repetitive content ({repetition_ratio:.2%} repetition)'
                }
        
        # File appears to be good quality
        return {
            'file': file_path.name,
            'status': 'GOOD',
            'size': file_size,
            'words': word_count,
            'reason': 'Quality scan'
        }
        
    except Exception as e:
        return {
            'file': file_path.name,
            'status': 'ERROR',
            'reason': f'Error reading file: {str(e)}'
        }

def main():
    """Main analysis function."""
    print("=" * 80)
    print("SCAN QUALITY ANALYSIS")
    print("=" * 80)
    print(f"Analyzing files in: {review_folder}")
    print()
    
    # Get all .txt files
    files = list(review_folder.glob("*.txt"))
    
    if not files:
        print("No .txt files found in review folder!")
        return
    
    print(f"Found {len(files)} files to analyze")
    print()
    
    results = []
    for i, file_path in enumerate(files, 1):
        if i % 50 == 0:
            print(f"  Analyzing {i}/{len(files)} files...")
        result = analyze_file(file_path)
        results.append(result)
    
    print()
    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    # Categorize results
    good_files = [r for r in results if r['status'] == 'GOOD']
    bad_files = [r for r in results if r['status'] != 'GOOD']
    
    # Group bad files by status
    by_status = {}
    for result in bad_files:
        status = result['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(result)
    
    print(f"Total files analyzed: {len(results)}")
    print(f"✓ Good quality scans: {len(good_files)}")
    print(f"✗ Poor quality scans: {len(bad_files)}")
    print()
    
    if bad_files:
        print("POOR QUALITY SCANS BY CATEGORY:")
        print("-" * 80)
        
        for status, files in sorted(by_status.items()):
            print(f"\n{status} ({len(files)} files):")
            for result in files[:10]:  # Show first 10 of each category
                print(f"  - {result['file']}")
                print(f"    Reason: {result['reason']}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
        
        print()
        print("=" * 80)
        print("DETAILED REPORT")
        print("=" * 80)
        
        # Save detailed report
        report_file = maatlangchain_root / "scan_quality_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("SCAN QUALITY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total files: {len(results)}\n")
            f.write(f"Good quality: {len(good_files)}\n")
            f.write(f"Poor quality: {len(bad_files)}\n\n")
            
            f.write("POOR QUALITY FILES:\n")
            f.write("-" * 80 + "\n\n")
            
            for status, files in sorted(by_status.items()):
                f.write(f"\n{status} ({len(files)} files):\n")
                f.write("-" * 40 + "\n")
                for result in files:
                    f.write(f"\nFile: {result['file']}\n")
                    f.write(f"Reason: {result['reason']}\n")
                    if 'size' in result:
                        f.write(f"Size: {result['size']} chars\n")
                    if 'words' in result:
                        f.write(f"Words: {result['words']}\n")
        
        print(f"Detailed report saved to: {report_file}")
        print()
        print(f"Summary: {len(bad_files)} files need rescanning")
    else:
        print("✓ All files appear to be good quality scans!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

