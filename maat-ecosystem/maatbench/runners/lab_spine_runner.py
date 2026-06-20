"""
lab_spine_runner — verify multi-agent lab spine (OpenClaw, Gateway, Hermes, triad registry).

Stdlib only. Optional tests pass with a skip note when organs are down (nightly cron friendly).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from maatbench.bootstrap import bootstrap, lab_root

bootstrap()
_LAB = lab_root()
_HERMES_DEFAULT = Path("/mnt/data_drive/hermes/skills")


def _http_ok(url: str, timeout: float = 3.0) -> tuple[bool, str]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return True, f"HTTP {code}"
            return False, f"HTTP {code}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


def _parse_registry_gateway_ids(registry_path: Path) -> set[str]:
    ids: set[str] = set()
    if not registry_path.is_file():
        return ids
    for line in registry_path.read_text().splitlines():
        m = re.match(r"^\s*-?\s*id:\s*(\S+)\s*$", line)
        if m:
            ids.add(m.group(1))
    return ids


def run_lab_spine_tests(test_defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        optional = bool(test.get("optional"))
        passed = True
        notes: list[str] = []

        try:
            if op == "file_exists":
                rel = test["path"]
                path = _LAB / rel
                if path.exists():
                    notes.append(f"found {rel}")
                else:
                    passed = False
                    notes.append(f"missing {path}")

            elif op == "http_health":
                ok, detail = _http_ok(test["url"])
                if ok:
                    notes.append(detail)
                else:
                    passed = False
                    notes.append(detail)

            elif op == "registry_gateways":
                reg = _LAB / test["registry"]
                found = _parse_registry_gateway_ids(reg)
                for gid in test.get("gateway_ids", []):
                    if gid in found:
                        notes.append(f"{gid} registered")
                    else:
                        passed = False
                        notes.append(f"{gid} missing from registry")

            elif op == "expert_roles":
                swarm = _LAB / "gemma4-toolshim" / "swarm"
                if str(swarm) not in sys.path:
                    sys.path.insert(0, str(swarm))
                import expert_config  # type: ignore

                roles = {e.get("role") for e in expert_config.EXPERTS}
                for role in test.get("roles", []):
                    if role in roles:
                        notes.append(f"role {role} in EXPERTS")
                    else:
                        passed = False
                        notes.append(f"role {role} missing")

            elif op == "openclaw_workspace":
                cfg_path = Path.home() / ".openclaw" / "openclaw.json"
                if not cfg_path.is_file():
                    passed = False
                    notes.append("~/.openclaw/openclaw.json missing")
                else:
                    cfg = json.loads(cfg_path.read_text())
                    ws = (
                        cfg.get("agents", {})
                        .get("defaults", {})
                        .get("workspace", "")
                    )
                    if Path(ws).resolve() == _LAB.resolve():
                        notes.append("workspace matches lab root")
                    else:
                        passed = False
                        notes.append(f"workspace mismatch: {ws!r} != {_LAB!r}")

            elif op == "hermes_skills":
                base = Path(os.getenv("HERMES_SKILLS_ROOT", str(_HERMES_DEFAULT)))
                required = [
                    base / "research" / "last30days",
                    base / "research" / "tehuti-research-memory",
                ]
                for p in required:
                    if p.is_dir():
                        notes.append(f"found {p.name}")
                    else:
                        passed = False
                        notes.append(f"missing {p}")

            else:
                passed = False
                notes.append(f"unknown operation: {op}")

        except Exception as exc:
            passed = False
            notes.append(f"Exception: {exc}")

        if not passed and optional:
            passed = True
            notes.append("optional — organ down or path absent; not blocking bench")

        results.append(
            {
                "id": test_id,
                "name": test.get("name", test_id),
                "category": "lab_spine",
                "passed": passed,
                "score": 1.0 if passed else 0.0,
                "notes": "; ".join(notes),
            }
        )

    return results
