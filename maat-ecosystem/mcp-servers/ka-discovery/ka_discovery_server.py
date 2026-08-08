#!/usr/bin/env python3
"""
Ka Discovery Server — The Nervous System (restored + honest auth).

GET /manifest  → Full Ka body map (JSON) with per-organ auth_enforced
GET /health    → Organ reachability
GET /organs    → Organ list
GET /organ/{name}
GET /connect   → Connection instructions

Port: 8010 (front door). Discovery itself stays open (the map).
Doctrine: advertised auth must match enforcement — absence of a probe is not "enforced".
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
)
log = logging.getLogger("ka_discovery")

WORKSPACE_ROOT = Path.home() / ".n8n"
MAAT_ECOSYSTEM_ROOT = WORKSPACE_ROOT / "maat-ecosystem"
SOUL_DIR = MAAT_ECOSYSTEM_ROOT / "soul"
HOSTNAME = socket.gethostname()
PORT = int(os.environ.get("KA_DISCOVERY_PORT", "8010"))


def _host_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(HOSTNAME)
        except Exception:
            return "127.0.0.1"


HOST_IP = os.environ.get("KA_DISCOVERY_HOST_IP") or _host_ip()


def _probe_auth(port: int, path: str = "/openapi.json") -> dict[str, Any]:
    """Probe whether an organ rejects unauthenticated GETs.

    Returns auth_enforced True only when unauthenticated request is 401/403.
    Connection failures → auth_enforced False (absence is not enforcement).
    """
    url = f"http://127.0.0.1:{port}{path}"
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=1.5) as resp:
            return {
                "reachable": True,
                "auth_enforced": False,
                "probe_status": resp.status,
                "probe_path": path,
            }
    except HTTPError as e:
        enforced = e.code in (401, 403)
        return {
            "reachable": True,
            "auth_enforced": enforced,
            "probe_status": e.code,
            "probe_path": path,
        }
    except (URLError, TimeoutError, OSError) as e:
        return {
            "reachable": False,
            "auth_enforced": False,
            "probe_status": None,
            "probe_error": type(e).__name__,
            "probe_path": path,
        }


def _organ_http(
    *,
    role: str,
    port: int,
    server: str,
    capabilities: list[str],
    organ_type: str = "mcp",
    tools: list[str] | None = None,
    note: str | None = None,
    probe_path: str = "/openapi.json",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    probe = _probe_auth(port, probe_path)
    out: dict[str, Any] = {
        "role": role,
        "type": organ_type,
        "endpoint": f"http://{HOST_IP}:{port}",
        "port": port,
        "server": server,
        "capabilities": capabilities,
        "auth_enforced": probe["auth_enforced"],
        "reachable": probe["reachable"],
        "auth_probe": {
            "status": probe.get("probe_status"),
            "path": probe.get("probe_path"),
            "error": probe.get("probe_error"),
        },
    }
    if tools:
        out["tools"] = tools
    if note:
        out["note"] = note
    if extra:
        out.update(extra)
    return out


def get_manifest() -> dict[str, Any]:
    organs: dict[str, Any] = {
        "soul": {
            "role": "Identity, governance, and moral constitution",
            "type": "files",
            "path": str(SOUL_DIR) + "/",
            "read_first": "constitution.md",
            "capabilities": ["identify", "govern", "constrain"],
            "auth_enforced": False,
            "note": "File-based organ — not an HTTP Bearer surface",
        },
        "policy": _organ_http(
            role="Tehuti Guard — policy enforcement",
            port=8013,
            server="tehuti-guard",
            capabilities=["decision", "validate", "risk"],
            organ_type="http",
            probe_path="/health",
            note="Bearer TEHUTI_GUARD_TOKEN (not KA_API_KEY)",
            extra={
                "primary_paths": ["POST /decision", "GET /health"],
                "source_path": "tehuti-guard/guard/",
            },
        ),
        "brain": _organ_http(
            role="Reasoning, model access, shell execution, and learning",
            port=8014,
            server="tehuti-core",
            capabilities=["think", "execute", "decide", "learn"],
            tools=[
                "execute_command",
                "run_python_code",
                "query_gitmaat",
                "log_gitmaat_task",
                "log_gitmaat_decision",
            ],
        ),
        "memory": _organ_http(
            role="Persistence, recall, sessions — Maat Memory MCP",
            port=8022,
            server="maat-memory",
            capabilities=["store", "retrieve", "search", "session", "stats"],
            note="Bearer KA_API_KEY / MCPO_API_KEY. Local write mint :8023 is separate (memory token).",
            extra={
                "write_mint": {
                    "endpoint": "http://127.0.0.1:8023",
                    "bind": "127.0.0.1",
                    "auth": "X-Maat-Memory-Token",
                    "stamps_origin": True,
                }
            },
        ),
        "hands": {
            "role": "Action, tool use, file operations",
            "type": "mcp",
            "endpoints": {
                "filesystem": _organ_http(
                    role="filesystem",
                    port=8016,
                    server="filesystem-mcp",
                    capabilities=["read", "write", "list"],
                ),
                "tools": _organ_http(
                    role="tehuti-core tools",
                    port=8014,
                    server="tehuti-core",
                    capabilities=["execute_command", "run_python_code"],
                ),
            },
            "auth_enforced": False,  # aggregate — see nested endpoints
        },
        "senses": {
            "role": "Perception surfaces",
            "type": "http",
            "endpoint": f"http://{HOST_IP}:18790",
            "port": 18790,
            "auth_enforced": False,
            "reachable": _probe_auth(18790, "/health")["reachable"],
        },
        "voice": _organ_http(
            role="Speech / audio helpers",
            port=8021,
            server="tehuti-audio",
            capabilities=["speak"],
            organ_type="http",
            probe_path="/health",
        ),
        "ka": {
            "role": "Discovery / body map (this service)",
            "type": "http",
            "endpoint": f"http://{HOST_IP}:8010/health",
            "port": 8010,
            "auth_enforced": False,
            "note": "Nervous map stays open; organs enforce Bearer where auth_enforced=true",
        },
        "skeleton": _organ_http(
            role="Postgres MCP",
            port=8017,
            server="postgres-mcp",
            capabilities=["query"],
        ),
        "blood": {
            "role": "Pipeline / RAG flow",
            "type": "http",
            "pipeline": _organ_http(
                role="maatlangchain-pipeline",
                port=8020,
                server="maatlangchain-pipeline",
                capabilities=["pipeline"],
                organ_type="http",
                probe_path="/health",
            ),
            "auth_enforced": False,
        },
        # Membership plane — knock door (rules only). Never advertise invite tokens or operator secrets.
        "membership": {
            **_probe_auth(8040, "/health"),
            "role": "Maat join — fleet membership / birth (Head Operator allow)",
            "type": "http",
            "endpoint": "http://127.0.0.1:8040/health",
            "port": 8040,
            "bind": "127.0.0.1-only",
            "note": (
                "Discover the door, not the key. GET /api/help (join-help). "
                "Agents ask-join with a chore; Head Operator allow/deny on /lab. "
                "Never read .env.broker / .ka-auth. join-produce does not grant master KA."
            ),
            "primary_paths": [
                "GET /api/help",
                "POST /api/join/ask",
                "GET /mobile",
                "GET /lab",
            ],
            "agent_start": [
                "curl -s http://127.0.0.1:8040/api/help",
                "python3 /mnt/data_drive/hermes/scripts/maat_memory_plane.py join-help",
                'python3 /mnt/data_drive/hermes/scripts/maat_memory_plane.py ask-join --working-on "<chore>"',
                'OR: maat-ask-join "<chore>"',
            ],
            "forbidden": [
                "Do not expect organ_bearer / master KA from join-produce",
                "Do not self-approve join-decide",
                "Do not copy operator secrets",
            ],
            "policy_version": "maat-join@0.1.1",
            "dashboards": {"mobile": "/mobile", "lab": "/lab"},
        },
    }

    # Flatten truth: which HTTP organs actually enforce
    enforced = []
    open_organs = []
    for name, body in organs.items():
        if isinstance(body.get("auth_enforced"), bool):
            (enforced if body["auth_enforced"] else open_organs).append(name)
        for sub in (body.get("endpoints") or {}).values():
            if isinstance(sub, dict) and sub.get("auth_enforced") is True:
                enforced.append(f"{name}.{sub.get('server')}")
            elif isinstance(sub, dict) and sub.get("port"):
                open_organs.append(f"{name}.{sub.get('server')}")
        pipe = body.get("pipeline")
        if isinstance(pipe, dict):
            (enforced if pipe.get("auth_enforced") else open_organs).append(f"{name}.pipeline")

    all_enforced = bool(enforced) and not open_organs
    auth_note = (
        "All probed HTTP organ endpoints enforce Bearer (or Guard token)."
        if all_enforced
        else (
            "Bearer required where organ.auth_enforced=true. "
            f"Enforced: {sorted(set(enforced)) or ['(none)']}. "
            f"Not yet enforced: {sorted(set(open_organs))}. "
            "Absence of enforcement is not compliance — see KA-SIBLING-MCP-IMMUNE-HANDOFF.md"
        )
    )

    return {
        "kind": "ka-body",
        "version": "1.1.0",
        "name": "maat-ecosystem",
        "hostname": HOSTNAME,
        "purpose": "Restore Maat through truth, balance, and order",
        "discovery": f"http://{HOST_IP}:{PORT}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "auth": {
            "type": "bearer",
            "header": "Authorization",
            "key_name": "KA_API_KEY",
            "note": auth_note,
            "universal_claim": False,
            "enforced_organs": sorted(set(enforced)),
            "open_organs": sorted(set(open_organs)),
        },
        "organs": organs,
        "boot_sequence": [
            "GET membership /api/help (join-help) — learn the knock rules",
            "ask-join --working-on '<chore>' — request membership (pending)",
            "Wait for Head Operator allow → join-produce --code … → whoami",
            "Read soul/constitution.md — know your laws",
            "gitmaat law / memory — only after birth (scoped organs TBD)",
            "Check organ.auth_enforced — do not trust open surfaces or master KA copies",
            "Ready — awaiting input under a live grant",
        ],
        "attribution": {
            "methodology": "KA2 / Ka Architecture — Dr. Tdka Kilimanjaro, University of KMT",
            "institution": "Tehuti Lab",
        },
    }


def get_health() -> dict[str, Any]:
    m = get_manifest()
    status = {}
    for name, body in m["organs"].items():
        if "port" in body:
            status[name] = {
                "status": "up" if body.get("reachable") else "down",
                "port": body.get("port"),
                "auth_enforced": body.get("auth_enforced"),
            }
        elif "endpoints" in body:
            for k, sub in body["endpoints"].items():
                status[f"{name}.{k}"] = {
                    "status": "up" if sub.get("reachable") else "down",
                    "port": sub.get("port"),
                    "auth_enforced": sub.get("auth_enforced"),
                }
        elif "pipeline" in body:
            p = body["pipeline"]
            status[f"{name}.pipeline"] = {
                "status": "up" if p.get("reachable") else "down",
                "port": p.get("port"),
                "auth_enforced": p.get("auth_enforced"),
            }
        else:
            status[name] = {"status": "static", "auth_enforced": body.get("auth_enforced")}
    return {
        "ok": True,
        "hostname": HOSTNAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organs": status,
        "auth": m["auth"],
    }


def get_connect_info() -> dict[str, Any]:
    m = get_manifest()
    return {
        "discovery": m["discovery"],
        "auth": m["auth"],
        "steps": [
            "GET /manifest — read the body map (includes membership/join)",
            "GET http://127.0.0.1:8040/api/help — join-help (rules, not secrets)",
            "ask-join with a concrete chore; do not self-approve",
            "After allow: join-produce with one-time code → whoami (birth, not master KA)",
            "Prefer organs with auth_enforced=true; treat open organs as exposure",
            "Organ tools: scoped bearer from grant when available — never copy .env.broker",
            "Guard uses TEHUTI_GUARD_TOKEN, not KA_API_KEY",
        ],
        "membership": {
            "help": "http://127.0.0.1:8040/api/help",
            "lab": "http://127.0.0.1:8040/lab",
            "mobile": "http://127.0.0.1:8040/mobile",
            "cli": "python3 /mnt/data_drive/hermes/scripts/maat_memory_plane.py join-help",
        },
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            if path in ("/", "/manifest"):
                self._json(200, get_manifest())
            elif path == "/health":
                self._json(200, get_health())
            elif path == "/organs":
                m = get_manifest()
                self._json(200, {"organs": list(m["organs"].keys()), "detail": m["organs"]})
            elif path.startswith("/organ/"):
                name = path[len("/organ/") :].strip("/")
                m = get_manifest()
                if name not in m["organs"]:
                    self._json(404, {"error": "unknown_organ", "name": name})
                else:
                    self._json(200, m["organs"][name])
            elif path == "/connect":
                self._json(200, get_connect_info())
            else:
                self._json(404, {"error": "not_found", "paths": ["/", "/manifest", "/health", "/organs", "/organ/{name}", "/connect"]})
        except Exception as e:
            log.exception("handler error")
            self._json(500, {"error": str(e)})

    def log_message(self, fmt: str, *args: Any) -> None:
        log.info("%s - %s", self.address_string(), fmt % args)


def main() -> None:
    host = os.environ.get("KA_DISCOVERY_BIND", "0.0.0.0")
    log.info("🪶 Ka Discovery starting on %s:%s (HOST_IP=%s)", host, PORT, HOST_IP)
    server = ThreadingHTTPServer((host, PORT), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        t.join()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
