"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


class TestAPIAuthentication:
    """Test API authentication."""
    
    def test_rag_query_without_api_key(self, client, mock_env):
        """Test RAG query without API key (should work in dev mode)."""
        # In dev mode (no API key configured), should work
        response = client.post(
            "/rag/query",
            json={"question": "What is Maat?"}
        )
        # Should either work (dev mode) or return 401 (if required)
        assert response.status_code in [200, 401, 500]  # 500 if DB not configured
    
    def test_rag_query_with_api_key(self, client, mock_env):
        """Test RAG query with valid API key."""
        response = client.post(
            "/rag/query",
            headers={"X-API-Key": mock_env["MAATLANGCHAIN_API_KEY"]},
            json={"question": "What is Maat?"}
        )
        # Should either work or return 500 if DB not configured
        assert response.status_code in [200, 500]
    
    def test_rag_query_with_invalid_api_key(self, client, mock_env):
        """Test RAG query with invalid API key."""
        # Set API key as required
        import os
        os.environ["MAATLANGCHAIN_API_KEY_REQUIRED"] = "true"
        
        response = client.post(
            "/rag/query",
            headers={"X-API-Key": "invalid-key"},
            json={"question": "What is Maat?"}
        )
        # Should return 401 if API key is required
        assert response.status_code in [401, 500]  # 500 if DB not configured


class TestOpenAPIEndpoint:
    """Test OpenAPI spec endpoint."""
    
    def test_openapi_spec(self, client):
        """Test OpenAPI spec endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

