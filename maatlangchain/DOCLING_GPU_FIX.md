# Docling GPU Memory Fix

## Problem
CUDA out of memory errors when processing PDFs:
- GPU has 11.75 GiB total
- Only 5.38 MiB free
- Multiple processes using GPU memory

## Solution Applied

Updated `document_processor.py` to:
1. **Force CPU usage** - Set `CUDA_VISIBLE_DEVICES=""` before Docling processing
2. **Disable expensive features** - Turn off table structure detection to save memory
3. **Restore CUDA setting** - After processing, restore original CUDA configuration

## Changes Made

- Docling now runs on CPU instead of GPU
- Table structure detection disabled (saves memory)
- CUDA environment variable managed properly

## Trade-offs

- **Slower processing** - CPU is slower than GPU (but avoids crashes)
- **More reliable** - No memory errors
- **Still extracts content** - OCR works on CPU too

## If Still Having Issues

1. **Clear GPU memory** - Kill other processes using GPU
2. **Process files in smaller batches** - Modify `enhanced_re_extract.py` to process 10 files at a time
3. **Use PyPDFLoader fallback** - For text-based PDFs, disable OCR

