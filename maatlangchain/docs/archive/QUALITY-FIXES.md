# PDF Extraction Quality Fixes

**Date:** 2025-12-20  
**Maat Alignment:** Truth (quality verification), Balance (filter noise), Order (better chunking)

## Problems Identified

1. **Only 10 chunks stored** - Processing was interrupted
2. **Poor quality chunks** - Some chunks only have 2 words or copyright statements
3. **Front matter included** - Title pages, copyright, TOC being chunked

## Solutions Implemented

### 1. Quality Filtering
- **Minimum chunk size:** 200 characters (configurable)
- **Copyright detection:** Filters chunks with 3+ copyright phrases
- **Whitespace filtering:** Removes chunks that are mostly whitespace
- **Page number filtering:** Removes chunks that are just page numbers

### 2. Front Matter Filtering
- **Skip first N pages:** Default 5 pages (title, copyright, TOC)
- **Configurable:** Can adjust with `--skip-front-pages` flag

### 3. Better Chunking
- **Adaptive chunk sizes:** Based on document size
- **Large PDFs (>500 pages):** 2500 chars, 400 overlap
- **Medium PDFs (100-500 pages):** 2000 chars, 300 overlap
- **Small PDFs (<100 pages):** 1000 chars, 200 overlap

## Usage

### Re-process with Quality Filtering

```bash
cd /home/suspect/.n8n/maatlangchain

# Re-process with defaults (skip 5 front pages, min 200 chars)
python3 scripts/reprocess_pdf_quality.py

# Custom settings
python3 scripts/reprocess_pdf_quality.py \
    --min-chunk-size 300 \
    --skip-front-pages 10
```

## What Changed

### DocumentProcessor Class
- Added `min_chunk_size` parameter (default: 200)
- Added `skip_front_pages` parameter (default: 5)
- Added `is_low_quality_chunk()` method
- Added `filter_front_matter()` method
- Updated `process_documents()` to filter before chunking

### Quality Checks
- Minimum length check
- Whitespace ratio check
- Copyright phrase detection
- Page number detection

## Expected Results

**Before:**
- 10 chunks (interrupted)
- Many chunks with 2 words or copyright
- Front matter included

**After:**
- All ~5800 chunks processed
- No chunks < 200 characters
- No copyright/TOC pages
- Better quality content

## Verification

After re-processing, check quality:

```bash
python3 scripts/check_extraction_quality.py --pdf-name "Africa and the Americas.pdf"
```

Should show:
- More chunks (thousands, not 10)
- Better average chunk length
- No short chunks (< 200 chars)
- No copyright pages

