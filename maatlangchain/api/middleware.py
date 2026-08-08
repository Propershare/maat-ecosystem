"""
MaatLangChain API Middleware

Security and rate limiting middleware following Maat principles.
"""

import time
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

from api.auth import check_rate_limit, get_client_id, get_rate_limit_config

log = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remove server header (security through obscurity)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health", "/openapi.json", "/docs", "/redoc"]:
            return await call_next(request)
        
        # Get rate limit config
        config = get_rate_limit_config()
        
        if not config["enabled"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key")
        client_id = get_client_id(api_key=api_key, request_ip=client_ip)
        
        # Check rate limit
        if not check_rate_limit(
            client_id=client_id,
            max_requests=config["max_requests"],
            window_seconds=config["window_seconds"]
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {config['max_requests']} requests per {config['window_seconds']} seconds.",
                headers={
                    "X-RateLimit-Limit": str(config["max_requests"]),
                    "X-RateLimit-Window": str(config["window_seconds"]),
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(config["max_requests"])
        response.headers["X-RateLimit-Window"] = str(config["window_seconds"])
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for audit trail."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        log.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            log.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            log.error(
                f"Error: {request.method} {request.url.path} "
                f"from {client_ip} "
                f"Time: {process_time:.3f}s "
                f"Error: {str(e)}"
            )
            raise

