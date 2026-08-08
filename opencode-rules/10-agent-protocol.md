# OpenCode Agent Protocol — Standard Agents

## 🤖 Standard Agents

### opencode_assistant
- **Role**: Main coding and development agent
- **Capabilities**: Code generation, file operations, debugging, analysis
- **MAAT Functions**: `memory.start_session()`, `memory.log_event()`
- **Auto-Reporting**: Session start/end, task completion

### opencode_analyzer
- **Role**: Code review and security analysis
- **Capabilities**: Code analysis, security scanning, performance analysis
- **MAAT Functions**: Constitutional validation of code changes
- **Auto-Reporting**: Analysis results, compliance metrics

### opencode_orchestrator
- **Role**: Task coordination and workflow management
- **Capabilities**: Multi-agent coordination, task distribution
- **MAAT Functions**: Cross-agent communication, workflow logging
- **Auto-Reporting**: Agent status, task completion tracking

### opencode_monitor
- **Role**: System monitoring and health checks
- **Capabilities**: Performance tracking, error detection, system status
- **MAAT Functions**: System health monitoring, constitutional compliance
- **Auto-Reporting**: System metrics, health reports

## 🔄 Auto-Reporting Protocol
1. **Session Start**: `memory.start_session(agent_id)` on any agent activity
2. **Event Logging**: `memory.log_event(event_type, data)` for all operations
3. **Constitutional Validation**: All entries validated against 5 MAAT articles
4. **Cross-Agent Communication**: Shared memory for agent coordination
5. **Persistent State**: Session data maintained across restarts

## 🏛️ MAAT Constitution Compliance
- **Truth (Khet)**: Accurate representation of data
- **Balance (Maat)**: Equitable distribution of memory
- **Order (Nfr)**: Logical structure and retrieval
- **Justice (Sia)**: Fair and proportional access
- **Self-Reflection (Heka)**: System awareness and improvement

## 📚 MAAT Memory System Integration
- **Database**: PostgreSQL via `PGVECTOR_DB_URL` (auto-detect from `~/.n8n/.env.broker`)
- **Fallback**: JSON store under `~/.opencode-rules/.memory/`
- **Usage**: `from maat_memory import MaatMemory`
- **Required provenance**: every `log_*` call needs `origin=` (e.g. `agent_authored`)

## 🎯 Project Integration
- **OC1 (MaatLangChain)**: `/home/suspect/.n8n/maatlangchain`
- **OC2 (Tehuti Memory)**: `/mnt/ai_backup/tehuti-memory`
- Project-specific doctrine: read the project's `AGENTS.md`
