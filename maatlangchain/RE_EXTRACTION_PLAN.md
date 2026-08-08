# Re-Extraction Plan for Problematic Files

## Overview
Since source PDFs are available in `docs/RBG_Library/`, we can re-extract problematic files with enhanced OCR settings.

## Strategy

### Phase 1: Find Source PDFs
Run improved mapping script to identify which problematic files have source PDFs:
```bash
python3 map_txt_to_pdf.py
```

### Phase 2: Enhanced Re-Extraction
For files with source PDFs:
- Use **DatalabMarkerLoader** with enhanced OCR settings
- Better image preprocessing (deskew, denoise, contrast)
- Higher OCR confidence thresholds
- Quality validation during extraction

### Phase 3: Post-Process Files Without PDFs
For files without source PDFs:
- Use deduplication for repetitive files
- OCR error cleanup
- Manual review for TOO_SHORT files

## Implementation

### Step 1: Run Mapping
```bash
python3 map_txt_to_pdf.py
python3 create_re_extract_plan.py
```

### Step 2: Create Enhanced Re-Extraction Script
- Enhanced OCR preprocessing
- Quality gates
- Automatic validation
- Backup originals

### Step 3: Batch Process
- Re-extract files with PDFs
- Post-process files without PDFs
- Validate all improvements

### Step 4: Replace & Move Forward
- Replace only if quality improved
- Generate final report
- Continue with RAG ingestion

## Expected Results

Based on file naming patterns, we should find:
- Most files in `docs/RBG_Library/` match extracted filenames
- Some may need fuzzy matching due to naming differences
- A few may not have PDFs (need post-processing)

## Next Steps

1. **Run mapping** - Find source PDFs
2. **Create re-extraction script** - Enhanced OCR
3. **Batch process** - Fix all problematic files
4. **Validate** - Ensure quality improved
5. **Move forward** - Continue with RAG ingestion

