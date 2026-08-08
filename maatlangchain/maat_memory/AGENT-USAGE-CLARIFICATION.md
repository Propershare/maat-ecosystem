# Maat Memory - Agent Usage Clarification

**Question:** When you say "automatic", does the agent automatically do things without being told?

**Answer:** No. Here's what "automatic" means:

---

## ✅ What IS Automatic

**Machine Info Detection:**
- When you call `start_session()`, machine info (hostname, terminal, etc.) is **automatically detected**
- When you call `log_conversation()`, machine info is **automatically detected**
- You don't need to manually pass hostname, terminal ID, etc.

**Example:**
```python
from maat_memory import MaatMemory

memory = MaatMemory()

# You call start_session() - machine info is auto-detected inside
session_id = memory.start_session("cursor", "working on task")
# ↑ Machine info (hostname, terminal, etc.) is automatically detected here
```

---

## ❌ What is NOT Automatic

**Session/Conversation Logging:**
- The agent does **NOT** automatically start sessions
- The agent does **NOT** automatically log conversations
- You must **explicitly call** `start_session()` and `log_conversation()`

**Example:**
```python
# ❌ This does NOT happen automatically:
# memory.start_session("cursor", "working on task")  # Agent doesn't call this automatically

# ✅ You must explicitly call it:
memory = MaatMemory()
session_id = memory.start_session("cursor", "working on task")  # You call this
```

---

## 📝 For Agents (Cursor/OpenCode)

**What You Need to Do:**

1. **Import Maat Memory:**
   ```python
   from maat_memory import MaatMemory
   memory = MaatMemory()
   ```

2. **Explicitly Start Session** (when you start working):
   ```python
   session_id = memory.start_session("your_agent_name", "what you're working on")
   ```

3. **Explicitly Log Conversations** (when you have conversations):
   ```python
   memory.log_conversation(
       agent="your_agent_name",
       user_query="user's question",
       agent_response="your response"
   )
   ```

4. **Explicitly End Session** (when you're done):
   ```python
   memory.end_session("your_agent_name", "summary", ["key points"])
   ```

**What Happens Automatically:**
- Machine info (hostname, terminal, project path) is detected automatically
- You don't need to pass this information manually

---

## 🎯 Summary

| Action | Automatic? | What You Do |
|--------|-----------|-------------|
| Detect machine info | ✅ Yes | Nothing - happens when you call methods |
| Start session | ❌ No | You must call `start_session()` |
| Log conversation | ❌ No | You must call `log_conversation()` |
| End session | ❌ No | You must call `end_session()` |

**"Automatic" = Machine info detection happens automatically**  
**"Not Automatic" = You must explicitly call the methods**

---

**The agent still needs to explicitly use Maat Memory methods. Only the machine info detection is automatic.**

