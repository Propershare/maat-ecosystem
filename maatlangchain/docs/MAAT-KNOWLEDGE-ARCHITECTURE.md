# Maat Knowledge Architecture — Complete

## Foundation

**13 knowledge files organized in a Maat-aligned structure** — Built to last. Built with Maat. Like the pyramids: precise, lasting, community-built, no mediocrity, Maat-guided unity.

## Core Architecture Files

### Design & Entry Points

- **`ARCHITECTURE.md`** — The sacred design document
  - System architecture and design principles
  - Maat-aligned structure and governance
  - Foundation for all knowledge

- **`README.md`** — Entry point for agents
  - Quick start guide
  - Navigation to all knowledge files
  - System overview

- **`AGENT-LIMITATIONS.md`** — System constraints
  - What agents can and cannot do
  - Boundaries and guardrails
  - Safety and security limits

- **`IMPLEMENTATION.md`** — Build guide
  - Step-by-step implementation instructions
  - Setup procedures
  - Configuration details

## Workflow Knowledge

### System Configuration

- **`workflow/system/ports.md`** — Port assignments (8011-8024)
  - MCP server ports
  - Service port mappings
  - Network configuration

- **`workflow/system/systemctl.md`** — Service management
  - systemd service configuration
  - Service lifecycle management
  - Monitoring and health checks

### Tool Documentation

- **`workflow/tools/n8n/patterns.md`** — n8n workflow patterns
  - Common workflow templates
  - Best practices
  - Integration patterns

- **`workflow/tools/mcp/server-setup.md`** — MCP server setup
  - MCP server configuration
  - Tool registration
  - Protocol implementation

- **`workflow/secrets/workflow-tricks.md`** — Time-saving secrets
  - Hidden features
  - Optimization tips
  - Efficiency hacks

## Learnings

### Proven Approaches

- **`learnings/what-works.md`** — Proven approaches
  - Successful patterns
  - Tested solutions
  - Reliable methods

- **`learnings/what-doesnt.md`** — Failed approaches
  - What didn't work
  - Lessons learned
  - Anti-patterns to avoid

- **`learnings/pivots.md`** — When we changed direction
  - Strategic changes
  - Course corrections
  - Evolution of approach

## Design Principles

### Three Pillars of Maat Knowledge

1. **Truth (Maat Memory - PostgreSQL)**
   - Agent decisions and learnings
   - Verified knowledge only
   - Cross-session memory
   - Audit trail

2. **Order (Workflow Files)**
   - System settings documentation
   - Tool documentation
   - Structured knowledge
   - Maintain structure

3. **Balance (Cross-Machine Access)**
   - Webmin/MCP coordination
   - Machine-specific knowledge
   - Essential knowledge only
   - Resource efficiency

### Tehuti-Guard

**Validation layer for knowledge updates:**
- Security and training functions
- Maat compliance checking
- Knowledge verification
- Access control

## Structure

```
memory-bank/
├── ARCHITECTURE.md          (The sacred design)
├── README.md                (Entry point)
├── AGENT-LIMITATIONS.md     (Constraints)
├── IMPLEMENTATION.md         (Build guide)
├── workflow/                (System & tool knowledge)
│   ├── system/              (Ports, systemctl)
│   │   ├── ports.md
│   │   └── systemctl.md
│   ├── tools/               (n8n, MCP, OpenWebUI)
│   │   ├── n8n/
│   │   │   └── patterns.md
│   │   └── mcp/
│   │       └── server-setup.md
│   ├── commands/            (Deployment, maintenance)
│   └── secrets/             (Workflow tricks)
│       └── workflow-tricks.md
├── learnings/               (What works/doesn't, pivots)
│   ├── what-works.md
│   ├── what-doesnt.md
│   └── pivots.md
└── cross-machine/           (Machine-specific knowledge)
```

## Principles

### Maat Principles Applied

1. **Truth**
   - Only verified knowledge
   - Evidence-based documentation
   - Honest assessment of what works/doesn't

2. **Balance**
   - Essential knowledge only
   - No bloat or redundancy
   - Efficient resource usage

3. **Order**
   - Maintain structure
   - Clear organization
   - Consistent patterns

4. **Reciprocity**
   - Share and credit
   - Community-built
   - Collaborative knowledge

## Integration with MaatLangChain

### Shared Infrastructure

The Maat Knowledge Architecture integrates with MaatLangChain through:

1. **PostgreSQL/pgvector**
   - Shared database for knowledge storage
   - Vector embeddings for semantic search
   - Cross-project knowledge access

2. **Maat Memory System**
   - Agent decisions and learnings
   - Cross-session memory
   - Audit trail

3. **Tehuti-Guard**
   - Validation layer
   - Maat compliance checking
   - Security enforcement

### Next Steps

1. **Review ARCHITECTURE.md** — Understand the design
2. **Populate examples** — Add actual n8n workflows, OpenWebUI patterns
3. **Implement MCP server** — Port 8022 for tehuti-memory-bank
4. **Set up Tehuti-Guard** — Validation and security layer

## Foundation Complete

The foundation is complete. Agents now have a clear structure for:
- Workflow knowledge
- Learnings
- Cross-machine coordination
- System configuration
- Tool documentation

**Built to last. Built with Maat.**

