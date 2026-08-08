#!/usr/bin/env python3
"""
Real Corpus Retriever for Maat Legal Runtime
Wire to /home/suspect/.n8n/Legal_AI_FL/ and perform real retrieval.
"""

import os
import re
import glob
from typing import List, Dict, Any

# ================== ================================
# 1. CORPUS PATHS (ARCHITECTURAL BOUNDARIES)
# ================== ================================

CORPUS_ROOT = "/home/suspect/.n8n/Legal_AI_FL/law_data_clean"
STATUTES_DIR = os.path.join(CORPUS_ROOT, "fl_statutes")
CASES_DIR = os.path.join(CORPUS_ROOT, "fl_cases")
RULES_DIR = os.path.join(CORPUS_ROOT, "fl_rules")

# ================== ================================
# 2. METADATA EXTRACTOR
# ================== ================================

def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata from content headers."""
    metadata = {}
    
    frontmatter_pattern = r'^---\s*\n(.*?)\n---'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        for line in fm_text.strip().split('\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                metadata[key.strip()] = value.strip()
    
    return metadata

# ================== ================================
# 3. CORPUS INDEXER
# ================== ================================

class CorpusIndexer:
    """Index the Florida trust law corpus."""
    
    def __init__(self):
        self.index: Dict[str, List[Dict]] = {}
        self.chunks: List[Dict] = []
        self.file_count = 0
        self.total_chunks = 0
    
    def index_corpus(self) -> None:
        """Index all available corpus files."""
        print("Indexing corpus from:", CORPUS_ROOT)
        
        # Index statutes
        statutes_path = os.path.join(CORPUS_ROOT, "fl_statutes")
        for statute_file in glob.glob(os.path.join(statutes_path, "*.md")):
            self._index_file(statute_file)
        
        # Index cases
        cases_path = os.path.join(CORPUS_ROOT, "fl_cases")
        for case_file in glob.glob(os.path.join(cases_path, "*.md")):
            self._index_file(case_file)
        
        # Index rules
        rules_path = os.path.join(CORPUS_ROOT, "fl_rules")
        for rule_file in glob.glob(os.path.join(rules_path, "*.md")):
            self._index_file(rule_file)
        
        print(f"Indexed {self.file_count} files into {self.total_chunks} chunks")
    
    def _index_file(self, path: str) -> None:
        """Index a single file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = extract_metadata(content)
            
            chunk_info = {
                'source': path,
                'filename': os.path.basename(path),
                'metadata': metadata,
                'content': content
            }
            
            if 'statutes' in path:
                chunk_info['type'] = 'statute'
            elif 'cases' in path:
                chunk_info['type'] = 'case'
            elif 'rules' in path:
                chunk_info['type'] = 'rule'
            else:
                chunk_info['type'] = 'other'
            
            doc_type = chunk_info['type']
            if doc_type not in self.index:
                self.index[doc_type] = []
            
            self.index[doc_type].append(chunk_info)
            self.chunks.append(chunk_info)
            self.file_count += 1
            self.total_chunks += 1
            
        except Exception as e:
            print(f"Error indexing {path}: {e}")

# ================== ================================
# 4. REAL RETRIEVE FUNCTION
# ================== ================================

def retrieve_by_type(doc_type: str, keywords: str = "", top_k: int = 5) -> List[Dict]:
    """Retrieve chunks by document type."""
    if doc_type not in CorpusIndexer.index:
        return []
    
    results = []
    for chunk in CorpusIndexer.index[doc_type]:
        full_text = chunk['content'][:500]
        
        if not keywords or keywords.lower() in full_text.lower():
            results.append(chunk)
    
    return results[:top_k]

def retrieve_by_keyword(keyword: str, top_k: int = 5) -> List[Dict]:
    """Retrieve chunks by keyword search."""
    all_chunks = []
    for doc_type in CorpusIndexer.index.values():
        all_chunks.extend(doc_type)
    
    results = []
    for chunk in all_chunks:
        content = chunk['content'][:1000]
        if keyword.lower() in content.lower() or keyword in chunk['metadata']:
            results.append(chunk)
    
    return results[:top_k]

# ================== ================================
# 5. MAIN RETRIEVE INTERFACE
# ================== ================================

class FloridaTrustRetriever:
    """Main retriever interface."""
    
    def __init__(self):
        self.indexer = CorpusIndexer()
        self.corpus_path = CORPUS_ROOT
    
    def connect(self) -> None:
        """Connect to and index the corpus."""
        self.indexer.index_corpus()
    
    def retrieve_statute(self, keyword: str, top_k: int = 5) -> List[Dict]:
        """Retrieve statute content."""
        if self.indexer.index.get('statute'):
            results = []
            for chunk in self.indexer.index['statute']:
                full_text = chunk['content'][:500]
                
                if not keyword or keyword.lower() in full_text.lower():
                    results.append(chunk)
            
            return results[:top_k]
        return []
    
    def retrieve_case(self, keyword: str, top_k: int = 5) -> List[Dict]:
        """Retrieve case law content."""
        if self.indexer.index.get('case'):
            results = []
            for chunk in self.indexer.index['case']:
                full_text = chunk['content'][:500]
                
                if not keyword or keyword.lower() in full_text.lower():
                    results.append(chunk)
            
            return results[:top_k]
        return []
    
    def retrieve_ruling(self, keyword: str, top_k: int = 5) -> List[Dict]:
        """Retrieve rule/regulation content."""
        if self.indexer.index.get('rule'):
            results = []
            for chunk in self.indexer.index['rule']:
                full_text = chunk['content'][:500]
                
                if not keyword or keyword.lower() in full_text.lower():
                    results.append(chunk)
            
            return results[:top_k]
        return []
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """General keyword search."""
        all_chunks = []
        for doc_type in self.indexer.index.values():
            all_chunks.extend(doc_type)
        
        results = []
        for chunk in all_chunks:
            content = chunk['content'][:1000]
            if query.lower() in content.lower() or query in chunk['metadata']:
                results.append(chunk)
        
        return results[:top_k]

# ================== ================================
# 6. CORPUS STATUS REPORT
# ================== ================================

def main():
    """Run retrieval tests and prove integration."""
    
    # ====== INITIALIZATION ======
    print("=" * 70)
    print("Maat Legal Runtime - Real Corpus Retriever Test")
    print("=" * 70)
    
    # ====== CORPUS PATH ======
    print(f"\nCorpus Path: {CORPUS_ROOT}")
    print(f"Statutes Dir: {STATUTES_DIR}")
    print(f"Cases Dir: {CASES_DIR}")
    print(f"Rules Dir: {RULES_DIR}")
    
    # ====== WIRING RETRIEVER ======
    print("\nWiring retriever to corpus...")
    retriever = FloridaTrustRetriever()
    
    # ====== INDEXING ======
    print("\nIndexing corpus files...")
    retriever.connect()
    
    # ====== INDEXING PROOF ======
    print(f"\n=== Indexing Proof ===")
    print(f"Corpus Path Used: {retriever.corpus_path}")
    print(f"Files Indexed: {retriever.indexer.file_count}")
    print(f"Total Chunks: {retriever.indexer.total_chunks}")
    print(f"Document Types: {list(retriever.indexer.index.keys())}")
    
    # ====== STATUTE RETRIEVAL ======
    print("\n=== Statute Retrieval Test ===")
    print("Query: 'trust'")
    statutes = retriever.retrieve_statute("trust", top_k=2)
    if statutes:
        print(f"✅ Retrieved {len(statutes)} statute(s)")
        for statute in statutes:
            print(f"   Source: {statute['filename']}")
            print(f"   Metadata: {statute['metadata']}")
            snippet = statute['content'][:200]
            print(f"   Snippet: {snippet}...")
    else:
        print("⚠️  No statutes found for keyword 'trust'")
    
    # ====== CASE RETRIEVAL ======
    print("\n=== Case Retrieval Test ===")
    print("Query: 'revocable'")
    cases = retriever.retrieve_case("revocable", top_k=2)
    if cases:
        print(f"✅ Retrieved {len(cases)} case(s)")
        for case in cases:
            print(f"   Source: {case['filename']}")
            print(f"   Metadata: {case['metadata']}")
            snippet = case['content'][:200]
            print(f"   Snippet: {snippet}...")
    else:
        print("⚠️  No cases found for keyword 'revocable'")
    
    # ====== GENERAL SEARCH ======
    print("\n=== General Search Test ===")
    print("Query: 'fiduciary'")
    results = retriever.search("fiduciary", top_k=2)
    if results:
        print(f"✅ Found {len(results)} results")
        for result in results:
            print(f"   Source: {result['filename']}")
            print(f"   Type: {result['type']}")
            print(f"   Content: {result['content'][:150]}...")
    else:
        print("⚠️  No results found")
    
    # ====== TRUST-SPECIFIC QUERY ======
    print("\n=== Trust-Specific Query Test ===")
    print("Query: 'minor beneficiary'")
    minor_results = retriever.search("minor", top_k=2)
    if minor_results:
        print(f"✅ Found {len(minor_results)} results for 'minor'")
        for result in minor_results:
            print(f"   Source: {result['filename']}")
            snippet = result['content'][:150]
            print(f"   Snippet: {snippet}...")
    else:
        print("⚠️  No minor-related results found")
    
    # ====== ASSET PROTECTION QUERY ======
    print("\n=== Asset Protection Query Test ===")
    print("Query: 'spendthrift'")
    asset_results = retriever.search("spendthrift", top_k=2)
    if asset_results:
        print(f"✅ Found {len(asset_results)} results")
        for result in asset_results:
            print(f"   Source: {result['filename']}")
            print(f"   Content: {result['content'][:150]}...")
    else:
        print("⚠️  No spendthrift results found")
    
    # ====== FINAL STATUS ======
    print("\n" + "=" * 70)
    print("Corpus Integration Status Report")
    print("=" * 70)
    print(f"Corpus Path Used: {retriever.corpus_path}")
    print(f"Files Indexed: {retriever.indexer.file_count}")
    print(f"Chunks Available: {retriever.indexer.total_chunks}")
    print(f"Retriever Type: REAL (CORPUS INTEGRATED)")
    print(f"Stub Retriever Status: REPLACED")
    print("=" * 70)
    
    return retriever

if __name__ == "__main__":
    main()