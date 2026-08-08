"""
Unit tests for API middleware (security headers, rate limiting, logging).
"""

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from starlette.responses import Response
from api.middleware import SecurityHeadersMiddleware, RateLimitMiddleware, RequestLoggingMiddleware


class TestSecurityHeaders:
    """Test security headers middleware."""
    
    def test_security_headers_added(self):
        """Test that security headers are added to responses."""
        middleware = SecurityHeadersMiddleware(lambda request: Response())
        
        request = Request({"type": "http", "method": "GET", "path": "/test"})
        response = middleware.dispatch(request, lambda req: Response())
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""
    
    def test_rate_limit_middleware_health_check(self):
        """Test that health checks bypass rate limiting."""
        middleware = RateLimitMiddleware(lambda request: Response())
        
        request = Request({"type": "http", "method": "GET", "path": "/health"})
        # Should not raise exception
        response = middleware.dispatch(request, lambda req: Response())
        assert response is not None


class TestRequestLogging:
    """Test request logging middleware."""
    
    def test_request_logging_middleware(self):
        """Test that requests are logged."""
        middleware = RequestLoggingMiddleware(lambda request: Response())
        
        request = Request({"type": "http", "method": "GET", "path": "/test"})
        response = middleware.dispatch(request, lambda req: Response())
        
        assert response is not None
        assert "X-Process-Time" in response.headers

