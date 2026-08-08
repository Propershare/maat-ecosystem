#!/usr/bin/env python3
"""View PDF chunks in plain English JSON - no SQL needed."""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def get_db():
    """Get database connection."""
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
        return None
    
    try:
        import psycopg2
        return psycopg2.connect(PGVECTOR_DB_URL)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_pdfs():
    """List all PDFs."""
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            cmetadata->>'file_name' as name,
            COUNT(*) as chunks
        FROM langchain_pg_embedding 
        GROUP BY name
        ORDER BY name;
    """)
    
    print("PDFs in database:")
    for name, count in cur.fetchall():
        print(f"  📄 {name}: {count} chunks")
    
    conn.close()

def view_chunks(pdf_name=None, limit=5, skip_toc=True, main_content_only=False):
    """View chunks as JSON.
    
    Args:
        pdf_name: PDF file name to filter
        limit: Number of chunks to return
        skip_toc: Skip table of contents pages
        main_content_only: Only show pages with Arabic numerals (skip Roman numeral pages)
    """
    conn = get_db()
    if not conn:
        return
    
    cur = conn.cursor()
    
    # Build query - skip TOC by default
    where_parts = []
    params = []
    
    if pdf_name:
        where_parts.append("cmetadata->>'file_name' = %s")
        params.append(pdf_name)
    
    if skip_toc:
        # Filter out TOC pages - match various patterns
        where_parts.append("""
            document NOT ILIKE '%%CONTENTS%%' 
            AND document NOT ILIKE '%%C ONTENTS%%'
            AND document NOT ILIKE '%%ONTENTS%%'
        """)
    
    if main_content_only:
        # Only show pages with Arabic numerals (page number >= 20 typically means main content)
        # Roman numerals are usually pages 1-20
        where_parts.append("(cmetadata->>'page')::int >= 20")
    
    where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
    params.append(limit)
    
    query = """
        SELECT document, cmetadata
        FROM langchain_pg_embedding 
        """ + where_clause + """
        ORDER BY (cmetadata->>'page')::int NULLS LAST
        LIMIT %s;
    """
    
    cur.execute(query, params)
    
    chunks = []
    for doc, meta in cur.fetchall():
        page_num = meta.get("page", meta.get("page_number", "unknown"))
        page_label = meta.get("page_label", "")
        
        # Determine if it's a Roman numeral page
        is_roman = False
        if page_label and page_label.strip():
            # Check if page_label looks like Roman numeral (i, ii, iii, iv, v, vi, vii, viii, ix, x, xi, xii, etc.)
            roman_patterns = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx']
            if page_label.lower().strip() in roman_patterns:
                is_roman = True
        
        chunks.append({
            "text": doc[:500] + "..." if len(doc) > 500 else doc,
            "full_length": len(doc),
            "file": meta.get("file_name", "unknown"),
            "page_number": page_num,
            "page_label": page_label,
            "is_front_matter": is_roman,  # True if Roman numeral (preface/TOC), False if main content
        })
    
    print(json.dumps(chunks, indent=2, ensure_ascii=False))
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="View PDF chunks in plain JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all PDFs
  python3 view_chunks.py --list
  
  # View main content only (skip Roman numeral pages like prefaces)
  python3 view_chunks.py --pdf "book.pdf" --main-content
  
  # View everything including TOC
  python3 view_chunks.py --pdf "book.pdf" --include-toc
        """
    )
    parser.add_argument("--list", action="store_true", help="List all PDFs in database")
    parser.add_argument("--pdf", help="PDF file name to view chunks for")
    parser.add_argument("--limit", type=int, default=5, help="Number of chunks to show (default: 5)")
    parser.add_argument("--include-toc", action="store_true", help="Include table of contents chunks")
    parser.add_argument("--main-content", action="store_true", 
                       help="Only show main content (skip Roman numeral pages like prefaces/TOC)")
    args = parser.parse_args()
    
    if args.list:
        list_pdfs()
    else:
        view_chunks(
            args.pdf, 
            args.limit, 
            skip_toc=not args.include_toc,
            main_content_only=args.main_content
        )

