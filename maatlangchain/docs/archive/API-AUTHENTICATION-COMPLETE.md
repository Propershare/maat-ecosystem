# API Authentication & Security - Complete ✅

## Summary

Added production-ready authentication and security features to MaatLangChain API following Maat principles.

## What Was Added

### 1. API Key Authentication (`api/auth.py`)
- ✅ API key verification via `X-API-Key` header
- ✅ Environment variable configuration (`MAATLANGCHAIN_API_KEY`)
- ✅ Development mode (no key required if not configured)
- ✅ Constant-time comparison (prevents timing attacks)
- ✅ Secure key generation utility

### 2. Rate Limiting (`api/middleware.py`)
- ✅ Per-client rate limiting (by API key or IP)
- ✅ Configurable limits (default: 100 requests/60 seconds)
- ✅ In-memory storage (can upgrade to Redis)
- ✅ Rate limit headers in responses
- ✅ 429 status code when exceeded

### 3. Security Headers (`api/middleware.py`)
- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Strict-Transport-Security` header
- ✅ Server header removal

### 4. Request Logging (`api/middleware.py`)
- ✅ Request/response logging
- ✅ Process time tracking
- ✅ Client IP and User-Agent logging
- ✅ Error logging with context

## Configuration

### Environment Variables

```bash
# API Key (required for production)
export MAATLANGCHAIN_API_KEY="your-secure-api-key-here"

# Require API key (default: false - allows development mode)
export MAATLANGCHAIN_API_KEY_REQUIRED="true"

# Rate Limiting
export MAATLANGCHAIN_RATE_LIMIT_ENABLED="true"  # default: true
export MAATLANGCHAIN_RATE_LIMIT_REQUESTS="100"  # default: 100
export MAATLANGCHAIN_RATE_LIMIT_WINDOW="60"    # default: 60 seconds
```

### Generate API Key

```python
from api.auth import generate_api_key

# Generate a secure API key
api_key = generate_api_key()
print(f"Your API key: {api_key}")
```

## Usage

### With API Key

```bash
# Set API key
export MAATLANGCHAIN_API_KEY="your-api-key-here"

# Make authenticated request
curl -X POST "http://localhost:8000/rag/query" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Maat?"}'
```

### Development Mode

If `MAATLANGCHAIN_API_KEY` is not set`, API works without authentication (development mode).

```bash
# No API key needed in development
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Maat?"}'
```

## Protected Endpoints

All RAG endpoints now require authentication (unless in development mode):

- ✅ `POST /rag/query` - RAG queries
- ✅ `POST /rag/chunks` - View chunks
- ✅ `POST /rag/ingest_pdf` - PDF ingestion
- ✅ `GET /rag/stats` - Statistics
- ✅ `GET /rag/collections` - List collections

### Public Endpoints (No Auth Required)

- ✅ `GET /` - Root endpoint
- ✅ `GET /health` - Health check
- ✅ `GET /openapi.json` - OpenAPI spec
- ✅ `GET /docs` - Swagger UI

## Rate Limiting

### Default Limits
- **100 requests per 60 seconds** per client (API key or IP)

### Rate Limit Headers

Responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Window: 60
```

### Rate Limit Exceeded

When limit is exceeded, returns `429 Too Many Requests`:

```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per 60 seconds."
}
```

## Security Features

### 1. API Key Security
- Constant-time comparison (prevents timing attacks)
- Secure key generation using `secrets.token_urlsafe()`
- Optional requirement (development vs production)

### 2. Security Headers
- Prevents MIME type sniffing
- Prevents clickjacking
- XSS protection
- HSTS for HTTPS

### 3. Request Logging
- Audit trail for all requests
- Client identification
- Process time tracking
- Error logging

## Files Modified

1. **`api/main.py`**
   - Added authentication dependencies to endpoints
   - Added security middleware
   - Preserved all existing functionality

2. **`api/auth.py`** (NEW)
   - API key verification
   - Rate limiting logic
   - Client identification

3. **`api/middleware.py`** (NEW)
   - Security headers middleware
   - Rate limiting middleware
   - Request logging middleware

## Testing

### Test Authentication

```python
import requests

# Without API key (should work in dev mode)
response = requests.post("http://localhost:8000/rag/query", json={
    "question": "What is Maat?"
})
print(response.status_code)  # Should be 200 in dev mode

# With invalid API key (should fail if required)
response = requests.post(
    "http://localhost:8000/rag/query",
    headers={"X-API-Key": "invalid-key"},
    json={"question": "What is Maat?"}
)
print(response.status_code)  # Should be 401 if required
```

### Test Rate Limiting

```python
import requests

# Make 101 requests quickly
for i in range(101):
    response = requests.post("http://localhost:8000/rag/query", json={
        "question": f"Test {i}"
    })
    if response.status_code == 429:
        print(f"Rate limited at request {i+1}")
        break
```

## Production Deployment

### Recommended Settings

```bash
# Require API key
export MAATLANGCHAIN_API_KEY_REQUIRED="true"

# Set secure API key
export MAATLANGCHAIN_API_KEY="$(python3 -c 'from api.auth import generate_api_key; print(generate_api_key())')"

# Enable rate limiting
export MAATLANGCHAIN_RATE_LIMIT_ENABLED="true"
export MAATLANGCHAIN_RATE_LIMIT_REQUESTS="100"
export MAATLANGCHAIN_RATE_LIMIT_WINDOW="60"
```

### Upgrade Rate Limiting

For production at scale, consider upgrading to Redis-based rate limiting:

```python
# Future: Replace in-memory storage with Redis
# from redis import Redis
# redis_client = Redis(host='localhost', port=6379)
```

## Maat Principles Applied

- **Truth**: Secure, verified authentication
- **Balance**: Minimal overhead, efficient middleware
- **Order**: Standard patterns, well-documented
- **Self-Reflection**: Comprehensive logging and monitoring

## Status

✅ **COMPLETE** - API authentication and security features ready for production!

---

**Next Steps:**
- Test with OC1's RAG chain integration
- Consider Redis for distributed rate limiting
- Add API key rotation mechanism
- Add request signing for additional security

