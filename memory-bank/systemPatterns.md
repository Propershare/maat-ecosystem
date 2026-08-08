# Tehuti Lab System Patterns

**Created**: 2025-12-20  
**Purpose**: Architecture patterns, design conventions, and system organization  
**Maat Alignment**: Order in patterns, balance in structure, justice in consistency

## Canonical MAAT doctrine (immune + bounded evolution)

Treat [`docs/MAAT-IMMUNE-SYSTEM.md`](../docs/MAAT-IMMUNE-SYSTEM.md) as **canonical** alongside the product map: distributed self-debugging, anomaly response, constitutional freeze, immune severity levels, first-response ownership per event type, and promotion rules. This is **operational constitution** for agents and humans — not optional philosophy.

For **machine-level** install, drift, and enrollment (sacred vs managed filesystem, gateway protection, `maat setup` / `doctor` / `repair` / `enroll`), use [`docs/MAAT-LAB-CONTROL-PLANE.md`](../docs/MAAT-LAB-CONTROL-PLANE.md).

For **zero-trust** initiation (envelopes, identity, Guard-minimum view, prompt-injection containment, dual containment), use [`docs/MAAT-ZERO-TRUST-AUTONOMY.md`](../docs/MAAT-ZERO-TRUST-AUTONOMY.md).

## Architectural Patterns

### MCP (Model Context Protocol) Pattern

#### Standard MCP Server Structure
```python
#!/usr/bin/env python3
"""
Tehuti [Service] MCP Server
Maat-aligned [purpose] server
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

# Standard logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("[service_name].log"),
        logging.StreamHandler(sys.stderr),
    ],
)

logger = logging.getLogger("[service_name]")

# Standard TOOLS registry pattern
TOOLS = {
    "tehuti-[service]/[action]": {
        "name": "tehuti-[service]/[action]",
        "description": "[Clear description of what the tool does]",
        "inputSchema": {
            "type": "object",
            "properties": {
                "[parameter]": {
                    "type": "string|integer|object",
                    "description": "[Parameter description]",
                    "required": false|true
                }
            },
            "required": ["[required_parameters]"]
        },
    },
}

# Standard server class pattern
class [Service]Server:
    """Server for [service purpose] following Maat principles."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with optional configuration."""
        self.setup_logging()
        self.load_configuration(config_path)
        logger.info(f"Initialized Tehuti-{[Service]} MCP server")
    
    def [tool_method](self, [parameters]) -> Dict[str, Any]:
        """
        Execute [action] with Maat-aligned error handling.
        
        Args:
            [parameter]: Description
            
        Returns:
            Dict with 'status' and 'data'/'error' keys
        """
        try:
            # Implementation logic
            logger.info(f"Executing [action] with {[parameters]}")
            result = {"status": "success", "data": result_data}
            return result
        except Exception as e:
            logger.error(f"Error in [action]: {str(e)}")
            return {"status": "error", "message": str(e)}

# Standard MCP protocol handlers
def handle_initialize(request_id: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "Tehuti-[Service]", "version": "1.0"},
            "capabilities": {"tools": TOOLS},
        },
    }

def handle_list_tools(request_id: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": list(TOOLS.values())},
    }

def handle_call_tool(server: [Service]Server, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})
    try:
        if name == "tehuti-[service]/[action]":
            result = server.[tool_method](**args)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {name}"},
            }

        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "json", "json": result}]}}
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)},
        }

def main():
    server = [Service]Server()
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            method = data.get("method")
            req_id = data.get("id")

            if method == "initialize":
                response = handle_initialize(req_id)
            elif method == "tools/list":
                response = handle_list_tools(req_id)
            elif method == "tools/call":
                response = handle_call_tool(server, req_id, data.get("params", {}))
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}), flush=True)

if __name__ == "__main__":
    main()
```

#### MCP Service Standardization Pattern
1. **File Naming**: `tehuti_[service]_server.py`
2. **Port Allocation**: Sequential ports starting from 8011
3. **Tool Naming**: `tehuti-[service]/[action]`
4. **Logging**: Consistent format with service name
5. **Error Handling**: Standard JSON response format
6. **Configuration**: Optional JSON/YAML config support

### Service Management Pattern

#### systemd Service Template
```ini
[Unit]
Description=mcpo bridge for Tehuti [Service] MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
Environment="PYTHONPATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port [PORT] -- python3 tehuti_[service]_server.py
StandardOutput=null
StandardError=journal
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Service Naming Convention
- **Service Files**: `mcpo-tehuti-[service].service`
- **Description**: "mcpo bridge for Tehuti [Service] MCP server"
- **Port Allocation**: Documented in service files and docs
- **Environment**: Consistent PYTHONPATH and working directory

### OpenAPI Documentation Pattern

#### Standard OpenAPI Structure
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Tehuti-[Service]",
    "description": "Tehuti-[Service] MCP Server",
    "version": "1.0"
  },
  "paths": {
    "/tehuti-[service]/[action]": {
      "post": {
        "summary": "Tehuti-[Service]/[Action]",
        "description": "[Clear description]",
        "operationId": "tool_tehuti_[service]_[action]_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "[parameter]": {
                    "type": "string|integer|object",
                    "description": "[Description]"
                  }
                },
                "required": ["[required_params]"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    }
  }
}
```

## Configuration Patterns

### Environment Variable Pattern

#### Standard Environment Files
```bash
# /home/suspect/.n8n/tehuti-config/secrets/.env
# Environment configuration for Tehuti Lab
# Generated: [DATE]
# Permissions: 600 (owner read only)

# Database Configuration
POSTGRES_URL=postgresql://suspect:[PASSWORD]@localhost:5432/jarvis
POSTGRES_USER=suspect
POSTGRES_DB=jarvis

# Service Ports
OPENWEBUI_PORT=3000
N8N_PORT=5678
OLLAMA_PORT=11434
SEARXNG_PORT=8080

# MCP Port Range
MCP_PORT_START=8011
MCP_PORT_END=8019

# API Keys (secure storage)
NGINX_TOOL_API_KEY=[API_KEY]
N8N_API_KEY=[JWT_TOKEN]
GEMINI_API_KEY=[API_KEY_IF_NEEDED]

# File Paths
PROJECT_ROOT=/home/suspect/.n8n
MCP_SERVERS_PATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP
LOG_PATH=/var/log/tehuti

# Security
CORS_ORIGINS=http://localhost:3000,https://n8ndocumentation.aiservices.pl
RATE_LIMIT_REQUESTS_PER_SECOND=10
```

#### Configuration Loading Pattern
```python
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    return {
        "postgres_url": os.getenv("POSTGRES_URL", "postgresql://suspect:suspect@localhost:5432/jarvis"),
        "postgres_user": os.getenv("POSTGRES_USER", "suspect"),
        "postgres_db": os.getenv("POSTGRES_DB", "jarvis"),
        "openwebui_port": int(os.getenv("OPENWEBUI_PORT", "3000")),
        "n8n_port": int(os.getenv("N8N_PORT", "5678")),
        "ollama_port": int(os.getenv("OLLAMA_PORT", "11434")),
        "searxng_port": int(os.getenv("SEARXNG_PORT", "8080")),
        "project_root": os.getenv("PROJECT_ROOT", "/home/suspect/.n8n"),
        "log_path": os.getenv("LOG_PATH", "/var/log/tehuti"),
        "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        "rate_limit": int(os.getenv("RATE_LIMIT_REQUESTS_PER_SECOND", "10")),
    }
```

### OpenWebUI Tools Configuration Pattern

#### External Tools Template
```json
{
  "id": "tehuti-[service]-tools",
  "name": "Tehuti [Service] Tools",
  "description": "[Clear description of what these tools do and their purpose]",
  "type": "openapi",
  "url": "http://127.0.0.1:[PORT]",
  "visibility": "public|private",
  "auth": {
    "type": "none|bearer",
    "bearer": "[API_KEY_IF_NEEDED]"
  }
}
```

## Data Patterns

### Database Schema Pattern

#### Standard Table Structure
```sql
-- Entity Table Pattern
CREATE TABLE [entities] (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    maat_verified BOOLEAN DEFAULT FALSE
);

-- Relationship Table Pattern  
CREATE TABLE [relationships] (
    id SERIAL PRIMARY KEY,
    source_entity_id INTEGER REFERENCES [entities](id),
    target_entity_id INTEGER REFERENCES [entities](id),
    relationship_type VARCHAR(100) NOT NULL,
    strength DECIMAL(3,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by VARCHAR(100),
    UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

-- Audit Log Pattern
CREATE TABLE [audit_logs] (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    maat_compliance BOOLEAN DEFAULT TRUE
);
```

#### Index Pattern
```sql
-- Standard indexes for performance
CREATE INDEX idx_[table]_type ON [table](type);
CREATE INDEX idx_[table]_created_at ON [table](created_at);
CREATE INDEX idx_[table]_updated_at ON [table](updated_at);
CREATE INDEX idx_[table]_created_by ON [table](created_by);
CREATE INDEX idx_relationships_source ON relationships(source_entity_id);
CREATE INDEX idx_relationships_target ON relationships(target_entity_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_changed_at ON audit_logs(changed_at);
```

### API Response Patterns

#### Success Response Pattern
```python
def success_response(data: Any, message: str = "Operation completed successfully") -> Dict[str, Any]:
    """Standard success response following Maat transparency."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "maat_compliant": True,
        "attribution": {
            "source": "Tehuti Lab",
            "method": "MCP Protocol",
            "version": "1.0"
        }
    }
```

#### Error Response Pattern
```python
def error_response(message: str, error_code: str = "UNKNOWN", details: Dict = None) -> Dict[str, Any]:
    """Standard error response with Maat transparency."""
    return {
        "status": "error", 
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat(),
        "maat_compliant": False,
        "attribution": {
            "source": "Tehuti Lab",
            "method": "MCP Protocol", 
            "version": "1.0"
        },
        "details": details or {},
        "suggestions": [
            "Check the input parameters",
            "Verify service configuration",
            "Review the Maat compliance checklist",
            "Consult the documentation"
        ]
    }
```

## Documentation Patterns

### File Organization Pattern

#### Standard Directory Structure
```
/home/suspect/.n8n/
├── mcp-servers/                    # MCP server implementations
│   └── ImhotepMCP/pythonMCP/       # Python MCP servers
├── docs/                           # System documentation
│   ├── tehuti/                     # Core system docs
│   ├── mcp/                        # MCP server documentation  
│   ├── n8n/                        # n8n workflow documentation
│   ├── openwebui/                  # OpenWebUI documentation
│   ├── governance/                 # Maat governance docs
│   ├── recovery/                   # Recovery procedures
│   ├── setup/                      # Setup guides
│   └── status/                    # Status documentation
├── memory-bank/                    # Current state and context
├── tehuti-config/                  # Configuration files
│   └── secrets/                    # Secure configuration
├── jarvis/                         # Legacy compatibility
├── openspec/                       # Change management
└── scripts/                       # Utility scripts
```

#### Documentation File Naming
- **Core docs**: `UPPERCASE-KEBAB-CASE.md`
- **Memory Bank**: `lowercase-kebab-case.md`
- **Setup docs**: `COMPONENT-SETUP.md`
- **Recovery docs**: `COMPONENT-RECOVERY.md`
- **Status docs**: `STATUS-SUMMARY.md`

### README Pattern

#### Component Documentation Template
```markdown
# [Component Name]

## Purpose
[Brief description of component purpose and role in Tehuti Lab]

## Architecture
[High-level architecture description with diagram if possible]

## Dependencies
[List of required services, libraries, and systems]

## Configuration
[Configuration requirements and environment variables]

## API Documentation
[API endpoints, tools, or interface documentation]

## Usage Examples
[Practical usage examples and common workflows]

## Troubleshooting
[Common issues and solutions]

## Maat Compliance
[How this component follows Maat principles]

## Dependencies and Attribution
[List of all dependencies and their attributions]
```

## Security Patterns

### Authentication Pattern

#### Bearer Token Pattern
```python
def verify_bearer_token(request: Request, expected_token: str) -> bool:
    """Verify bearer token with Maat security principles."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    return token == expected_token

def rate_limit_check(client_ip: str, limit: int, window: int = 60) -> bool:
    """Rate limiting following Maat balance principles."""
    key = f"rate_limit:{client_ip}"
    current_count = redis.get(key)
    
    if current_count and int(current_count) >= limit:
        return False
    
    redis.incr(key)
    redis.expire(key, window)
    return True
```

### Secret Management Pattern

#### Secure Configuration Pattern
```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    """Secure configuration manager following Maat justice principles."""
    
    def __init__(self, master_key: str):
        self.cipher = Fernet(master_key.encode())
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt secret for storage."""
        return self.cipher.encrypt(secret.encode()).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt secret from storage."""
        return self.cipher.decrypt(encrypted_secret.encode()).decode()
    
    def get_secret(self, key: str) -> str:
        """Get secret from environment with decryption."""
        encrypted_value = os.getenv(key)
        if encrypted_value:
            return self.decrypt_secret(encrypted_value)
        raise ValueError(f"Secret {key} not found in environment")
```

## Testing Patterns

### Unit Test Pattern

#### Standard Test Structure
```python
import unittest
import json
from unittest.mock import Mock, patch
from tehuti_[service]_server import [Service]Server, success_response, error_response

class Test[Service]Server(unittest.TestCase):
    """Test [Service] server following Maat truth principles."""
    
    def setUp(self):
        """Set up test environment."""
        self.server = [Service]Server()
    
    def test_[method]_success(self):
        """Test successful [method] execution."""
        # Arrange
        test_params = {"param1": "value1", "param2": "value2"}
        
        # Act
        result = self.server.[method](**test_params)
        
        # Assert
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertTrue(result["maat_compliant"])
    
    def test_[method]_error_handling(self):
        """Test [method] error handling with Maat transparency."""
        # Arrange
        invalid_params = {"invalid": "params"}
        
        # Act
        result = self.server.[method](**invalid_params)
        
        # Assert
        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)
        self.assertIn("suggestions", result)
        self.assertFalse(result["maat_compliant"])
    
    def test_[method]_attribution(self):
        """Test [method] includes proper attribution following Maat justice."""
        # Arrange
        test_params = {"param1": "value1"}
        
        # Act
        result = self.server.[method](**test_params)
        
        # Assert
        self.assertIn("attribution", result)
        self.assertEqual(result["attribution"]["source"], "Tehuti Lab")
```

### Integration Test Pattern

#### MCP Protocol Test
```python
import requests
import json

class TestMCPIntegration:
    """Integration tests for MCP servers following Maat order principles."""
    
    def setup_method(self):
        """Set up test environment."""
        self.base_url = "http://127.0.0.1:[PORT]"
        self.headers = {"Content-Type": "application/json"}
    
    def test_openapi_spec_available(self):
        """Test OpenAPI spec is available and valid."""
        response = requests.get(f"{self.base_url}/openapi.json")
        assert response.status_code == 200
        
        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
    
    def test_tool_execution(self):
        """Test tool execution through MCP protocol."""
        # Test initialization
        init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        init_response = requests.post(self.base_url, json=init_request, headers=self.headers)
        assert init_response.status_code == 200
        
        # Test tool list
        tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        tools_response = requests.post(self.base_url, json=tools_request, headers=self.headers)
        assert tools_response.status_code == 200
        
        tools = tools_response.json()["result"]["tools"]
        assert len(tools) > 0
```

## Deployment Patterns

### Docker Container Pattern

#### Standard Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user following Maat justice principles
RUN useradd -m -u 1000 tehuti && chown -R tehuti:tehuti /app
USER tehuti

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:[PORT]/openapi.json || exit 1

# Expose port
EXPOSE [PORT]

# Start application
CMD ["python3", "tehuti_[service]_server.py"]
```

### Service Deployment Pattern

#### Deployment Checklist
```yaml
# deployment-checklist.yml
deployment:
  pre-deployment:
    - [ ] Backup current configuration
    - [ ] Verify all dependencies are installed
    - [ ] Test current system state is healthy
    - [ ] Review Maat compliance checklist
  
  deployment:
    - [ ] Stop services safely
    - [ ] Update configuration files
    - [ ] Deploy new code/images
    - [ ] Start services in dependency order
    - [ ] Verify each service responds correctly
  
  post-deployment:
    - [ ] Run full test suite
    - [ ] Verify documentation accuracy
    - [ ] Update monitoring dashboards
    - [ ] Notify stakeholders of changes
    - [ ] Update documentation as needed
```

---

**These system patterns provide the foundation for consistent, Maat-aligned development across all Tehuti Lab components. All new development should follow these established patterns.**