# RBG Library Integration Documentation

## Tehuti Lab WebUI - Maat-Aligned AI Interface System

### Overview

The RBG Library integration provides structured access to the RBG (Revolutionary Black Genealogy) Library through the Tehuti Lab WebUI tool system. This integration follows the **Maat Constitution** principles with three-ring governance enforcement.

### Maat Foundation Principles

- **Truth (Ma'a)**: Evidence-based access with transparent source attribution and classification metadata
- **Balance (Hetep)**: Resource-aware tool execution with proper error handling and stability
- **Order (Sedjet)**: Structured boundaries through three-ring governance (Middle Ring for RBG)
- **Justice (Rekh)**: Ethical access control with proper permissions and audit trails
- **Self-Reflection (Saa)**: Comprehensive logging and accountability for all operations

---

## Architecture Overview

### Layer Structure

```
Layer 2: Knowledge Layer
├── MaatKnowledge (main interface)
├── MaatMemoryBank (Memory Bank - DONE)
└── MaatRBGLibrary (RBG Library - DONE)

Layer 3: Tool Interface Layer
└── RBG Tools (Tehuti System integration - DONE)
```

### Three-Ring Governance Classification

**RBG Library = MIDDLE RING (Scholarship & Methodology)**

- **Access Pattern**: Read with proposal review required for modifications
- **Source Attribution**: Automatic metadata inclusion
- **Permissions**: User-based access control via TehutiGuard
- **Audit Trail**: Complete operation logging

---

## Tool System Integration

### File: `backend/open_webui/utils/rbg_tools.py`

The RBG Tools module integrates with the **Tehuti System** tool loading pattern:

```python
class Tools:
    def read_rbg_file(self, file_path: str, user: UserModel) -> dict
    def search_rbg_library(self, query: str, limit: int, user: UserModel) -> dict
    def list_rbg_files(self, pattern: str, user: UserModel) -> dict
```

### Integration Flow

1. **Tool Loading**: `plugin.py` → `load_tool_module_by_id()` → `Tools` class discovery
2. **User Context**: `tools.py` → `get_async_tool_function_and_apply_extra_params()` → `user: UserModel`
3. **Policy Enforcement**: `wrap_tool_execution()` → TehutiGuard protection
4. **RBG Access**: `get_maat_rbg_library()` → Three-ring governance
5. **Response**: Dict structure with success/error information

---

## Tool Reference

### 1. read_rbg_file

**Purpose**: Read individual RBG Library files with governance

**Truth (Ma'a)** - Returns content with full source attribution

```python
def read_rbg_file(self, file_path: str, user: UserModel) -> dict:
```

**Parameters**:

- `file_path`: Relative path within RBG Library (e.g., "A-4/Crowley.pdf")
- `user`: User requesting access (auto-injected by Tehuti System)

**Returns**:

```json
{
  "success": true,
  "id": "/path/to/file",
  "title": "File Title.pdf",
  "content": "File content (extracted or placeholder)",
  "source": "/home/suspect/.n8n/jarvis/rbg-library/A-4/File.pdf",
  "classification": "middle",
  "ring_name": "Middle Ring (Scholarship)",
  "metadata": {
    "rbg_library": true,
    "ring": "middle",
    "file_path": "A-4/Crowley.pdf"
  }
}
```

**Justice (Rekh)** - Access denied for \_non-scanned/ directory

```json
{
  "error": "File not found or access denied: _non-scanned/secret.pdf",
  "success": false
}
```

### 2. search_rbg_library

**Purpose**: Search RBG Library content with query matching

**Order (Sedjet)** - Structured search with result limits

```python
def search_rbg_library(self, query: str, limit: int, user: UserModel) -> dict:
```

**Parameters**:

- `query`: Search query string
- `limit`: Maximum results to return (default: 10)
- `user`: User requesting search

**Returns**:

```json
{
  "success": true,
  "count": 3,
  "items": [
    {
      "id": "/path/to/result1",
      "title": "Result 1.pdf",
      "source": "/home/suspect/.n8n/jarvis/rbg-library/...",
      "classification": "middle",
      "ring_name": "Middle Ring (Scholarship)",
      "metadata": { "rbg_library": true }
    }
  ]
}
```

### 3. list_rbg_files

**Purpose**: List available RBG Library files with pattern filtering

**Balance (Hetep)** - Efficient file enumeration with resource awareness

```python
def list_rbg_files(self, pattern: str, user: UserModel) -> dict:
```

**Parameters**:

- `pattern`: File pattern filter (e.g., "_.pdf", "_.json")
- `user`: User requesting listing

**Returns**:

```json
{
  "success": true,
  "count": 1250,
  "files": [
    "A-4/Aleister Crowley - The book of Thoth.pdf",
    "A-4/Alexander Crummell~Afrikan Pastor.pdf",
    "B-2/BLACK-TALK-RADIO-NEWS.pdf"
  ]
}
```

---

## TehutiGuard Integration

### Automatic Policy Enforcement

All RBG tools are automatically protected by **TehutiGuard** through the **Tehuti System**:

```python
# In tools.py - automatic wrapping
result = await wrap_tool_execution(
    tool_id=f"{tool_id}:{function_name}",
    tool_name=function_name,
    user=user,
    arguments=kwargs,
    tool_server_id=None,  # Local tool
    tool_metadata=tool_dict.get("metadata", {}),
    execute_fn=base_callable
)
```

### Policy Checks

- **Classification**: RBG content forced to MIDDLE RING
- **Permissions**: User role-based access verification
- **Resource Limits**: Execution boundaries enforced
- **Audit Logging**: Self-Reflection (Saa) - all operations logged

---

## Error Handling & Self-Reflection (Saa)

### Comprehensive Logging

All tool operations include **Self-Reflection (Saa)** audit trails:

```python
try:
    # Tool execution
    result = perform_operation()
    return {"success": True, "data": result}
except Exception as e:
    log.error(f"Error in RBG operation: {e}")
    return {"error": str(e), "success": False}
```

### Error Categories

1. **Access Denied**: File not found, permission issues
2. **Classification Errors**: Three-ring governance failures
3. **System Errors**: File I/O, encoding issues
4. **Resource Limits**: Timeout, memory constraints

---

## Usage Examples

### Basic File Reading

```python
# Through Tehuti Lab WebUI interface
tools = rbg_tools.Tools()
user = UserModel(id="user123", role="user")

# Read RBG file
result = tools.read_rbg_file("A-4/Crowley.pdf", user)

if result["success"]:
    print(f"Content: {result['content']}")
    print(f"Ring: {result['ring_name']}")
else:
    print(f"Error: {result['error']}")
```

### Search Operations

```python
# Search for specific topics
result = tools.search_rbg_library("Egypt", 5, user)

if result["success"]:
    print(f"Found {result['count']} results:")
    for item in result["items"]:
        print(f"- {item['title']} ({item['ring_name']})")
```

### File Listing

```python
# List PDF files
result = tools.list_rbg_files("*.pdf", user)

if result["success"]:
    print(f"Available files: {result['count']}")
    for file_path in result["files"][:10]:
        print(f"- {file_path}")
```

---

## Security & Compliance

### Three-Ring Governance Enforcement

**Middle Ring (Scholarship) Rules Applied**:

- ✅ **Read Access**: Allowed with user verification
- ✅ **Source Attribution**: Mandatory metadata inclusion
- ✅ **Proposal Requirements**: Modifications need review
- ✅ **Audit Trails**: Complete operation logging

### Justice (Rekh) Protection

- **Directory Restrictions**: `_non-scanned/` access blocked
- **User Permissions**: Role-based access control
- **Content Classification**: Forced Middle Ring assignment
- **Error Boundaries**: Graceful failure handling

---

## Integration Status

### ✅ Completed Components

1. **RBG Library Layer**: `maat_rbg_library.py`
   - Three-ring governance integration
   - PDF and JSON file support
   - \_non-scanned/ directory protection

2. **Tool Interface Layer**: `rbg_tools.py`
   - Tehuti System tool pattern
   - Automatic TehutiGuard protection
   - Maat principles compliance

3. **Tool Loading Integration**
   - `plugin.py` → `load_tool_module_by_id()` support
   - `tools.py` → `wrap_tool_execution()` protection
   - User context injection via `extra_params`

### 🔄 Next Steps

1. **UI Integration**: Add RBG tools to Tehuti Lab WebUI interface
2. **Frontend Components**: Create search/browse interfaces
3. **Advanced Search**: Implement full-text search capabilities
4. **Export Functions**: Add content export with attribution

---

## Conclusion

The RBG Library integration exemplifies **Maat Constitution** principles:

- **Truth (Ma'a)**: Transparent access with source attribution
- **Balance (Hetep)**: Resource-efficient tool execution
- **Order (Sedjet)**: Structured three-ring governance
- **Justice (Rekh)**: Ethical access control and permissions
- **Self-Reflection (Saa)**: Comprehensive audit trails

This integration provides the **Tehuti Lab WebUI** with structured, governed access to the RBG Library while maintaining the highest standards of security, transparency, and accountability.

---

_Documented following Maat Constitution principles for Tehuti Lab WebUI v0.6.5_
