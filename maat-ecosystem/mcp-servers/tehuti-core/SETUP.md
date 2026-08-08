# Tehuti Core Setup Guide

## ✅ Test Results

All core tools are working:
- ✅ `execute_command` - Terminal execution works
- ✅ `get_system_info` - System info works
- ✅ `list_directory` - Directory listing works
- ✅ `read_file` - File reading works
- ⚠️ `query_gitmaat` - Needs psycopg2 (available in WebUI venv)

## 🔧 Dependencies

### Required (for basic tools)
- Python 3.10+
- `mcp` package (FastMCP)

### Optional (for gitMaat queries)
- `psycopg2-binary` (for PostgreSQL connection)
- `PGVECTOR_DB_URL` environment variable

## 🚀 Running in WebUI Context

When registered in Open WebUI, the server will:
1. Use WebUI's venv (has all dependencies)
2. Inherit environment variables (including PGVECTOR_DB_URL)
3. Have access to all tools including gitMaat

## 📝 Next Step: Register in Open WebUI

Add to WebUI's tool server configuration.

