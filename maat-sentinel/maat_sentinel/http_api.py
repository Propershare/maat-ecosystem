"""Minimal HTTP API (stdlib) for multi-host Sentinel: POST ingest, GET status/machines/alerts."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from maat_sentinel.envelope import now_iso
from maat_sentinel.ingest import ingest_doctor_json, ingest_immune_dict, ingest_presence
from maat_sentinel.models import PresenceRecord
from maat_sentinel.surface import alerts, all_machine_ids, unified_view


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any] | list[Any] | None:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b""
    if not raw:
        return {}
    try:
        out = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(out, (dict, list)):
        return out
    return None


class SentinelHTTPHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, obj: dict[str, Any]) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/machines":
            self._json(200, {"machines": all_machine_ids()})
            return
        if path == "/alerts":
            self._json(200, {"alerts": alerts()})
            return
        if path.startswith("/status"):
            rest = path[len("/status") :].strip("/")
            if not rest:
                self._json(400, {"error": "missing machine_id"})
                return
            self._json(200, unified_view(rest))
            return
        self._json(404, {"error": "not_found", "hint": "/machines /alerts /status/<id>"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        data = _read_json(self)
        if data is None:
            self._json(400, {"error": "invalid_json"})
            return
        if path == "/doctor":
            if not isinstance(data, dict):
                self._json(400, {"error": "expected_object"})
                return
            ingest_doctor_json(data)
            self._json(200, {"ok": True})
            return
        if path == "/immune":
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        ingest_immune_dict(item)
                self._json(200, {"ok": True, "ingested": len(data)})
                return
            if isinstance(data, dict):
                ingest_immune_dict(data)
                self._json(200, {"ok": True})
                return
            self._json(400, {"error": "expected_object_or_array"})
            return
        if path == "/presence":
            if not isinstance(data, dict):
                self._json(400, {"error": "expected_object"})
                return
            if not data.get("last_seen_at"):
                data = {**data, "last_seen_at": now_iso()}
            rec = PresenceRecord.from_dict(data)
            ingest_presence(rec)
            self._json(200, {"ok": True})
            return
        self._json(404, {"error": "not_found", "hint": "/doctor /immune /presence"})

    def log_message(self, fmt: str, *args: object) -> None:
        return


def run_http_server(host: str, port: int) -> None:
    import sys

    print(
        f"maat-sentinel HTTP http://{host}:{port}  GET /machines /alerts /status/<id>  POST /doctor /immune /presence",
        file=sys.stderr,
    )
    server = ThreadingHTTPServer((host, port), SentinelHTTPHandler)
    server.serve_forever()
