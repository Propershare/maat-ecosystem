"""
Store K2 Methodology in RAG System
Maat: Truth, Order - Makes K2 methodology retrievable for agents
"""

import sys
from pathlib import Path

maatlangchain_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(maatlangchain_root))

from core.chains.maat_rag import MaatRAG
from core.chains.document_processor import DocumentProcessor
from langchain_core.documents import Document
from core.agents.k2_agent import K2_STAGES

def store_k2_in_rag():
    """Store K2 methodology in RAG system."""
    print("=" * 80)
    print("Storing K2 Methodology in RAG")
    print("=" * 80)
    print()
    
    # Initialize RAG and processor
    try:
        # Get vector store and embeddings (same as api/main.py)
        from api.main import get_vector_store
        vector_store, embeddings = get_vector_store()
        rag = MaatRAG(vector_store=vector_store, embeddings=embeddings)
        processor = DocumentProcessor()
        print("✅ RAG and DocumentProcessor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create K2 methodology document
    k2_content = "# K2 Dialectical Development Methodology\n\n"
    k2_content += "## Overview\n\n"
    k2_content += "K2 is a 42-stage dialectical development framework for analyzing "
    k2_content += "how systems, ideas, and processes develop through contradiction and transformation.\n\n"
    
    k2_content += "## The 42 Stages\n\n"
    
    for stage_num in sorted(K2_STAGES.keys()):
        stage = K2_STAGES[stage_num]
        k2_content += f"### Stage {stage_num}: {stage['name']}\n\n"
        k2_content += f"{stage['description']}\n\n"
    
    k2_content += "## Maat Principles\n\n"
    k2_content += "- **Truth**: Reveals hidden contradictions and power dynamics\n"
    k2_content += "- **Order**: Structured 42-stage process\n"
    k2_content += "- **Balance**: Shows how opposites interact and balance\n"
    k2_content += "- **Justice**: Exposes power shifts and transformations\n"
    k2_content += "- **Self-Reflection**: Requires examining internal contradictions\n\n"
    
    k2_content += "## Usage\n\n"
    k2_content += "Use K2 methodology when analyzing:\n"
    k2_content += "- Complex systems undergoing change\n"
    k2_content += "- Social movements and historical processes\n"
    k2_content += "- Relationships and organizational dynamics\n"
    k2_content += "- Any process involving contradiction and transformation\n"
    
    # Create document
    doc = Document(
        page_content=k2_content,
        metadata={
            "source": "k2_methodology",
            "method_name": "K2_Dialectical_Development",
            "type": "research_methodology",
            "stages": 42,
            "category": "dialectical_analysis"
        }
    )
    
    print(f"✅ Created K2 document ({len(k2_content)} characters)")
    print()
    
    # Process and store
    collection_name = "research_methods_k2"
    print(f"Processing and storing in collection: {collection_name}")
    
    try:
        success = processor.process_documents([doc], collection_name)
        
        if success:
            print("✅ K2 methodology stored in RAG successfully")
            print()
            print(f"Collection: {collection_name}")
            print(f"Stages documented: {len(K2_STAGES)}")
        else:
            print("❌ Failed to store K2 methodology")
            
    except Exception as e:
        print(f"❌ Error storing K2: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("K2 Storage Complete")
    print("=" * 80)

if __name__ == "__main__":
    store_k2_in_rag()

