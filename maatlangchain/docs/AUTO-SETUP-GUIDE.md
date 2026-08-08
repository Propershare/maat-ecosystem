# Auto-Setup System Guide

## 🎯 Overview

**Zero-Config System:** Agents automatically configure themselves when they load the project. No user intervention needed.

## 🚀 How It Works

### 1. Agent Loads Project

When an agent (Cursor or OpenCode) loads this project:

```python
# Auto-setup runs automatically on import
from maat_memory import MaatMemory
# ✅ Auto-setup complete - project configured
```

### 2. What Auto-Setup Does

**Automatically:**
- ✅ Detects project root (looks for `AGENTS.md` or `maatlangchain/` directory)
- ✅ Adds project to Python path
- ✅ Detects machine and terminal info
- ✅ Gets unique agent ID
- ✅ Validates project structure
- ✅ Detects conflicts
- ✅ Validates Maat compliance
- ✅ Tests Maat Memory connection

### 3. Manual Setup Check (Optional)

If you want to see the setup report:

```python
from maat_memory import run_auto_setup

# Get detailed report
report = run_auto_setup("opencode", verbose=True)

# Report shows:
# - Project root detected
# - Agent ID assigned
# - Structure validated
# - Conflicts detected
# - Maat compliance checked
# - Memory system status
```

## 🏗️ Building Core Components

### Using Maat Standards

When building new components, use the standards validator:

```python
from maat_memory import MaatStandards
from pathlib import Path

# Check for conflicts before creating
component_name = "my_component"
project_root = Path("/home/suspect/.n8n/maatlangchain")

conflicts = MaatStandards.check_conflicts(component_name, project_root)
if conflicts["conflicts"]:
    print(f"⚠️  Conflicts: {conflicts['conflicts']}")
    # Agent resolves or uses different name
else:
    print("✅ No conflicts - safe to create")

# Generate template following Maat standards
template = MaatStandards.generate_component_template(
    component_name,
    component_type="standard"  # or "governance", "integration", "api"
)

# Create component from template
# (agent creates files following template structure)
```

### Component Types

**Standard Component:**
- General purpose component
- Follows standard structure
- Includes logging, error handling, validation

**Governance Component:**
- Maat governance (three-ring, TehutiGuard, etc.)
- Includes policy validation
- Includes audit logging

**Integration Component:**
- External system integration (PostgreSQL, Redis, Ollama)
- Includes connection management
- Includes health checks

**API Component:**
- API endpoints
- Includes request/response handling
- Includes validation

### Validation

After creating a component, validate it:

```python
from maat_memory import MaatStandards
from pathlib import Path

component_path = Path("/home/suspect/.n8n/maatlangchain/core/my_component")

# Validate structure
structure = MaatStandards.validate_component_structure(component_path)
if not structure["valid"]:
    print(f"❌ Structure issues: {structure['issues']}")
    # Agent fixes issues

# Validate Maat compliance
main_file = component_path / "my_component.py"
if main_file.exists():
    code = main_file.read_text()
    compliance = MaatStandards.validate_maat_compliance(code, main_file)
    print(f"Compliance: {compliance['compliance']}")
```

## 🔧 Conflict Resolution

### Automatic Conflict Detection

Auto-setup automatically detects:
- Duplicate component names
- Missing required files
- Configuration conflicts
- Missing required files
- Python path issues

### Agent Resolution

**Agents automatically:**
1. **Detect conflicts** - Auto-setup reports them
2. **Resolve conflicts** - Remove old files, fix structure
3. **Report actions** - Log what was fixed
4. **Maintain Maat compliance** - Ensure fixes follow principles

### Manual Conflict Check

```python
from maat_memory import MaatAutoSetup

setup = MaatAutoSetup()
conflicts = setup.detect_conflicts()

if conflicts["conflicts"]:
    print(f"⚠️  Conflicts: {conflicts['conflicts']}")
    print(f"💡 Recommendations: {conflicts['recommendations']}")
    # Agent resolves conflicts
```

## ✅ Maat Compliance

### Automatic Validation

Auto-setup validates Maat compliance:
- **Truth:** Accurate configuration, proper validation
- **Balance:** No conflicts, efficient resource usage
- **Order:** Correct structure, proper organization
- **Justice:** Fair access, proper permissions
- **Self-Reflection:** Proper logging, error handling

### Manual Compliance Check

```python
from maat_memory import MaatAutoSetup

setup = MaatAutoSetup()
compliance = setup.validate_maat_compliance()

print("Truth:", compliance["truth"])
print("Balance:", compliance["balance"])
print("Order:", compliance["order"])
print("Justice:", compliance["justice"])
print("Self-Reflection:", compliance["self_reflection"])
```

## 📋 Agent Workflow

### Standard Workflow

1. **Load project** - Agent reads `AGENTS.md`
2. **Auto-setup runs** - Automatic configuration
3. **Get unique ID** - Auto-detected
4. **Check task** - Read `PROMPT-NEXT-ACTION.md`
5. **Build component** - Use `MaatStandards` to ensure compliance
6. **Validate** - Check structure and compliance
7. **Use Maat Memory** - Log sessions, conversations, tasks

### Building New Component

```python
from maat_memory import MaatStandards, get_unique_agent_id, MaatMemory
from pathlib import Path

# 1. Get unique agent ID
agent_id = get_unique_agent_id("opencode")

# 2. Check for conflicts
component_name = "my_component"
conflicts = MaatStandards.check_conflicts(component_name, Path.cwd())
if conflicts["conflicts"]:
    # Resolve or use different name
    pass

# 3. Generate template
template = MaatStandards.generate_component_template(
    component_name,
    component_type="standard"
)

# 4. Create component from template
# (agent creates files)

# 5. Validate
component_path = Path(f"core/{component_name}")
structure = MaatStandards.validate_component_structure(component_path)
compliance = MaatStandards.validate_maat_compliance(
    (component_path / f"{component_name.lower()}.py").read_text(),
    component_path / f"{component_name.lower()}.py"
)

# 6. Log to Maat Memory
memory = MaatMemory()
memory.log_conversation(
    agent=agent_id,
    user_query="Built new component",
    agent_response=f"Created {component_name} following Maat standards"
)
```

## 🚫 What NOT to Do

- ❌ Don't manually configure paths - auto-setup handles it
- ❌ Don't use generic agent IDs - auto-detected unique IDs
- ❌ Don't create legacy memory systems - use Maat Memory only
- ❌ Don't break Maat compliance - validation prevents it
- ❌ Don't create conflicts - detection prevents it
- ❌ Don't skip validation - always validate new components

## 💡 Tips

1. **Always check conflicts** before creating new components
2. **Use templates** - `MaatStandards.generate_component_template()` ensures compliance
3. **Validate after creation** - Check structure and compliance
4. **Log to Maat Memory** - Track what you build
5. **Follow existing patterns** - Check `core/` for examples

---

**Remember:** This is a **zero-config system**. Agents handle everything automatically while maintaining Maat principles.

