#!/usr/bin/env python3
"""
Check PDF Extraction Quality from PostgreSQL

This script checks what was extracted from the RBG Library PDFs
and displays sample content to assess quality.

Maat Alignment: Truth (verify extraction), Order (document results)
"""

import os
import sys
import json
import psycopg2
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_db_connection():
    """Get PostgreSQL connection from environment."""
    PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
    
    if not PGVECTOR_DB_URL:
        # Try reading from .env file
        env_file = "/home/suspect/.n8n/open-webui/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("PGVECTOR_DB_URL="):
                        PGVECTOR_DB_URL = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not PGVECTOR_DB_URL:
        print("❌ PGVECTOR_DB_URL not found in environment or .env file")
        return None
    
    try:
        conn = psycopg2.connect(PGVECTOR_DB_URL)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
            return None

def check_extraction_quality(pdf_name=None):
    """Check extraction quality from PostgreSQL."""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    print("=" * 80)
    print("PDF EXTRACTION QUALITY CHECK")
    print("=" * 80)
    print()
    
    # Check if PGVector tables exist
    try:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'langchain_pg_collection'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ PGVector tables do not exist")
            print("   No data has been stored yet.")
            conn.close()
            return
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        conn.close()
        return
    
    # Check collections
    cur.execute("SELECT name, uuid FROM langchain_pg_collection;")
    collections = cur.fetchall()
    
    if not collections:
        print("⚠️  No collections found in database")
        print("   Run the processing script first:")
        print("   python3 scripts/process_rbg_library.py --limit 1")
        conn.close()
        return
    
    print("📊 Collections in database:")
    for name, uuid in collections:
        print(f"  - {name}")
    print()
    
    # Use maat_knowledge collection (or first collection if not found)
    collection_name = "maat_knowledge"
    collection_uuid = None
    
    for name, uuid in collections:
        if name == collection_name:
            collection_uuid = uuid
            break
    
    if not collection_uuid and collections:
        # Use first collection
        collection_name, collection_uuid = collections[0]
        print(f"⚠️  Using collection '{collection_name}' (maat_knowledge not found)")
        print()
    
    # Count total chunks
    cur.execute("""
        SELECT COUNT(*) 
        FROM langchain_pg_embedding
        WHERE collection_id = %s;
    """, (collection_uuid,))
    total_chunks = cur.fetchone()[0]
    print(f"📊 Total chunks in '{collection_name}': {total_chunks}")
    print()
    
    # Check for specific PDF
    if pdf_name:
        cur.execute("""
            SELECT COUNT(*) 
            FROM langchain_pg_embedding e
            WHERE e.collection_id = %s
            AND e.cmetadata->>'pdf_name' = %s;
        """, (collection_uuid, pdf_name))
        pdf_chunks = cur.fetchone()[0]
        print(f"📄 Chunks for '{pdf_name}': {pdf_chunks}")
        print()
        
        if pdf_chunks == 0:
            print(f"⚠️  No chunks found for '{pdf_name}'")
            print("   The PDF may not have been fully processed or stored.")
            print()
        
        # Get sample chunks
        cur.execute("""
            SELECT e.document, e.cmetadata, e.embedding IS NOT NULL as has_embedding
            FROM langchain_pg_embedding e
            WHERE e.collection_id = %s
            AND e.cmetadata->>'pdf_name' = %s
            ORDER BY (e.cmetadata->>'chunk_index')::int NULLS LAST
            LIMIT 10;
        """, (collection_uuid, pdf_name))
        
        samples = cur.fetchall()
        
        if samples:
            print("=" * 80)
            print(f"SAMPLE EXTRACTS FROM: {pdf_name}")
            print("=" * 80)
            print()

            for i, (content, metadata, has_embedding) in enumerate(samples, 1):
                print(f"--- Chunk {i} ---")
                print(f"Has Embedding: {'✅' if has_embedding else '❌'}")
                if metadata:
                    print(f"Metadata: {json.dumps(metadata, indent=2)}")
                print(f"Content Preview (first 300 chars):")
                print("-" * 80)
                print(content[:300] if content else "(empty)")
                if content and len(content) > 300:
                    print("...")
                print("-" * 80)
                print()
        else:
            print("⚠️  No sample chunks available")
    else:
        # Get all PDFs
        cur.execute("""
            SELECT DISTINCT e.cmetadata->>'pdf_name' as pdf_name,
                   COUNT(*) as chunk_count
            FROM langchain_pg_embedding e
            WHERE e.collection_id = %s
            AND e.cmetadata->>'pdf_name' IS NOT NULL
            GROUP BY e.cmetadata->>'pdf_name'
            ORDER BY chunk_count DESC;
        """, (collection_uuid,))
        
        pdfs = cur.fetchall()
        
        if pdfs:
            print("=" * 80)
            print("PDFs IN DATABASE:")
            print("=" * 80)
            print()
            
            for pdf_name, chunk_count in pdfs:
                print(f"📄 {pdf_name}: {chunk_count} chunks")
            
            print()
            print("💡 Use --pdf-name to see samples from a specific PDF")
        else:
            print("⚠️  No PDFs found in database")
            print("   Run the processing script first:")
            print("   python3 scripts/process_rbg_library.py --limit 1")
    
    # Get extraction method statistics
    cur.execute("""
        SELECT 
            e.cmetadata->>'extraction_method' as method,
            COUNT(*) as count
        FROM langchain_pg_embedding e
        WHERE e.collection_id = %s
        AND e.cmetadata->>'extraction_method' IS NOT NULL
        GROUP BY e.cmetadata->>'extraction_method';
    """, (collection_uuid,))
    
    methods = cur.fetchall()
    if methods:
        print("=" * 80)
        print("EXTRACTION METHODS USED:")
        print("=" * 80)
        for method, count in methods:
            print(f"  {method}: {count} chunks")
        print()
    
    # Quality indicators
    cur.execute("""
        SELECT 
            AVG(LENGTH(e.document)) as avg_length,
            MIN(LENGTH(e.document)) as min_length,
            MAX(LENGTH(e.document)) as max_length,
            COUNT(*) FILTER (WHERE LENGTH(e.document) < 100) as short_chunks,
            COUNT(*) FILTER (WHERE LENGTH(e.document) > 1000) as long_chunks
        FROM langchain_pg_embedding e
        WHERE e.collection_id = %s;
    """, (collection_uuid,))
    
    stats = cur.fetchone()
    if stats and total_chunks > 0:
        avg_len, min_len, max_len, short_chunks, long_chunks = stats
        print("=" * 80)
        print("QUALITY STATISTICS:")
        print("=" * 80)
        print(f"Average chunk length: {avg_len:.0f} characters")
        print(f"Min chunk length: {min_len} characters")
        print(f"Max chunk length: {max_len} characters")
        print(f"Short chunks (<100 chars): {short_chunks} ({short_chunks/total_chunks*100:.1f}%)")
        print(f"Long chunks (>1000 chars): {long_chunks} ({long_chunks/total_chunks*100:.1f}%)")
        print()
        
        # Quality assessment
        if short_chunks / total_chunks > 0.1:
            print("⚠️  WARNING: High percentage of short chunks")
            print("   This may indicate poor extraction quality")
        else:
            print("✅ Chunk length distribution looks good")
    
    conn.close()
    print("=" * 80)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check PDF extraction quality from PostgreSQL"
    )
    parser.add_argument(
        "--pdf-name",
        type=str,
        default="Africa and the Americas.pdf",
        help="PDF name to check (default: Africa and the Americas.pdf)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all PDFs in database"
    )

    args = parser.parse_args()

    if args.all:
        check_extraction_quality(pdf_name=None)
    else:
        check_extraction_quality(pdf_name=args.pdf_name)

if __name__ == "__main__":
    main()
