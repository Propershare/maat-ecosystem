# Quick Docling Test & Re-Extraction

## Step 1: Install Docling

```bash
cd /home/suspect/.n8n/maatlangchain
pip install docling
```

Or use the automated script:
```bash
bash RUN_DOCLING_TEST.sh
```

## Step 2: Test Extraction

```bash
python3 install_and_test_docling.py
```

This will:
- Install Docling (if not already installed)
- Test extraction on a problematic PDF
- Show content comparison (old vs new)

## Step 3: Re-Run Extraction (if test succeeds)

```bash
python3 enhanced_re_extract.py
```

This will re-extract all 87 files using Docling.

## Expected Results

**Before (DatalabMarkerLoader)**:
- Most files: ~162 chars (blank)
- Files saved but empty

**After (Docling)**:
- Should extract thousands of chars
- Actual readable content
- Better OCR quality

## Verification

After re-extraction, check a few files:
```bash
# Check file size
ls -lh re_extracted_files/metu_neter_volume_1_by_ra_un_amen_nefer_smaller.txt

# View content
head -50 re_extracted_files/metu_neter_volume_1_by_ra_un_amen_nefer_smaller.txt
```

If files have substantial content (>1000 chars), the fix worked!

