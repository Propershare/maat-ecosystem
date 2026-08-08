# Batch Fix Plan for 147 Problematic Files

## Mapping Results
- **Total problematic files**: 147
- **Files with source PDFs**: 87 (59%) - Can re-extract
- **Files without PDFs**: 60 (41%) - Need post-processing

## Strategy

### Phase 1: Re-Extract Files with PDFs (87 files)
**Use enhanced OCR re-extraction:**
```bash
python3 enhanced_re_extract.py
```

**What it does:**
- Re-extracts from source PDFs in `docs/RBG_Library/`
- Uses enhanced OCR settings (DatalabMarkerLoader)
- Saves to `re_extracted_files/` folder
- Creates backups before replacing

### Phase 2: Post-Process Files Without PDFs (60 files)
**Use deduplication and OCR cleanup:**
```bash
python3 deduplicate_repetitive.py  # For repetitive files
# Create OCR cleanup script for error files
```

### Phase 3: Validate & Replace
**Quality check and replacement:**
- Run quality analysis on fixed files
- Compare before/after quality
- Replace originals only if improved
- Generate final report

## Execution Order

1. **Re-extract 87 files with PDFs** (1-2 hours)
   ```bash
   python3 enhanced_re_extract.py
   ```

2. **Fix repetitive files** (30 min)
   ```bash
   python3 deduplicate_repetitive.py
   ```

3. **Clean OCR errors** (1 hour)
   - Create OCR cleanup script
   - Process 60 files without PDFs

4. **Validate all fixes** (30 min)
   - Run quality check
   - Compare improvements
   - Replace if better

5. **Move forward** - Continue with RAG ingestion

## Expected Outcome

- **87 files**: Re-extracted with better OCR quality
- **25 repetitive files**: Deduplicated (remove duplicates)
- **60 files without PDFs**: Post-processed (OCR cleanup)
- **3 TOO_SHORT files**: Manual review

**Total time**: 3-4 hours automated processing

## Next Steps

1. Run re-extraction for 87 files with PDFs
2. Run deduplication for repetitive files
3. Create OCR cleanup for remaining files
4. Validate and replace
5. Move forward with RAG ingestion

