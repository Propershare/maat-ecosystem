"""
Pytest configuration and fixtures for MaatLangChain tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DB_URL = os.environ.get("TEST_PGVECTOR_DB_URL", "postgresql://test:test@localhost:5434/test_db")
TEST_API_KEY = os.environ.get("TEST_API_KEY", "test-api-key-12345")


@pytest.fixture
def test_db_url():
    """Get test database URL."""
    return TEST_DB_URL


@pytest.fixture
def test_api_key():
    """Get test API key."""
    return TEST_API_KEY


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("PGVECTOR_DB_URL", TEST_DB_URL)
    monkeypatch.setenv("MAATLANGCHAIN_API_KEY", TEST_API_KEY)
    monkeypatch.setenv("MAATLANGCHAIN_RATE_LIMIT_ENABLED", "false")  # Disable rate limiting in tests
    return {
        "PGVECTOR_DB_URL": TEST_DB_URL,
        "MAATLANGCHAIN_API_KEY": TEST_API_KEY,
    }


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        "content": "This is a test document about Maat principles. Maat represents truth, balance, order, justice, and self-reflection.",
        "metadata": {
            "file_name": "test_document.txt",
            "page": 1,
            "source": "test"
        }
    }

