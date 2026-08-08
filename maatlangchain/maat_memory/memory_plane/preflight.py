"""Preflight — every agent, every machine: enroll, presence, Sankofa recall."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from ..machine_info import get_machine_info, get_unique_agent_id
from .learning_loop import LearningLoop
from .messaging import AgentMessaging
from .registry import FleetRegistry
from .session_presence import SessionPresence
from .storage import StorageAwareness
from .tepi import TepiIdentity


def _maat_memory():
    root = None
    cur = Path(__file__).resolve()
    for p in [cur.parent] + list(cur.parents):
        if (p / "maat_memory").is_dir() and (p / "maat_memory" / "__init__.py").exists():
            # parent of maat_memory package is maatlangchain
            if p.name == "maat_memory":
                root = p.parent
            else:
                root = p
            break
    # package lives at maatlangchain/maat_memory/memory_plane → maatlangchain on path
    ml = Path(__file__).resolve().parents[2]  # maatlangchain
    if str(ml) not in sys.path:
        sys.path.insert(0, str(ml))
    from maat_memory import MaatMemory  # type: ignore

    return MaatMemory()


def run_preflight(
    *,
    tool_type: str = "cursor",
    topic: str | None = None,
    role: str = "general",
    task_hint: str | None = None,
) -> dict[str, Any]:
    """
    1) enroll machine+agent
    2) register session presence
    3) recall tasks / learnings / decisions
    4) list active fleet peers
    """
    reg = FleetRegistry()
    presence = SessionPresence()
    learn = LearningLoop(reg)
    storage = StorageAwareness(reg)
    messaging = AgentMessaging()

    ids = reg.ensure_local(tool_type=tool_type)
    agent_id = ids["agent_id"]
    machine_id = ids["machine_id"]
    info = get_machine_info()
    principal_id = os.environ.get("MAAT_PRINCIPAL_ID") or "imhotep"

    # Bootstrap storage roots for this machine
    workspace = None
    for cand in ("/mnt/data_drive", str(Path.home() / ".n8n")):
        if Path(cand).is_dir():
            workspace = cand
            break
    roots = storage.bootstrap_local_roots(machine_id, workspace=workspace)
    storage_capacity = storage.check_capacity(machine_id)

    agent_row = reg.get_agent(agent_id) or {}
    agent_ring = agent_row.get("ring") or "outer"
    session = presence.register(
        agent_id=agent_id,
        machine_id=machine_id,
        role=role,
        ring=agent_ring,
        task_id=task_hint,
        current_topic=topic or "preflight",
        current_tools=["maat_memory_plane"],
    )

    tepi = TepiIdentity()
    tepi_bind = tepi.bind(
        principal_id=principal_id,
        agent_id=agent_id,
        ring=agent_ring,
        machine_id=machine_id,
        episode_id=str(session.get("session_id")),
        summary="preflight bind",
        payload={"topic": topic or "preflight"},
    )
    tepi_recall = tepi.recall(
        principal_id=principal_id,
        viewer_ring=agent_ring,
        limit=10,
    )

    tasks: list[Any] = []
    decisions: list[Any] = []
    try:
        mem = _maat_memory()
        if hasattr(mem, "get_tasks"):
            tasks = mem.get_tasks(status="pending", limit=8) or []
        if hasattr(mem, "get_decisions"):
            decisions = mem.get_decisions(limit=5) or []
    except Exception as exc:  # noqa: BLE001
        tasks = [{"error": str(exc)}]

    applied = learn.list_applied(topic_ilike=topic, limit=8) if topic else learn.list_applied(limit=8)
    proposed = learn.list_proposed(limit=5)
    active = presence.list_active(stale_minutes=45)

    # Agent messaging inbox
    pending_messages: list[dict[str, Any]] = []
    try:
        pending_messages = messaging.inbox(agent_id, status="pending", limit=10)
    except Exception:
        pass

    from .write_preflight import body_snapshot

    return {
        "schema": "maat.memory_plane.preflight.v0",
        "agent_id": agent_id,
        "machine_id": machine_id,
        "hostname": info.get("hostname"),
        "principal_id": principal_id,
        "ring": agent_ring,
        "session_id": str(session.get("session_id")),
        "tepi_bind": {
            "event_type": (tepi_bind or {}).get("event_type"),
            "id": str((tepi_bind or {}).get("id") or ""),
        },
        "tepi_recall": {
            "artifact_n": len(tepi_recall.get("artifacts") or []),
            "learning_n": len(tepi_recall.get("learnings") or []),
            "tepi_n": len(tepi_recall.get("tepi") or []),
            "viewer_ring": tepi_recall.get("viewer_ring"),
        },
        "storage_roots_registered": roots,
        "storage_capacity": {
            "ok": bool(storage_capacity.get("ok")),
            "reason": storage_capacity.get("reason"),
            "threshold_pct": storage_capacity.get("threshold_pct"),
            "preferred_root": (storage_capacity.get("preferred_root") or {}).get("probe"),
            "preferred_used_pct": (storage_capacity.get("preferred_root") or {}).get(
                "used_pct"
            ),
        },
        "host_body": body_snapshot(),
        "tasks_pending": _summarize_tasks(tasks),
        "learnings_applied": applied,
        "learnings_proposed": proposed,
        "decisions_recent": _summarize_decisions(decisions),
        "fleet_active": active,
        "pending_messages": {
            "count": len(pending_messages),
            "messages": pending_messages,
        },
        "law": [
            "Query gitMaat / Memory Plane before planning",
            "Propose learning with applied=false; apply only when enrolled + allowed",
            "Constitutional / policy_update is amendment — not learning",
            "Artifacts: use artifacts[].open (https) or fetch-artifact — never host file://",
            "Root is cockpit not warehouse — write-check before large durable writes",
        ],
        "one_liner": (
            "If you can reach gitMaat, you can reach the artifact bank — "
            "use open/https or fetch-artifact; never require /mnt/data_drive or file://."
        ),
        "artifact_how": {
            "list": "python3 ~/.hermes/scripts/gitmaat_memory_query.py artifacts --every-agent",
            "law": "python3 ~/.hermes/scripts/gitmaat_memory_query.py law",
            "fetch": "python3 ~/.hermes/scripts/gitmaat_memory_query.py fetch-artifact --uri maat://artifact/<slug>",
            "write_check": "python3 ~/.hermes/scripts/maat_memory_plane.py write-check --path PATH --size-mb N",
            "body": "python3 ~/.hermes/scripts/maat_memory_plane.py body",
        },
    }


def _summarize_tasks(tasks: list[Any]) -> list[dict[str, Any]]:
    out = []
    for t in tasks[:8]:
        if not isinstance(t, dict):
            out.append({"raw": str(t)[:160]})
            continue
        if t.get("error"):
            out.append(t)
            continue
        out.append(
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "agent": t.get("agent"),
            }
        )
    return out


def _summarize_decisions(decisions: list[Any]) -> list[dict[str, Any]]:
    out = []
    for d in decisions[:5]:
        if not isinstance(d, dict):
            continue
        out.append(
            {
                "context": str(d.get("context") or "")[:120],
                "decision": str(d.get("decision_made") or "")[:160],
                "agent": d.get("agent"),
            }
        )
    return out
