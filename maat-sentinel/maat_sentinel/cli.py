"""CLI: ingest doctor JSON, tail immune log, print unified view."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from maat_sentinel import __version__
from maat_sentinel.ingest import ingest_doctor_json, ingest_stdin_immune
from maat_sentinel.surface import unified_view


def _default_sentinel_port() -> int:
    """4242 by default; override with MAAT_SENTINEL_PORT (containers, systemd, cloud)."""
    raw = os.environ.get("MAAT_SENTINEL_PORT", "").strip()
    if not raw:
        return 4242
    try:
        return int(raw)
    except ValueError:
        return 4242


def _cmd_serve(args: argparse.Namespace) -> int:
    from maat_sentinel.http_api import run_http_server

    run_http_server(args.host, args.port)
    return 0


def _cmd_ingest_doctor(args: argparse.Namespace) -> int:
    raw = Path(args.file).read_text(encoding="utf-8")
    doc = json.loads(raw)
    ingest_doctor_json(doc)
    out = {"ok": True, "machine_id": doc.get("machine_id")}
    print(json.dumps(out, indent=2))
    return 0


def _cmd_ingest_immune_stdin(_args: argparse.Namespace) -> int:
    n = ingest_stdin_immune()
    print(json.dumps({"ingested": n}, indent=2))
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    mid = args.machine_id.strip()
    if not mid:
        print("machine_id required", file=sys.stderr)
        return 2
    view = unified_view(mid, immune_limit=args.limit)
    print(json.dumps(view, indent=2))
    return 0


def _cmd_doctor_pipe(_args: argparse.Namespace) -> int:
    """Run maat doctor --json and ingest (requires maat on PATH)."""
    r = subprocess.run(
        ["maat", "doctor", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0 and not r.stdout.strip():
        print(r.stderr or "maat doctor failed", file=sys.stderr)
        return 1
    doc = json.loads(r.stdout)
    ingest_doctor_json(doc)
    out = {"ok": True, "ingested": True, "machine_id": doc.get("machine_id")}
    print(json.dumps(out, indent=2))
    return 0


def main() -> None:
    desc = "Sentinel v1 scaffold — ingest & surface awareness."
    p = argparse.ArgumentParser(prog="maat-sentinel", description=desc)
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("ingest-doctor", help="Append doctor-report JSON file to state")
    s1.add_argument("file", type=str, help="Path to maat doctor --json output")
    s1.set_defaults(func=_cmd_ingest_doctor)

    s2 = sub.add_parser(
        "ingest-immune-stdin",
        help="Append immune JSONL lines from stdin",
    )
    s2.set_defaults(func=_cmd_ingest_immune_stdin)

    s3 = sub.add_parser("status", help="Print unified JSON for a machine_id")
    s3.add_argument(
        "--machine-id",
        required=True,
        help="MAAT_MACHINE_ID / doctor machine_id",
    )
    s3.add_argument("--limit", type=int, default=20, help="Max immune events")
    s3.set_defaults(func=_cmd_status)

    s4 = sub.add_parser(
        "ingest-doctor-pipe",
        help="Run maat doctor --json and ingest (maat on PATH)",
    )
    s4.set_defaults(func=_cmd_doctor_pipe)

    s5 = sub.add_parser("serve", help="HTTP API (multi-host ingest + status)")
    s5.add_argument("--host", default="127.0.0.1", help="Bind address")
    s5.add_argument(
        "--port",
        type=int,
        default=_default_sentinel_port(),
        help="Port (default 4242, or MAAT_SENTINEL_PORT)",
    )
    s5.set_defaults(func=_cmd_serve)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
