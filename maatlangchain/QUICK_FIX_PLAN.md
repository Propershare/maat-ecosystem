# Quick Fix Plan - Work with What We Have

## Situation
- 147 problematic files (27% of total)
- 0 source PDFs found (PDFs may have been moved/deleted after extraction)
- Need to move forward quickly

## Strategy: Post-Process Extracted Text Files

Since we can't re-extract from PDFs, we'll fix the extracted `.txt` files directly:

### Phase 1: Fix Repetitive Content (25 files)
**Automated deduplication** - Remove duplicate lines/sections
- Fast and effective
- Can recover significant content

### Phase 2: Improve OCR Error Files (119 files)  
**Post-processing cleanup**:
- Fix common OCR errors (character substitutions)
- Remove excessive special characters
- Clean up formatting

### Phase 3: Expand Short Files (3 files)
**Manual review** - Only 3 files, quick check

## Implementation

### Option A: Automated Fix (Recommended)
1. **Deduplicate repetitive files** - Remove duplicate content
2. **Clean OCR errors** - Fix common character mistakes
3. **Validate improvements** - Check if quality improved
4. **Replace originals** - Only if better

**Time: 1-2 hours automated**

### Option B: Accept & Move On
- Use the 405 good quality files (73%)
- Flag problematic files for later
- Move forward with RAG ingestion

**Time: Immediate**

## Recommended: Option A

### Benefits:
- Improves 147 files without needing source PDFs
- Automated - runs without manual intervention
- Can recover significant content from repetitive files
- Quick validation to ensure improvements

### Scripts Needed:
1. `deduplicate_repetitive.py` - Remove duplicate lines/sections
2. `clean_ocr_errors.py` - Fix common OCR mistakes
3. `validate_fixes.py` - Check if quality improved
4. `apply_fixes.py` - Orchestrate the process

## Next Steps

1. Run improved mapping (check if any PDFs found)
2. Create deduplication script for repetitive files
3. Create OCR cleanup script
4. Run batch fix
5. Validate and move forward

