# Plan to Fix Poor Quality Scans

## Current Status
- **Total files**: 552
- **Good quality**: 405 (73%)
- **Poor quality**: 147 (27%)

### Breakdown of Issues:
1. **HIGH_OCR_ERRORS**: 119 files (81% of problems)
2. **HIGHLY_REPETITIVE**: 25 files (17% of problems) 
3. **TOO_SHORT**: 3 files (2% of problems)

## Strategy

### Phase 1: Identify Source PDFs
- Map problematic `.txt` files back to their source PDFs
- Create a list of PDFs that need re-extraction
- Check if source PDFs still exist

### Phase 2: Re-extraction with Enhanced OCR
- Use improved OCR settings:
  - Higher resolution preprocessing
  - Better OCR engine configuration
  - Quality validation during extraction
- Batch process problematic files
- Validate output before replacing

### Phase 3: Fix Repetitive Content
- For HIGHLY_REPETITIVE files:
  - Detect and remove duplicate lines/sections
  - Use deduplication algorithms
  - Manual review for critical files

### Phase 4: Validation & Replacement
- Run quality check on fixed files
- Replace original files only if quality improved
- Keep backups of originals

## Implementation Options

### Option A: Quick Fix (Recommended)
**Focus on HIGH_OCR_ERRORS (119 files) - these are the majority**

1. **Re-extract with better OCR settings**
   - Use DatalabMarkerLoader with enhanced preprocessing
   - Increase OCR confidence thresholds
   - Better image preprocessing (deskew, denoise)

2. **Automated deduplication for repetitive files**
   - Remove duplicate lines/sections
   - Keep unique content only

3. **Manual review for TOO_SHORT files (only 3 files)**
   - Quick manual check if source PDFs exist
   - Re-extract if needed

**Time estimate**: 2-4 hours automated processing

### Option B: Comprehensive Fix
**Fix all 147 files systematically**

1. Create mapping: txt → source PDF
2. Batch re-extract all problematic PDFs
3. Apply deduplication to repetitive files
4. Validate all fixes
5. Replace originals

**Time estimate**: 4-8 hours

### Option C: Skip & Move On
**Accept current quality, focus on good files**

- Use the 405 good quality files
- Flag problematic files for later
- Move forward with RAG ingestion of good files

**Time estimate**: Immediate

## Recommended Approach: Option A

### Step 1: Create File Mapping
```python
# Map problematic .txt files to source PDFs
# Check if source PDFs exist in tehuti_library
```

### Step 2: Enhanced Re-extraction Script
```python
# Re-extract with:
# - Better OCR preprocessing
# - Quality gates during extraction
# - Automatic deduplication
```

### Step 3: Batch Process
```python
# Process all 119 HIGH_OCR_ERRORS files
# Process all 25 HIGHLY_REPETITIVE files (with dedup)
# Process 3 TOO_SHORT files manually
```

### Step 4: Validate & Replace
```python
# Run quality check on fixed files
# Only replace if quality improved
# Generate final report
```

## Next Steps

1. **Create file mapping script** - Map txt → PDF sources
2. **Create enhanced extraction script** - Better OCR + deduplication
3. **Run batch fix** - Process all problematic files
4. **Validate results** - Ensure quality improved
5. **Move forward** - Continue with RAG ingestion

## Files to Create

1. `map_txt_to_pdf.py` - Find source PDFs for problematic files
2. `enhanced_re_extract.py` - Re-extract with better OCR
3. `deduplicate_repetitive.py` - Fix repetitive content
4. `batch_fix_scans.py` - Orchestrate the fix process

