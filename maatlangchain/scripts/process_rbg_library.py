#!/usr/bin/env python3
"""
Batch Process RBG Library PDFs
Extracts content from all PDFs in RBG library and ingests into RAG system.
Creates monitoring output for testing.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add maatlangchain to path
maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))

from api.main import get_vector_store, get_rag_instance
from core.chains.document_processor import DocumentProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Output directory for monitoring
OUTPUT_DIR = maatlangchain_root / "rbg_processing_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# RBG Library locations to check
RBG_LOCATIONS = [
    Path("/home/suspect/.n8n/maatlangchain/docs/RBG_Library"),  # RBG Library
]


def find_pdfs(base_path: Path) -> List[Path]:
    """Find all PDF files recursively."""
    pdfs = []
    if base_path.exists() and base_path.is_dir():
        pdfs = list(base_path.rglob("*.pdf"))
        pdfs.extend(list(base_path.rglob("*.PDF")))
    return pdfs


def detect_pdf_type(pdf_path: Path) -> str:
    """
    Simple detection: try PyPDF first, if fails or returns little text, use OCR.
    This is a heuristic - in production, you'd want more sophisticated detection.
    """
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        
        # Check if we got meaningful text
        total_text = sum(len(doc.page_content) for doc in docs)
        avg_text_per_page = total_text / len(docs) if docs else 0
        
        # If average text per page is very low, likely scanned PDF
        if avg_text_per_page < 100:
            return "scanned"  # Needs OCR
        return "text"  # Text-based, no OCR needed
    except Exception as e:
        log.warning(f"Could not detect PDF type for {pdf_path}: {e}, defaulting to OCR")
        return "scanned"


def process_pdf(pdf_path: Path, use_ocr: bool = False) -> Dict[str, Any]:
    """Process a single PDF and return results."""
    result = {
        "pdf_path": str(pdf_path),
        "pdf_name": pdf_path.name,
        "status": "pending",
        "use_ocr": use_ocr,
        "pages_loaded": 0,
        "chunks_created": 0,
        "processing_time": 0.0,
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }
    
    start_time = datetime.now()
    
    try:
        # Get vector store and embeddings
        vector_store, embeddings = get_vector_store()
        
        # Create processor
        processor = DocumentProcessor(
            embeddings=embeddings,
            vector_store=vector_store,
            max_chunk_size=2500,
            min_chunk_size=200,
            skip_front_pages=5,
            use_ocr=use_ocr,
        )
        
        # Load PDF
        documents = processor.load_pdf(str(pdf_path), force_ocr=use_ocr)
        
        if not documents:
            result["status"] = "error"
            result["error"] = "No documents loaded"
            return result
        
        result["pages_loaded"] = len(documents)
        
        # Process documents
        collection_name = f"rbg_{pdf_path.stem.lower().replace(' ', '_')}"
        success = processor.process_documents(documents, collection_name)
        
        if success:
            # Count chunks (approximate from document count)
            result["chunks_created"] = len(documents)  # Approximate
            result["status"] = "success"
            result["collection_name"] = collection_name
        else:
            result["status"] = "error"
            result["error"] = "Failed to process documents"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        log.error(f"Error processing {pdf_path}: {e}", exc_info=True)
    
    finally:
        processing_time = (datetime.now() - start_time).total_seconds()
        result["processing_time"] = processing_time
    
    return result


def main():
    """Main processing function."""
    log.info("=" * 80)
    log.info("RBG Library PDF Processing")
    log.info("=" * 80)
    
    # Find all PDFs
    all_pdfs = []
    for location in RBG_LOCATIONS:
        pdfs = find_pdfs(location)
        if pdfs:
            log.info(f"Found {len(pdfs)} PDFs in {location}")
            all_pdfs.extend(pdfs)
    
    if not all_pdfs:
        log.warning("No PDFs found in any RBG library location")
        log.info(f"Searched locations: {RBG_LOCATIONS}")
        return
    
    log.info(f"Total PDFs to process: {len(all_pdfs)}")
    
    # Processing results
    results = []
    summary = {
        "total_pdfs": len(all_pdfs),
        "processed": 0,
        "success": 0,
        "errors": 0,
        "with_ocr": 0,
        "without_ocr": 0,
        "start_time": datetime.now().isoformat(),
    }
    
    # Process each PDF
    for i, pdf_path in enumerate(all_pdfs, 1):
        log.info(f"\n[{i}/{len(all_pdfs)}] Processing: {pdf_path.name}")
        
        # Detect PDF type
        pdf_type = detect_pdf_type(pdf_path)
        use_ocr = (pdf_type == "scanned")
        
        if use_ocr:
            summary["with_ocr"] += 1
            log.info(f"  Detected: Scanned PDF - Using OCR")
        else:
            summary["without_ocr"] += 1
            log.info(f"  Detected: Text PDF - Using PyPDFLoader")
        
        # Process PDF
        result = process_pdf(pdf_path, use_ocr=use_ocr)
        results.append(result)
        summary["processed"] += 1
        
        if result["status"] == "success":
            summary["success"] += 1
            log.info(f"  ✓ Success: {result['pages_loaded']} pages, {result['chunks_created']} chunks")
        else:
            summary["errors"] += 1
            log.error(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    
    # Finalize summary
    summary["end_time"] = datetime.now().isoformat()
    summary["total_processing_time"] = (
        datetime.fromisoformat(summary["end_time"]) - 
        datetime.fromisoformat(summary["start_time"])
    ).total_seconds()
    
    # Save results
    output_file = OUTPUT_DIR / f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": summary,
            "results": results
        }, f, indent=2)
    
    # Save summary
    summary_file = OUTPUT_DIR / "latest_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    log.info("\n" + "=" * 80)
    log.info("PROCESSING SUMMARY")
    log.info("=" * 80)
    log.info(f"Total PDFs: {summary['total_pdfs']}")
    log.info(f"Processed: {summary['processed']}")
    log.info(f"Success: {summary['success']}")
    log.info(f"Errors: {summary['errors']}")
    log.info(f"With OCR: {summary['with_ocr']}")
    log.info(f"Without OCR: {summary['without_ocr']}")
    log.info(f"Total Time: {summary['total_processing_time']:.2f} seconds")
    log.info(f"\nResults saved to: {output_file}")
    log.info(f"Summary saved to: {summary_file}")
    log.info("=" * 80)


if __name__ == "__main__":
    main()
