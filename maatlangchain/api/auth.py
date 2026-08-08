"""
MaatLangChain API Authentication & Security

Following Maat principles:
- Truth: Secure, verified authentication
- Balance: Minimal overhead, efficient
- Order: Standard patterns, well-documented
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from functools import lru_cache
import logging

log = logging.getLogger(__name__)

# API Key Header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limiting storage (in-memory for now, can be upgraded to Redis)
_rate_limit_store = {}


def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variable."""
    return os.environ.get("MAATLANGCHAIN_API_KEY")


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: Optional[str] = None) -> bool:
    """
    Verify API key against configured key.
    
    Args:
        api_key: API key to verify
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    expected_key = get_api_key_from_env()
    
    # If no API key configured, allow access (development mode)
    if not expected_key:
        log.warning("No MAATLANGCHAIN_API_KEY configured - allowing all requests (development mode)")
        return True
    
    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(api_key, expected_key)


async def get_api_key(api_key_header: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """
    Dependency to verify API key.
    
    Args:
        api_key_header: API key from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    # Check if API key is required
    api_key_required = os.environ.get("MAATLANGCHAIN_API_KEY_REQUIRED", "false").lower() == "true"
    expected_key = get_api_key_from_env()
    
    # If no key configured and not required, allow access
    if not expected_key and not api_key_required:
        return "development_mode"
    
    # If key is required but not provided
    if api_key_required and not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
        )
    
    # Verify the key
    if not verify_api_key(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return api_key_header


def check_rate_limit(client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
    """
    Check if client has exceeded rate limit.
    
    Args:
        client_id: Client identifier (IP or API key)
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        
    Returns:
        True if within limit, False if exceeded
    """
    import time
    
    current_time = time.time()
    window_start = current_time - window_seconds
    
    # Clean old entries
    if client_id in _rate_limit_store:
        _rate_limit_store[client_id] = [
            req_time for req_time in _rate_limit_store[client_id]
            if req_time > window_start
        ]
    else:
        _rate_limit_store[client_id] = []
    
    # Check limit
    request_count = len(_rate_limit_store[client_id])
    
    if request_count >= max_requests:
        log.warning(f"Rate limit exceeded for {client_id}: {request_count}/{max_requests}")
        return False
    
    # Record this request
    _rate_limit_store[client_id].append(current_time)
    return True


def get_client_id(api_key: Optional[str] = None, request_ip: Optional[str] = None) -> str:
    """
    Get client identifier for rate limiting.
    
    Args:
        api_key: API key if available
        request_ip: Client IP address
        
    Returns:
        Client identifier
    """
    # Prefer API key as identifier (more stable)
    if api_key and api_key != "development_mode":
        return f"api_key:{api_key[:8]}..."
    
    # Fallback to IP
    return f"ip:{request_ip or 'unknown'}"


@lru_cache()
def get_rate_limit_config() -> dict:
    """
    Get rate limit configuration from environment.
    
    Returns:
        Dictionary with rate limit settings
    """
    return {
        "max_requests": int(os.environ.get("MAATLANGCHAIN_RATE_LIMIT_REQUESTS", "100")),
        "window_seconds": int(os.environ.get("MAATLANGCHAIN_RATE_LIMIT_WINDOW", "60")),
        "enabled": os.environ.get("MAATLANGCHAIN_RATE_LIMIT_ENABLED", "true").lower() == "true",
    }

