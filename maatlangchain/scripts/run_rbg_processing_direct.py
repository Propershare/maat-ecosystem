#!/usr/bin/env python3
"""
Direct execution of RBG processing - imports and runs main()
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Setup paths
maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

# Import after path setup
try:
    from api.main import get_vector_store
    from core.chains.document_processor import DocumentProcessor, DATALAB_AVAILABLE
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(maatlangchain_root / "processing.log")
    ]
)
log = logging.getLogger(__name__)

# Output directory - ROOT of maatlangchain
OUTPUT_DIR = maatlangchain_root
OUTPUT_DIR.mkdir(exist_ok=True)

# RBG Library locations
RBG_LOCATIONS = [
    Path("/home/suspect/.n8n/maatlangchain/docs/RBG_Library"),
]

def find_pdfs(base_path: Path) -> List[Path]:
    """Find all PDF files recursively."""
    pdfs = []
    if base_path.exists() and base_path.is_dir():
        pdfs = list(base_path.rglob("*.pdf"))
        pdfs.extend(list(base_path.rglob("*.PDF")))
    return pdfs

def detect_pdf_type(pdf_path: Path) -> str:
    """Detect if PDF is text-based or scanned."""
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        total_text = sum(len(doc.page_content) for doc in docs)
        avg_text_per_page = total_text / len(docs) if docs else 0
        if avg_text_per_page < 100:
            return "scanned"
        return "text"
    except Exception as e:
        log.warning(f"Could not detect PDF type for {pdf_path}: {e}, defaulting to OCR")
        return "scanned"

def process_pdf(pdf_path: Path, use_ocr: bool = False, vector_store=None, embeddings=None, processor=None) -> Dict[str, Any]:
    """Process a single PDF and save extracted text."""
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
        "extracted_text_file": None,
    }
    
    start_time = datetime.now()
    
    try:
        # Reuse existing processor or create new one
        # Create processor even if DB connection failed (for text extraction)
        if processor is None:
            # Only try to get vector store if we don't have it yet
            if vector_store is None or embeddings is None:
                try:
                    vector_store, embeddings = get_vector_store()
                except:
                    # Will extract text but not store in DB
                    pass
            # Create processor - embeddings/vector_store can be None if DB failed
            processor = DocumentProcessor(
                embeddings=embeddings,
                vector_store=vector_store,
                max_chunk_size=2500,
                min_chunk_size=200,
                skip_front_pages=5,
                use_ocr=use_ocr,
            )
        
        documents = processor.load_pdf(str(pdf_path), force_ocr=use_ocr)
        
        if not documents:
            result["status"] = "error"
            result["error"] = "No documents loaded"
            return result
        
        result["pages_loaded"] = len(documents)
        
        # Save extracted text to file
        safe_name = pdf_path.stem.lower().replace(' ', '_').replace('-', '_')
        text_output_file = OUTPUT_DIR / f"extracted_{safe_name}.txt"
        try:
            with open(text_output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== EXTRACTED TEXT FROM: {pdf_path.name} ===\n")
                f.write(f"Extraction Method: {'OCR (DatalabMarker)' if use_ocr else 'PyPDFLoader'}\n")
                f.write(f"Total Pages: {len(documents)}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, doc in enumerate(documents, 1):
                    f.write(f"\n--- PAGE {i} ---\n")
                    f.write(doc.page_content)
                    f.write("\n\n")
            
            result["extracted_text_file"] = str(text_output_file)
            log.info(f"  Saved extracted text to: {text_output_file.name}")
        except Exception as e:
            log.warning(f"  Could not save extracted text: {e}")
        
        # Try to store in database (may fail if DB connection issues)
        collection_name = f"rbg_{safe_name}"
        try:
            success = processor.process_documents(documents, collection_name)
            if success:
                result["chunks_created"] = len(documents)
                result["status"] = "success"
                result["collection_name"] = collection_name
            else:
                result["status"] = "partial_success"
                result["error"] = "Text extracted but failed to store in database"
        except Exception as db_error:
            # Text extraction succeeded, but DB storage failed
            result["status"] = "partial_success"
            result["error"] = f"Text extracted but DB storage failed: {str(db_error)}"
            log.warning(f"  Database storage failed, but text extracted: {db_error}")
        
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
    log.info(f"OCR Available: {DATALAB_AVAILABLE}")
    log.info("")
    
    # Find PDFs
    all_pdfs = []
    for location in RBG_LOCATIONS:
        if location.exists():
            pdfs = find_pdfs(location)
            if pdfs:
                log.info(f"Found {len(pdfs)} PDFs in {location}")
                all_pdfs.extend(pdfs)
        else:
            log.info(f"Location not found: {location}")
    
    if not all_pdfs:
        log.warning("No PDFs found in any RBG library location")
        log.info(f"Searched locations: {RBG_LOCATIONS}")
        summary = {
            "total_pdfs": 0,
            "processed": 0,
            "success": 0,
            "errors": 0,
            "with_ocr": 0,
            "without_ocr": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_processing_time": 0.0,
        }
        with open(OUTPUT_DIR / "latest_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        return
    
    log.info(f"Total PDFs to process: {len(all_pdfs)}")
    
    # Initialize vector store once (reuse for all PDFs)
    # Note: We'll still extract text even if DB connection fails
    log.info("Initializing vector store and embeddings...")
    vector_store = None
    embeddings = None
    try:
        vector_store, embeddings = get_vector_store()
        log.info("✓ Vector store initialized successfully")
    except Exception as e:
        log.warning(f"⚠️  Database connection failed: {e}")
        log.warning("Will extract text to files, but cannot store in database")
        log.warning("Please check PGVECTOR_DB_URL in /home/suspect/.n8n/tehuti-lab-webui/.env")
        # Continue anyway - we can still extract text
    
    # Process
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
    
    for i, pdf_path in enumerate(all_pdfs, 1):
        log.info(f"\n[{i}/{len(all_pdfs)}] Processing: {pdf_path.name}")
        
        pdf_type = detect_pdf_type(pdf_path)
        use_ocr = (pdf_type == "scanned")
        
        if use_ocr:
            summary["with_ocr"] += 1
            log.info(f"  Detected: Scanned PDF - Using OCR")
        else:
            summary["without_ocr"] += 1
            log.info(f"  Detected: Text PDF - Using PyPDFLoader")
        
        result = process_pdf(pdf_path, use_ocr=use_ocr, vector_store=vector_store, embeddings=embeddings)
        results.append(result)
        summary["processed"] += 1
        
        if result["status"] == "success":
            summary["success"] += 1
            log.info(f"  ✓ Success: {result['pages_loaded']} pages, {result['chunks_created']} chunks")
            if result.get("extracted_text_file"):
                log.info(f"    Text saved to: {Path(result['extracted_text_file']).name}")
        elif result["status"] == "partial_success":
            summary["success"] += 1  # Count as success since text was extracted
            log.info(f"  ⚠️  Partial Success: {result['pages_loaded']} pages extracted")
            log.info(f"    Text saved to: {Path(result['extracted_text_file']).name}")
            log.warning(f"    Database storage failed: {result.get('error', 'Unknown')}")
        else:
            summary["errors"] += 1
            log.error(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    
    # Finalize
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
    
    summary_file = OUTPUT_DIR / "latest_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create index of extracted text files
    extracted_files = [r.get("extracted_text_file") for r in results if r.get("extracted_text_file")]
    if extracted_files:
        index_file = OUTPUT_DIR / "extracted_text_index.txt"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("=== EXTRACTED TEXT FILES INDEX ===\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Total Files: {len(extracted_files)}\n")
            f.write("=" * 80 + "\n\n")
            for text_file in extracted_files:
                if text_file:
                    f.write(f"{Path(text_file).name}\n")
        log.info(f"Created extracted text index: {index_file.name}")
    
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

