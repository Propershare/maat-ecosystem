"""
Unit tests for API authentication and security.
"""

import pytest
import os
from api.auth import (
    verify_api_key,
    generate_api_key,
    check_rate_limit,
    get_client_id,
    get_rate_limit_config,
)


class TestAPIKeyAuth:
    """Test API key authentication."""
    
    def test_generate_api_key(self):
        """Test API key generation."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert len(key1) > 20  # Should be reasonably long
        assert key1 != key2  # Should be unique
    
    def test_verify_api_key_valid(self, mock_env):
        """Test valid API key verification."""
        api_key = mock_env["MAATLANGCHAIN_API_KEY"]
        assert verify_api_key(api_key) is True
    
    def test_verify_api_key_invalid(self, mock_env):
        """Test invalid API key verification."""
        assert verify_api_key("invalid-key") is False
        assert verify_api_key("") is False
        assert verify_api_key(None) is False
    
    def test_verify_api_key_no_config(self, monkeypatch):
        """Test API key verification when no key is configured (dev mode)."""
        monkeypatch.delenv("MAATLANGCHAIN_API_KEY", raising=False)
        # Should allow any key in dev mode
        assert verify_api_key("any-key") is True


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_within_limit(self):
        """Test rate limiting when within limit."""
        client_id = "test_client_1"
        # Clear any existing entries
        from api.auth import _rate_limit_store
        if client_id in _rate_limit_store:
            del _rate_limit_store[client_id]
        
        # Should allow requests within limit
        for i in range(10):
            assert check_rate_limit(client_id, max_requests=100, window_seconds=60) is True
    
    def test_rate_limit_exceeded(self):
        """Test rate limiting when limit is exceeded."""
        client_id = "test_client_2"
        # Clear any existing entries
        from api.auth import _rate_limit_store
        if client_id in _rate_limit_store:
            del _rate_limit_store[client_id]
        
        # Exceed the limit
        max_requests = 5
        for i in range(max_requests):
            assert check_rate_limit(client_id, max_requests=max_requests, window_seconds=60) is True
        
        # Next request should be blocked
        assert check_rate_limit(client_id, max_requests=max_requests, window_seconds=60) is False
    
    def test_get_client_id_api_key(self):
        """Test client ID generation from API key."""
        api_key = "test-api-key-12345"
        client_id = get_client_id(api_key=api_key)
        assert client_id.startswith("api_key:")
        assert "..." in client_id
    
    def test_get_client_id_ip(self):
        """Test client ID generation from IP."""
        client_id = get_client_id(request_ip="192.168.1.1")
        assert client_id.startswith("ip:")
        assert "192.168.1.1" in client_id
    
    def test_get_rate_limit_config(self, mock_env):
        """Test rate limit configuration."""
        config = get_rate_limit_config()
        assert "max_requests" in config
        assert "window_seconds" in config
        assert "enabled" in config
        assert isinstance(config["max_requests"], int)
        assert isinstance(config["window_seconds"], int)
        assert isinstance(config["enabled"], bool)

