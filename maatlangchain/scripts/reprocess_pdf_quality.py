#!/usr/bin/env python3
"""
Re-process PDF with improved quality filtering.

This script re-processes a PDF with:
- Front matter filtering (skips title pages, copyright, TOC)
- Quality filtering (removes small/low-quality chunks)
- Better chunking strategy
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))
os.environ['PYTHONPATH'] = str(maatlangchain_root)
os.chdir(maatlangchain_root)  # Change to root directory

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def main():
    """Re-process PDF with quality improvements."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Re-process PDF with quality filtering")
    parser.add_argument(
        "--pdf-path",
        type=str,
        default="/home/suspect/.n8n/jarvis/rbg-library/A-1/Africa and the Americas.pdf",
        help="Path to PDF file"
    )
    parser.add_argument(
        "--min-chunk-size",
        type=int,
        default=200,
        help="Minimum chunk size in characters (default: 200)"
    )
    parser.add_argument(
        "--skip-front-pages",
        type=int,
        default=5,
        help="Number of front pages to skip (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Import after path setup
    try:
        from core.chains.document_processor import DocumentProcessor
        from langchain_community.vectorstores import PGVector
        from langchain_huggingface import HuggingFaceEmbeddings
        import psycopg2
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the maatlangchain directory")
        import traceback
        traceback.print_exc()
        return 1
    
    # Initialize components
    print("Initializing MaatLangChain components...")
    
    # Get PostgreSQL connection string
    PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
    if not PGVECTOR_DB_URL:
        env_file = "/home/suspect/.n8n/open-webui/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("PGVECTOR_DB_URL="):
                        PGVECTOR_DB_URL = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not PGVECTOR_DB_URL:
        print("❌ PGVECTOR_DB_URL not found")
        return 1
    
    # Get embeddings
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Use CPU to avoid GPU conflicts
        )
        print("✅ Embeddings initialized")
    except Exception as e:
        print(f"❌ Failed to initialize embeddings: {e}")
        return 1
    
    # Get vector store (PostgreSQL/pgvector)
    try:
        # Verify pgvector extension
        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        if not cur.fetchone():
            print("❌ pgvector extension not found")
            conn.close()
            return 1
        conn.close()
        
        vector_store = PGVector(
            connection_string=PGVECTOR_DB_URL,
            embedding_function=embeddings,
            collection_name="maat_knowledge",
            use_jsonb=True
        )
        print("✅ Connected to PostgreSQL/pgvector")
    except Exception as e:
        print(f"❌ Failed to connect to vector store: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Create processor with quality filtering
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=2500,
        min_chunk_size=args.min_chunk_size,
        skip_front_pages=args.skip_front_pages
    )
    
    print(f"\nProcessing: {args.pdf_path}")
    print(f"Settings:")
    print(f"  - Min chunk size: {args.min_chunk_size} chars")
    print(f"  - Skip front pages: {args.skip_front_pages}")
    print()
    
    # Process PDF
    result = processor.process_pdf(args.pdf_path, collection_name="maat_knowledge")
    
    if result.get("status") == "success":
        print("\n✅ PDF processed successfully!")
        print(f"   Documents loaded: {result.get('documents_loaded', 0)}")
    else:
        print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

