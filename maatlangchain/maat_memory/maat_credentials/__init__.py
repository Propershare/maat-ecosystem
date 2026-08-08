"""
Maat Credentials (T3) — credential split.

Law: Broker keys do not sit in the same .env every agent can read.
Absence of a role is not broker access.

Roles:
  agent  — may load .env.agent only; broker-class keys are stripped / refused
  broker — may load .env.broker (and agent); requires MAAT_CREDENTIAL_ROLE=broker

The frame here is role + file separation. Pattern-matching key names is
defense-in-depth for classification, not a substitute for keeping secrets
out of the agent-readable path.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping


class CredentialError(ValueError):
    """Refuse unsafe credential access."""


class CredentialRole(str, Enum):
    AGENT = "agent"
    BROKER = "broker"


# Spend / impersonation / platform tokens — never agent-readable.
BROKER_KEYS = frozenset(
    {
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_GENAI_API_KEY",
        "XAI_API_KEY",
        "OLLAMA_API_KEY",
        "DISCORD_BOT_TOKEN",
        "HERMES_GATEWAY_TOKEN",
        "HERMES_API_KEY",
        "BRIDGE_TOKEN",
        "META_BLR_PAGE_ACCESS_TOKEN",
        "META_BLR_USER_ACCESS_TOKEN",
        "META_BLR_APP_SECRET",
        "META_BLR_VERIFY_TOKEN",
        "KA_API_KEY",
        "MAAT_OPERATOR_TOKEN",
        "TEHUTI_GUARD_TOKEN",
        "N8N_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "PAYPAL_CLIENT_SECRET",
        "JWT_SECRET",
        "WEBUI_SECRET_KEY",
        "DB_POSTGRESDB_PASSWORD",
        "POSTGRES_PASSWORD",
        "N8N_ENCRYPTION_KEY",
        "N8N_USER_MANAGEMENT_JWT_SECRET",
        "NGINX_TOOL_API_KEY",
        "MCP_API_KEY",
        "AUTH_TOKEN",
        "MCP_AUTH_TOKEN",
        "PRIVATE_KEY",
        # T1 integrity: DSN is a write-trust mint — broker/organ only
        "PGVECTOR_DB_URL",
        "DATABASE_URL",
    }
)

# Name patterns that classify as broker even if not in the set above.
_BROKER_NAME_RE = re.compile(
    r"(?:^|_)(API_KEY|ACCESS_TOKEN|SECRET|PASSWORD|PRIVATE_KEY|BOT_TOKEN|GATEWAY_TOKEN)(?:$|_)",
    re.I,
)

# Explicit agent-safe allowlist (coordination). Everything else unknown → broker
# if it looks secret; else agent (flags/hosts).
AGENT_SAFE_KEYS = frozenset(
    {
        "MAAT_MEMORY_URL",
        "MAAT_MEMORY_WRITE_URL",
        "MAAT_MEMORY_AGENT_TOKEN",
        "MAAT_MEMORY_MEDIATED",
        "MAAT_DOTENV",
        "MAAT_ENV_AGENT",
        "MAAT_ENV_BROKER",
        "MAAT_CREDENTIAL_ROLE",
        "MAAT_TOOL_TYPE",
        "MAAT_MACHINE_ID",
        "HERMES_HOME",
        "HERMES_BIN",
        "HERMES_TIMEOUT_SEC",
        "HERMES_API_BASE",
        "HERMES_NODE",
        "KA_AUTH_FILE",
        "KA_EDU_API_BASE",
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE_URL",
        "OPENAI_MODEL",
        "OLLAMA_HOST",
        "ENABLE_OLLAMA_API",
        "WHATSAPP_ENABLED",
        "DISCORD_ALLOWED_USERS",
        "BRIDGE_HOST",
        "BRIDGE_PORT",
        "BACKEND",
        "N8N_HOST",
        "N8N_PORT",
        "N8N_PROTOCOL",
        "N8N_SECURE_COOKIE",
        "N8N_WEBHOOK_URL",
        "N8N_OAUTH_CALLBACK_URL",
        "N8N_HIDE_USAGE_INFORMATION",
        "DB_TYPE",
        "DB_POSTGRESDB_HOST",
        "DB_POSTGRESDB_PORT",
        "DB_POSTGRESDB_DATABASE",
        "DB_POSTGRESDB_USER",
        "API_HOST",
        "API_PORT",
        "META_BLR_APP_ID",
        "META_BLR_WEBHOOK_HOST",
        "META_BLR_WEBHOOK_PORT",
        "META_BLR_WEBHOOK_PATH",
        "META_BLR_API_VERSION",
        "META_BLR_ECHO",
        "META_BLR_ALLOWED_SENDERS",
        "META_BLR_PAGE_ID",
        "ASK_SCHOLAR_MAX_TOKENS",
        "SESSION_SECRET",  # borderline — treat as broker below via pattern? keep listed then override
    }
)

# Remaining agent-reachable holes (not DSN — those are broker now).
DECLARED_DEBT_KEYS = frozenset(
    {
        "SESSION_SECRET",
        "MAATBENCH_LAB_KEY",
    }
)


class KeyClass(str, Enum):
    AGENT = "agent"
    BROKER = "broker"
    DEBT = "debt"  # still agent-reachable; documented hole


def classify_key(name: str) -> KeyClass:
    n = name.strip()
    if n in DECLARED_DEBT_KEYS:
        return KeyClass.DEBT
    # Explicit agent allowlist wins over secretish name patterns
    # (e.g. MAAT_MEMORY_AGENT_TOKEN is a scoped write token, not a DSN).
    if n in AGENT_SAFE_KEYS:
        return KeyClass.AGENT
    if n in BROKER_KEYS or _BROKER_NAME_RE.search(n):
        return KeyClass.BROKER
    # Unknown: if it looks like a secret name → broker; else agent (hosts/flags)
    if re.search(r"(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)", n, re.I):
        return KeyClass.BROKER
    return KeyClass.AGENT


def require_role(expected: CredentialRole | str) -> CredentialRole:
    raw = (os.environ.get("MAAT_CREDENTIAL_ROLE") or "").strip().lower()
    if not raw:
        raise CredentialError(
            "MAAT_CREDENTIAL_ROLE required — absence is not broker access"
        )
    try:
        role = CredentialRole(raw)
    except ValueError as e:
        raise CredentialError(f"unknown MAAT_CREDENTIAL_ROLE {raw!r}") from e
    want = CredentialRole(expected) if isinstance(expected, str) else expected
    if role != want:
        raise CredentialError(f"role {role.value} cannot assume {want.value}")
    return role


def parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        if s.startswith("export "):
            s = s[7:].strip()
        k, _, v = s.partition("=")
        k = k.strip()
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        if k:
            out[k] = v
    return out


def split_env_map(env: Mapping[str, str]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Return (agent, broker, debt) maps. Debt rides with agent file but is flagged."""
    agent: dict[str, str] = {}
    broker: dict[str, str] = {}
    debt: dict[str, str] = {}
    for k, v in env.items():
        cls = classify_key(k)
        if cls == KeyClass.BROKER:
            broker[k] = v
        elif cls == KeyClass.DEBT:
            debt[k] = v
            agent[k] = v
        else:
            agent[k] = v
    return agent, broker, debt


def _format_env(mapping: Mapping[str, str], header: str) -> str:
    lines = [header.rstrip(), ""]
    for k in sorted(mapping):
        v = mapping[k]
        # Preserve values; quote if needed
        if any(c in v for c in ' \n#"\'') or v == "":
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k}="{escaped}"')
        else:
            lines.append(f"{k}={v}")
    lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True)
class SplitResult:
    source: Path
    agent_path: Path
    broker_path: Path
    agent_keys: tuple[str, ...]
    broker_keys: tuple[str, ...]
    debt_keys: tuple[str, ...]


def split_dotenv(
    source: Path,
    *,
    agent_path: Path | None = None,
    broker_path: Path | None = None,
    rewrite_source: bool = True,
) -> SplitResult:
    """Split a monolithic .env into .env.agent + .env.broker.

    If rewrite_source, replace source with agent-safe content + pointer comments
    (broker keys removed from the agent-readable path).
    """
    source = source.resolve()
    agent_path = (agent_path or source.with_name(source.name + ".agent")).resolve()
    # Prefer .env.agent / .env.broker naming when source is `.env`
    if source.name == ".env":
        agent_path = source.with_name(".env.agent")
        broker_path = broker_path or source.with_name(".env.broker")
    else:
        broker_path = (broker_path or source.with_name(source.name + ".broker")).resolve()

    parsed = parse_env_file(source)
    agent, broker, debt = split_env_map(parsed)

    agent_path.write_text(
        _format_env(
            agent,
            "# Maat T3 — AGENT-readable env (coordination + declared debt).\n"
            "# Broker spend/tokens live in sibling .env.broker — not here.",
        ),
        encoding="utf-8",
    )
    agent_path.chmod(0o600)

    broker_path.write_text(
        _format_env(
            broker,
            "# Maat T3 — BROKER-only env. Load only with MAAT_CREDENTIAL_ROLE=broker.\n"
            "# Agents must not read this file.",
        ),
        encoding="utf-8",
    )
    broker_path.chmod(0o600)

    if rewrite_source:
        # Source becomes agent view + explicit redirect (no broker values)
        stub = (
            "# Maat T3 credential split — this file is AGENT-safe only.\n"
            f"# Broker secrets: {broker_path}\n"
            f"# Agent env:      {agent_path}\n"
            "# Gateway/systemd should EnvironmentFile both .env.agent and .env.broker.\n"
            "# Do NOT put OPENROUTER/Discord/Meta tokens back into this file.\n"
            "\n"
        ) + _format_env(agent, "# --- agent keys (mirrored from .env.agent) ---")
        source.write_text(stub, encoding="utf-8")
        source.chmod(0o600)

    return SplitResult(
        source=source,
        agent_path=agent_path,
        broker_path=broker_path,
        agent_keys=tuple(sorted(agent)),
        broker_keys=tuple(sorted(broker)),
        debt_keys=tuple(sorted(debt)),
    )


def load_agent_env(
    paths: Iterable[Path] | None = None,
    *,
    into_environ: bool = True,
    allow_debt: bool = True,
) -> dict[str, str]:
    """Load agent-safe env. Refuses broker-class keys if present in those files."""
    role = (os.environ.get("MAAT_CREDENTIAL_ROLE") or "agent").strip().lower()
    if role == CredentialRole.BROKER.value:
        raise CredentialError("use load_broker_env for broker role")
    # Default role agent — absence of explicit role defaults to agent (fail-closed for broker)

    candidates = list(paths) if paths is not None else _default_agent_paths()
    merged: dict[str, str] = {}
    for p in candidates:
        if not p.exists():
            continue
        data = parse_env_file(p)
        for k, v in data.items():
            cls = classify_key(k)
            if cls == KeyClass.BROKER:
                raise CredentialError(
                    f"broker key {k} found in agent path {p} — T3 split violated"
                )
            if cls == KeyClass.DEBT and not allow_debt:
                raise CredentialError(f"declared debt key {k} refused (allow_debt=False)")
            merged[k] = v

    if into_environ:
        for k, v in merged.items():
            if k not in os.environ:
                os.environ[k] = v
    return merged


def load_broker_env(
    paths: Iterable[Path] | None = None,
    *,
    into_environ: bool = True,
    also_agent: bool = True,
) -> dict[str, str]:
    """Load broker env. Requires MAAT_CREDENTIAL_ROLE=broker."""
    require_role(CredentialRole.BROKER)
    merged: dict[str, str] = {}
    if also_agent:
        for p in _default_agent_paths():
            if not p.exists():
                continue
            data = parse_env_file(p)
            for k, v in data.items():
                if classify_key(k) == KeyClass.BROKER:
                    raise CredentialError(
                        f"broker key {k} found in agent path {p} — T3 split violated"
                    )
                merged[k] = v

    candidates = list(paths) if paths is not None else _default_broker_paths()
    for p in candidates:
        if not p.exists():
            continue
        data = parse_env_file(p)
        for k, v in data.items():
            merged[k] = v

    if into_environ:
        for k, v in merged.items():
            os.environ[k] = v
    return merged


def assert_agent_cannot_see(keys: Iterable[str], env: Mapping[str, str] | None = None) -> None:
    e = env if env is not None else os.environ
    leaked = [k for k in keys if e.get(k)]
    if leaked:
        raise CredentialError(f"agent can still see broker keys: {leaked}")


def _default_agent_paths() -> list[Path]:
    home = Path.home()
    hermes = Path(os.environ.get("HERMES_HOME", "/mnt/data_drive/hermes"))
    out = [hermes / ".env.agent", home / ".hermes" / ".env.agent"]
    if os.environ.get("MAAT_ENV_AGENT"):
        out.insert(0, Path(os.environ["MAAT_ENV_AGENT"]))
    return out


def _default_broker_paths() -> list[Path]:
    home = Path.home()
    hermes = Path(os.environ.get("HERMES_HOME", "/mnt/data_drive/hermes"))
    out = [hermes / ".env.broker", home / ".hermes" / ".env.broker"]
    if os.environ.get("MAAT_ENV_BROKER"):
        out.insert(0, Path(os.environ["MAAT_ENV_BROKER"]))
    return out


__all__ = [
    "CredentialError",
    "CredentialRole",
    "KeyClass",
    "BROKER_KEYS",
    "DECLARED_DEBT_KEYS",
    "classify_key",
    "require_role",
    "parse_env_file",
    "split_env_map",
    "split_dotenv",
    "load_agent_env",
    "load_broker_env",
    "assert_agent_cannot_see",
]
