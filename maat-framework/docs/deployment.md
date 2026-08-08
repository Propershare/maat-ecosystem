# Deployment

## Single Machine (Recommended Start)

```bash
# 1. Prerequisites
sudo apt install postgresql postgresql-contrib
# Enable pgvector extension (Ubuntu/Debian)
sudo apt install postgresql-15-pgvector

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:e4b
ollama pull nomic-embed-text

# 2. Set up database
sudo -u postgres createdb maat
sudo -u postgres psql -d maat -f schema/maat_memory.sql

# 3. Set connection string
export PGVECTOR_DB_URL="postgresql://postgres:password@localhost:5432/maat"

# 4. Install Maat
cd maat-framework
pip install -e .

# 5. Run setup
maat setup

# 6. Start
maat start
```

## Systemd Service

```ini
# /etc/systemd/system/maat-agent.service
[Unit]
Description=Maat AI Agent
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=suspect
Environment=PGVECTOR_DB_URL=postgresql://...
WorkingDirectory=/home/suspect/.n8n/maat-framework
ExecStart=/usr/local/bin/maat start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now maat-agent
```

## With OpenClaw (Current Setup)

Maat framework integrates with OpenClaw as a library:

```python
# In OpenClaw's agent loop, use maat.learn for memory
from maat.learn import query_memory, log_conversation
from maat.guard import check_access

# Query memory before responding
context = query_memory("relevant topic")

# Check permissions
access = check_access("openclaw-tehuti", "execute")

# Log the interaction
log_conversation(user_msg, agent_response, agent="openclaw-tehuti")
```

This lets OpenClaw use gitMaat for memory without replacing the whole agent.

## Multi-Machine

For accessing Maat from other machines:

```bash
# Open MCP ports to LAN (firewall)
sudo ufw allow from 192.168.0.0/24 to any port 8014 proto tcp

# Bind MCP servers to 0.0.0.0 instead of 127.0.0.1
# See CLAWD-MCP-ACCESS.md for systemd override examples
```

Remote agents connect to:
```yaml
tools:
  mcp_servers:
    - name: "maat-core"
      url: "http://SERVER_IP:8014"
```

## Environment Variables

| Variable | Description | Required |
|----------|------------|----------|
| `PGVECTOR_DB_URL` | PostgreSQL connection string | Yes (or in config) |
| `OLLAMA_HOST` | Ollama API URL | No (default: localhost:11434) |
| `MAAT_CONFIG` | Override config path | No (default: ~/.maat/config.yaml) |

## Health Check

```bash
maat status
```

Shows:
- Config location and values
- Ollama status and available models
- PostgreSQL connection
- Running MCP servers
