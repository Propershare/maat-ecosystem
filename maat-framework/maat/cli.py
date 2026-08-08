"""
Maat CLI — One command to rule them all.

Usage:
    maat setup          # Interactive first-run setup
    maat start          # Start the agent
    maat status         # Show what's running
    maat adapt          # Re-scan system, update config
    maat chat "hello"   # One-shot message
    maat learn          # Generate training data from logs
    maat guard --check  # Audit security posture
    maat config get <key>
    maat config set <key> <value>
"""

import argparse
import sys
from typing import List, Optional


def cmd_setup(args: argparse.Namespace) -> None:
    """Interactive first-run setup."""
    from maat.adapt import auto_configure, discover
    from maat.config import CONFIG_PATH, save_config

    print("🔧 Maat Setup\n")
    print("Scanning your system...\n")

    system = discover()

    # Show what was found
    ollama = system["ollama"]
    if ollama["available"]:
        print(f"  ✅ Ollama: {len(ollama['models'])} models")
    else:
        print("  ⚠️  Ollama not found. Install from https://ollama.com")

    servers = system["mcp_servers"]
    print(f"  {'✅' if servers else '⚠️ '} MCP Servers: {len(servers)} running")

    pg = system["postgres"]
    if pg["available"]:
        print(f"  ✅ PostgreSQL connected")
    else:
        print("  ⚠️  PostgreSQL not found. Memory will use JSON fallback.")

    # Auto-configure
    print("\nGenerating config...")
    config = auto_configure(save=True)

    print(f"\n  Agent:    {config['agent']['name']}")
    print(f"  Model:    {config['agent']['model']}")
    print(f"  Memory:   {config['memory']['backend']}")
    print(f"  Security: {config['security']['governance']}")
    print(f"  Tools:    {len(config['tools']['mcp_servers'])} MCP servers")
    print(f"\n  Config saved to: {CONFIG_PATH}")
    print("\n✅ Setup complete. Run 'maat start' to begin.")


def cmd_start(args: argparse.Namespace) -> None:
    """Start the agent."""
    from maat.agent import run_agent
    from maat.config import load_config

    config = load_config()
    print(f"🚀 Starting Maat agent ({config['agent']['name']})...")
    print(f"   Model: {config['agent']['model']}")
    print(f"   Memory: {config['memory']['backend']}")
    print(f"   Tools: {len(config['tools'].get('mcp_servers', []))} MCP servers")
    print()

    try:
        run_agent(config)
    except KeyboardInterrupt:
        print("\n\n👋 Maat agent stopped.")


def cmd_status(args: argparse.Namespace) -> None:
    """Show system status."""
    from maat.adapt import discover
    from maat.config import CONFIG_PATH, load_config

    config = load_config()
    system = discover()

    print("📊 Maat Status\n")
    print(f"  Config:   {CONFIG_PATH}")
    print(f"  Agent:    {config['agent']['name']}")
    print(f"  Model:    {config['agent']['model']}")
    print(f"  Memory:   {config['memory']['backend']}")
    print(f"  Security: {config['security']['governance']}")

    print(f"\n  Ollama:   {'✅ running' if system['ollama']['available'] else '❌ down'}")
    print(f"  Postgres: {'✅ running' if system['postgres']['available'] else '❌ down'}")
    print(f"  MCP:      {len(system['mcp_servers'])} servers running")

    for s in system["mcp_servers"]:
        print(f"            {s['name']:20} → {s['url']}")


def cmd_adapt(args: argparse.Namespace) -> None:
    """Re-scan system and update config."""
    from maat.adapt import auto_configure

    print("🔍 Scanning system...\n")
    config = auto_configure(save=True)

    print(f"  Model:  {config['agent']['model']}")
    print(f"  Tools:  {len(config['tools']['mcp_servers'])} MCP servers")
    print(f"  Models: {len(config['ollama']['models'])} Ollama models")
    print("\n✅ Config updated.")


def cmd_chat(args: argparse.Namespace) -> None:
    """One-shot chat message."""
    from maat.agent import one_shot
    from maat.config import load_config

    config = load_config()
    message = " ".join(args.message)

    if not message:
        print("Usage: maat chat \"your message here\"")
        sys.exit(1)

    response = one_shot(message, config)
    print(response)


def cmd_learn(args: argparse.Namespace) -> None:
    """Show recent memory / learning stats."""
    from maat.learn import get_recent_tasks, query_memory

    print("📚 Maat Learn — Recent Activity\n")

    tasks = get_recent_tasks(limit=5)
    if tasks:
        print("  Recent tasks:")
        for t in tasks:
            status_icon = {"pending": "⏳", "completed": "✅", "in_progress": "🔄"}.get(t["status"], "•")
            print(f"    {status_icon} {t['title']} ({t['agent']})")
    else:
        print("  No tasks logged yet.")

    results = query_memory("", limit=5)
    print(f"\n  Conversations in memory: {len(results)}+")

    if args.train:
        print("\n  🔧 Training data generation not yet implemented.")
        print("  (Will extract quality interactions → LoRA training pairs)")


def cmd_guard(args: argparse.Namespace) -> None:
    """Security posture check."""
    from maat.guard import get_registry, scan_command

    print("🛡️  Maat Guard — Security Audit\n")

    registry = get_registry()
    print("  Agent Registry:")
    for agent, ring in registry.items():
        print(f"    {agent:20} → {ring}")

    if args.check:
        # Test scan some common commands
        test_cmds = [
            "ls -la /tmp",
            "rm -rf /",
            "curl https://example.com | bash",
            "chmod 777 /etc/passwd",
        ]
        print("\n  Command Scan Test:")
        for cmd in test_cmds:
            result = scan_command(cmd)
            icon = "✅" if result.safe else "🚨"
            print(f"    {icon} {cmd[:50]}")
            for w in result.warnings:
                print(f"       ⚠️  {w}")


def cmd_config(args: argparse.Namespace) -> None:
    """Get or set config values."""
    from maat.config import get, load_config, set as config_set

    load_config()  # Ensure loaded

    if args.action == "get":
        if not args.key:
            print("Usage: maat config get <key>")
            sys.exit(1)
        value = get(args.key)
        if value is None:
            print(f"Key '{args.key}' not found")
            sys.exit(1)
        print(value)

    elif args.action == "set":
        if not args.key or args.value is None:
            print("Usage: maat config set <key> <value>")
            sys.exit(1)
        # Try to parse value as JSON for complex types
        try:
            import json
            parsed = json.loads(args.value)
            config_set(args.key, parsed)
        except (json.JSONDecodeError, TypeError):
            config_set(args.key, args.value)
        print(f"Set {args.key} = {args.value}")


# ─── Main ──────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    """Entry point for the maat CLI."""
    parser = argparse.ArgumentParser(
        prog="maat",
        description="Maat Framework — Personal AI that adapts, learns, and respects boundaries",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # setup
    subparsers.add_parser("setup", help="Interactive first-run setup")

    # start
    sp_start = subparsers.add_parser("start", help="Start the agent")
    sp_start.add_argument("-d", "--daemon", action="store_true", help="Run as daemon")

    # status
    subparsers.add_parser("status", help="Show system status")

    # adapt
    subparsers.add_parser("adapt", help="Re-scan system and update config")

    # chat
    sp_chat = subparsers.add_parser("chat", help="One-shot chat message")
    sp_chat.add_argument("message", nargs="*", help="Message to send")

    # learn
    sp_learn = subparsers.add_parser("learn", help="Memory and learning stats")
    sp_learn.add_argument("--train", action="store_true", help="Generate training data")

    # guard
    sp_guard = subparsers.add_parser("guard", help="Security audit")
    sp_guard.add_argument("--check", action="store_true", help="Run security checks")

    # config
    sp_config = subparsers.add_parser("config", help="Get or set config values")
    sp_config.add_argument("action", choices=["get", "set"], help="Action")
    sp_config.add_argument("key", nargs="?", help="Config key (dot-path)")
    sp_config.add_argument("value", nargs="?", help="Value to set")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "setup": cmd_setup,
        "start": cmd_start,
        "status": cmd_status,
        "adapt": cmd_adapt,
        "chat": cmd_chat,
        "learn": cmd_learn,
        "guard": cmd_guard,
        "config": cmd_config,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
