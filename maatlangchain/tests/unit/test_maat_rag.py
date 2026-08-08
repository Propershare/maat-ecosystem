"""
Unit tests for MaatRAG class.
"""

import pytest
from unittest.mock import Mock, MagicMock
from core.chains.maat_rag import MaatRAG


class TestMaatRAG:
    """Test MaatRAG class."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = Mock()
        store.add_texts = Mock(return_value=None)
        store.similarity_search = Mock(return_value=[])
        store.similarity_search_with_score = Mock(return_value=[])
        return store
    
    @pytest.fixture
    def mock_embeddings(self):
        """Create mock embeddings."""
        embeddings = Mock()
        return embeddings
    
    @pytest.fixture
    def rag_instance(self, mock_vector_store, mock_embeddings):
        """Create MaatRAG instance."""
        return MaatRAG(mock_vector_store, mock_embeddings)
    
    def test_rag_initialization(self, rag_instance):
        """Test RAG initialization."""
        assert rag_instance.vector_store is not None
        assert rag_instance.embeddings is not None
        assert "documents_processed" in rag_instance.performance_stats
    
    def test_store_document_empty_chunks(self, rag_instance):
        """Test storing empty chunks."""
        result = rag_instance.store_document([], "test_collection")
        assert result is False
    
    def test_search_similar(self, rag_instance, mock_vector_store):
        """Test similarity search."""
        # Mock documents
        from langchain_core.documents import Document
        mock_docs = [
            Document(page_content="Test content 1", metadata={"page": 1}),
            Document(page_content="Test content 2", metadata={"page": 2}),
        ]
        mock_vector_store.similarity_search.return_value = mock_docs
        
        results = rag_instance.search_similar("test query", "test_collection", top_k=2)
        assert len(results) == 2
        assert results[0].page_content == "Test content 1"
    
    def test_get_performance_stats(self, rag_instance):
        """Test getting performance statistics."""
        stats = rag_instance.get_performance_stats()
        assert "documents_processed" in stats
        assert "chunks_created" in stats
        assert "embeddings_generated" in stats
        assert "total_processing_time" in stats
    
    def test_reset_stats(self, rag_instance):
        """Test resetting performance statistics."""
        # Modify stats
        rag_instance.performance_stats["documents_processed"] = 10
        rag_instance.reset_stats()
        
        stats = rag_instance.get_performance_stats()
        assert stats["documents_processed"] == 0
        assert stats["chunks_created"] == 0

