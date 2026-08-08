"""
Maat Agent — Core conversation loop.

Ties together Ollama (model), gitMaat (memory), and Guard (security).
Simple loop: receive message → query memory → call model → log → respond.

Usage:
    from maat.agent import run_agent, one_shot
    from maat.config import load_config

    config = load_config()
    run_agent(config)          # Interactive REPL
    one_shot("hello", config)  # Single message
"""

import json
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from maat.guard import check_access, register_agent, scan_command
from maat.learn import log_conversation, query_memory


# ─── Ollama Client ─────────────────────────────────────────────────

def _call_ollama(
    prompt: str,
    model: str,
    host: str = "http://localhost:11434",
    system: str = "",
    context_messages: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Call Ollama's /api/chat endpoint.

    Args:
        prompt: User message.
        model: Model name (e.g., "gemma4:e4b").
        host: Ollama host URL.
        system: System prompt.
        context_messages: Previous conversation messages.

    Returns:
        Model response text. Empty string on error.
    """
    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    if context_messages:
        messages.extend(context_messages)

    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
    }).encode("utf-8")

    req = Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "")
    except URLError as e:
        print(f"[maat.agent] Ollama error: {e}")
        return ""
    except Exception as e:
        print(f"[maat.agent] Unexpected error calling model: {e}")
        return ""


# ─── System Prompt Builder ─────────────────────────────────────────

def _build_system_prompt(config: Dict[str, Any], memory_context: str = "") -> str:
    """
    Build the system prompt from config + memory context.

    The prompt is kept minimal to save tokens. Memory context is
    injected as "relevant past interactions" so the model has
    awareness without a massive static prompt.
    """
    name = config.get("agent", {}).get("name", "maat")
    personality = config.get("agent", {}).get("personality", "concise and helpful")

    parts = [
        f"You are {name}, a personal AI assistant. You are {personality}.",
        "You have access to the user's memory and tools. Be direct and helpful.",
        "If you don't know something, say so. Don't make things up.",
    ]

    if memory_context:
        parts.append(f"\nRelevant context from memory:\n{memory_context}")

    return "\n".join(parts)


def _get_memory_context(user_message: str, agent_name: str, limit: int = 5) -> str:
    """
    Query gitMaat for relevant past interactions.

    Returns formatted context string, or empty string if nothing found.
    """
    results = query_memory(user_message, agent=agent_name, limit=limit)

    if not results:
        return ""

    lines = []
    for r in results:
        lines.append(f"- User asked: {r['user_query'][:100]}")
        lines.append(f"  Agent said: {r['agent_response'][:150]}")

    return "\n".join(lines)


# ─── Agent Functions ───────────────────────────────────────────────

def one_shot(message: str, config: Dict[str, Any]) -> str:
    """
    Send a single message and get a response.

    Queries memory, builds context, calls model, logs conversation.

    Args:
        message: User's message.
        config: Maat config dict.

    Returns:
        Agent's response text.
    """
    agent_name = config.get("agent", {}).get("name", "maat")
    model = config.get("agent", {}).get("model", "gemma4:e4b")
    host = config.get("ollama", {}).get("host", "http://localhost:11434")
    context_limit = config.get("memory", {}).get("context_limit", 5)

    # Security check
    access = check_access(agent_name, "execute")
    if not access.allowed:
        return f"Access denied: {access.reason}"

    # Query memory for context
    memory_context = _get_memory_context(message, agent_name, limit=context_limit)

    # Build system prompt
    system_prompt = _build_system_prompt(config, memory_context)

    # Call model
    response = _call_ollama(
        prompt=message,
        model=model,
        host=host,
        system=system_prompt,
    )

    if not response:
        return "Sorry, I couldn't generate a response. Is Ollama running?"

    # Log to memory
    log_conversation(message, response, agent=agent_name)

    return response


def run_agent(config: Dict[str, Any]) -> None:
    """
    Run the interactive agent REPL.

    Loops forever reading input, querying memory, calling the model,
    and logging conversations.

    Args:
        config: Maat config dict.
    """
    agent_name = config.get("agent", {}).get("name", "maat")
    model = config.get("agent", {}).get("model", "gemma4:e4b")
    host = config.get("ollama", {}).get("host", "http://localhost:11434")
    context_limit = config.get("memory", {}).get("context_limit", 5)

    # Register the agent with full access
    register_agent(agent_name, "outer-ring")

    # Conversation history (kept in memory for multi-turn)
    history: List[Dict[str, str]] = []

    print(f"💬 {agent_name} is ready. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print(f"\n👋 {agent_name} signing off.")
            break

        # Special commands
        if user_input.startswith("/"):
            _handle_command(user_input, config)
            continue

        # Query memory for context
        memory_context = _get_memory_context(user_input, agent_name, limit=context_limit)

        # Build system prompt
        system_prompt = _build_system_prompt(config, memory_context)

        # Call model with conversation history
        response = _call_ollama(
            prompt=user_input,
            model=model,
            host=host,
            system=system_prompt,
            context_messages=history[-10:],  # Keep last 10 turns
        )

        if response:
            print(f"\n{agent_name}: {response}\n")

            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

            # Log to gitMaat
            log_conversation(user_input, response, agent=agent_name)
        else:
            print(f"\n{agent_name}: [no response — is Ollama running?]\n")


def _handle_command(command: str, config: Dict[str, Any]) -> None:
    """Handle slash commands in the REPL."""
    cmd = command.lower().strip()

    if cmd == "/status":
        from maat.adapt import discover
        system = discover()
        print(f"\n  Model: {config['agent']['model']}")
        print(f"  Ollama: {'✅' if system['ollama']['available'] else '❌'}")
        print(f"  Memory: {config['memory']['backend']}")
        print(f"  MCP: {len(system['mcp_servers'])} servers\n")

    elif cmd == "/memory":
        results = query_memory("", limit=5)
        if results:
            print("\n  Recent memory:")
            for r in results:
                print(f"    {r['agent']}: {r['user_query'][:60]}...")
            print()
        else:
            print("\n  No memory entries yet.\n")

    elif cmd == "/help":
        print("""
  Commands:
    /status  — Show system status
    /memory  — Show recent memory
    /help    — This help
    quit     — Exit
""")
    else:
        print(f"\n  Unknown command: {command}. Try /help\n")
