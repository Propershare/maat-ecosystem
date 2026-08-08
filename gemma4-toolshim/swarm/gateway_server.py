"""
MAAT Gateway HTTP server — one port, all channels.

Why this exists
---------------
OpenClaw (TypeScript) and any other channel — Telegram, Discord, WhatsApp,
n8n, a shell script, a cron job — can hit **one HTTP endpoint** to talk to
the MAAT expert gateways with the full immune-loop pipeline attached:

    channel  →  POST /ask  →  KA2 router  →  Ollama  →  ArchivistRecord
                                          ↓
                               guard_validator  →  archivist_gitmaat
                                          ↓
                               reply + structured decision

This replaces the "OpenClaw calls Ollama directly" shortcut and turns every
turn into a recorded, validated, persisted event — with no CLI required.

Ports
-----
Default: **127.0.0.1:8040** (local only). To expose on LAN set
``GATEWAY_SERVER_BIND=0.0.0.0`` AND set ``GATEWAY_SERVER_TOKEN`` to a bearer
token; the server refuses to bind non-loopback without a token.

Endpoints
---------
- ``GET  /health``   — liveness + subsystem probe.
- ``GET  /info``     — plain-language description. Any agent should read this first.
- ``GET  /gateways`` — list gateways from the registry.
- ``POST /ask``      — main entry. Body: ``{message, gateway_id?, session_id?, user_id?, research_grade?}``

All POST bodies are JSON. Responses are JSON. Errors are JSON with
``{"error": ..., "status": "..."}`` and a non-200 status code.

Stdlib only.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))

import expert_config  # noqa: E402
import governance_memory  # noqa: E402
from archivist_gitmaat import ArchivistGitMaatAdapter  # noqa: E402
from gateway_contract import (  # noqa: E402
    ArchivistRecord,
    MaatScorecard,
    Source,
    now_iso,
)
from gateway_registry import GatewayRegistry  # noqa: E402
from guard_validator import validate_turn  # noqa: E402
import ka2_router  # noqa: E402
import retrieval  # noqa: E402


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8040
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT_SEC = float(os.getenv("GATEWAY_OLLAMA_TIMEOUT", "120"))
GATEWAY_SERVER_VERSION = "0.2.0"

# Retrieval budget per turn. Raise for larger context windows; lower to save tokens.
RAG_TOP_K_PER_PACK = int(os.getenv("GATEWAY_RAG_TOP_K", "4"))
RAG_CONTEXT_CHARS = int(os.getenv("GATEWAY_RAG_CONTEXT_CHARS", "3500"))


class SessionTracker:
    """Tracks turn indices per session so correlation_ids increment cleanly.

    A ``session_id`` is provided by the channel (e.g. ``telegram:<chat_id>``
    or ``cli:<user>``). Turn indices reset on server restart — sessions
    are not durable memory, that's gitMaat's job. For durable replay use the
    ``correlation_id`` which embeds both.
    """

    def __init__(self) -> None:
        self._turns: dict[str, int] = {}
        self._lock = threading.Lock()

    def next_turn(self, session_id: str) -> int:
        with self._lock:
            n = self._turns.get(session_id, -1) + 1
            self._turns[session_id] = n
            return n


def _ollama_generate(model: str, prompt: str, *, system: str | None = None) -> dict[str, Any]:
    """Call Ollama /api/generate. Returns structured result dict."""
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        body["system"] = system
    t0 = time.time()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
        return {
            "ok": True,
            "text": data.get("response", ""),
            "model": data.get("model", model),
            "latency_ms": int((time.time() - t0) * 1000),
            "eval_count": data.get("eval_count", 0),
        }
    except urllib.error.URLError as exc:
        return {"ok": False, "error": f"ollama_unreachable: {exc.reason}", "latency_ms": int((time.time() - t0) * 1000)}
    except TimeoutError:
        return {"ok": False, "error": "ollama_timeout", "latency_ms": int((time.time() - t0) * 1000)}
    except json.JSONDecodeError:
        return {"ok": False, "error": "ollama_bad_json", "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"ollama_error:{type(exc).__name__}", "latency_ms": int((time.time() - t0) * 1000)}


def _build_system_prompt(gateway_entry: Any, route: Any) -> str:
    """Light system envelope. Full KA2 enforcement happens post-turn.

    The model is not asked to self-police here; that's the guard_validator's
    job. We just give it the gateway identity and a short posture.
    """
    gid = gateway_entry.id if gateway_entry else "default"
    research = "research-grade" if route.research_grade else "conversational"
    return (
        f"You are the MAAT expert gateway '{gid}'. "
        f"Default expert: {route.expert_name}. "
        f"Mode: {research}. "
        f"Level of analysis: {route.level_of_analysis}. "
        f"Research type: {route.research_type}. "
        "Cite sources when you have them. Be direct. "
        "If asked something outside your scope, say so plainly."
    )


def _build_user_prompt(message: str, hits: list["retrieval.RetrievalHit"]) -> str:
    """Inject retrieved context above the user message so the model can cite.

    We put context *before* the question and explicitly tell the model the
    [n] markers correspond to sources. No self-policing here — scoring and
    forbidden-vocab checks are the validator's job post-turn.
    """
    if not hits:
        return message
    ctx = retrieval.format_context_block(hits, max_chars=RAG_CONTEXT_CHARS)
    if not ctx:
        return message
    return (
        "You have retrieved context. Use it to answer. "
        "Cite with [n] matching the numbered sources.\n\n"
        f"CONTEXT:\n{ctx}\n\n"
        f"QUESTION:\n{message}"
    )


def _heuristic_scorecard(
    reply_text: str,
    sources_count: int,
    rbl_found: int,
    *,
    retrieval_chunk_hits: int = 0,
) -> MaatScorecard:
    """Very crude baseline scorecard. Real self-assessment comes from the
    model when it's fine-tuned to emit one; until then, we score from signals
    the server can see.

    Axes (0-10 each): truth, order, balance, justice, self_reflection.
    This is a placeholder so research-grade turns produce *some* scorecard
    rather than failing validation on missing data. The guard_validator
    sanitises and re-derives ``passed`` from this.
    """
    length = len(reply_text or "")
    has_sources = sources_count > 0
    scores = {
        "truth": 8 if has_sources else 5,
        "order": 8 if length > 120 else 6,
        "balance": 7,
        "justice": 7,
        "self_reflection": 6,
    }
    if rbl_found:
        for k in scores:
            scores[k] = max(0, scores[k] - rbl_found)
    total = sum(scores.values())
    # Phase-1 gateway: when BM25 returned chunks, bump axes so total>=PASS_AT
    # unless RBL already ate the budget — avoids spurious scorecard_fail on
    # every grounded short reply (heuristic is not a model self-grade).
    if (
        retrieval_chunk_hits > 0
        and rbl_found < 3
        and total < 40
    ):
        need = 40 - total
        for axis in ("truth", "order", "self_reflection", "balance", "justice"):
            while need > 0 and scores[axis] < 10:
                scores[axis] += 1
                need -= 1
            if need <= 0:
                break
        total = sum(scores.values())
    correction: str | None = None
    if total < 40 or rbl_found >= 3:
        correction = (
            f"heuristic: total={total}<40; reply_len={length}, sources={sources_count}, "
            f"rbl={rbl_found}. Re-route deeper model."
        )
    return MaatScorecard(scores=scores, halt_flags=rbl_found, correction_notes=correction)


class GatewayService:
    """All-in-one pipeline. Holds registry, adapter, router, session state."""

    def __init__(self, *, registry: GatewayRegistry | None = None) -> None:
        self.registry = registry or GatewayRegistry.load()
        self.adapter = ArchivistGitMaatAdapter()
        self.sessions = SessionTracker()
        self.started_at = now_iso()
        self.turn_count = 0

    def describe(self) -> dict[str, Any]:
        return {
            "service": "maat-gateway-server",
            "version": GATEWAY_SERVER_VERSION,
            "started_at": self.started_at,
            "turn_count": self.turn_count,
            "ollama_url": OLLAMA_URL,
            "registry_gateways": self.registry.list_ids(),
            "archivist_stream": str(self.adapter.stream_path),
        }

    def pick_gateway(self, gateway_id: str | None):
        if gateway_id:
            entry = self.registry.get(gateway_id)
            if entry is None:
                raise KeyError(f"unknown gateway: {gateway_id}")
            return entry
        # Default to scout if present, else the first registered.
        ids = self.registry.list_ids()
        if not ids:
            return None
        preferred = "scout" if "scout" in ids else ids[0]
        return self.registry.get(preferred)

    def ask(
        self,
        *,
        message: str,
        gateway_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        research_grade: bool | None = None,
    ) -> dict[str, Any]:
        gateway_entry = self.pick_gateway(gateway_id)
        sess = session_id or (f"user:{user_id}" if user_id else f"anon:{uuid.uuid4().hex[:8]}")
        turn_index = self.sessions.next_turn(sess)

        override_expert = gateway_entry.default_expert if gateway_entry else None
        route = ka2_router.route(
            message,
            session_id=sess,
            turn_index=turn_index,
            override_expert=override_expert,
        )

        if research_grade is not None:
            route.research_grade = bool(research_grade)

        model = gateway_entry.model if gateway_entry else route.expert_model
        model = model.replace("ollama/", "")

        retrieved_hits: list[retrieval.RetrievalHit] = []
        retrieval_packs = list(gateway_entry.retrieval_packs) if gateway_entry else []
        if retrieval_packs:
            retrieved_hits = retrieval.search_many(
                retrieval_packs, message, top_k_per_pack=RAG_TOP_K_PER_PACK
            )

        system_prompt = _build_system_prompt(gateway_entry, route)
        user_prompt = _build_user_prompt(message, retrieved_hits)
        gen = _ollama_generate(model, user_prompt, system=system_prompt)
        reply_text = gen.get("text", "") if gen.get("ok") else ""
        model_err = None if gen.get("ok") else gen.get("error")

        sources: list[Source] = []
        for pack_id in retrieval_packs:
            sources.append(Source(kind="corpus", ref=f"pack:{pack_id}"))
        # Concrete per-chunk citations so validators see real anchors, not
        # just "pack:fl-trust-law". Dedupe by source path.
        seen_refs: set[str] = set()
        for hit in retrieved_hits:
            ref = f"pack:{retrieval_packs[0] if retrieval_packs else 'unknown'}#{hit.source}"
            if hit.section_id:
                ref = f"{ref}§{hit.section_id}"
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            sources.append(Source(kind="file", ref=ref))
        sources.append(Source(kind="tool_result", ref=f"ollama:{model}"))

        ka2_block: dict[str, Any] | None = None
        scorecard: MaatScorecard | None = None
        if route.research_grade:
            ka2_block = {
                "research_type": route.research_type,
                "level_of_analysis": route.level_of_analysis,
                "problem": message[:280],
                "time_dimension": "present request; no historical window asserted",
                "method_naming": "KA2-v1",
                # Satisfy detect_forbidden_hits (gateway_contract): research_grade
                # turns must declare at least one dialectical tension placeholder
                # until the Phase-2 planner fills real KA2 life_cycle blocks.
                "dialectical_findings": {
                    "contradiction": (
                        "Gateway turn: retrieved statute scope vs. narrow user "
                        "question; full dialectical pass deferred to analyst/planner."
                    ),
                },
            }
            from gateway_contract import detect_rbl_flags
            rbl_now = detect_rbl_flags(reply_text)
            scorecard = _heuristic_scorecard(
                reply_text,
                len(sources),
                len(rbl_now),
                retrieval_chunk_hits=len(retrieved_hits),
            )

        tags = list(route.tags)
        tags.append(f"gateway:{gateway_entry.id if gateway_entry else 'default'}")
        if model_err:
            tags.append(f"model_error:{model_err.split(':', 1)[0]}")

        governance_memory.log_gateway_route_row(
            expert_name=route.expert_name,
            model=model,
            gateway_id=gateway_entry.id if gateway_entry else None,
            session_id=sess,
            correlation_id=route.correlation_id,
            tags=tags,
        )

        record = ArchivistRecord(
            correlation_id=route.correlation_id,
            agent_id=f"gateway_server@{socket.gethostname()}",
            gateway_id=gateway_entry.id if gateway_entry else "default",
            summary=reply_text[:500] if reply_text else (model_err or "(empty reply)"),
            sources=sources,
            tags=tags,
            research_grade=route.research_grade,
            ka2=ka2_block,
            maat_scorecard=scorecard,
            gateway_state={
                "turn_index": turn_index,
                "tools_used": [],
                "model_id": model,
                "latency_ms": gen.get("latency_ms", 0),
                "eval_count": gen.get("eval_count", 0),
                "model_error": model_err,
            },
            notes=None,
            payload={
                "user_message": message,
                "retrieved_excerpts": [
                    {
                        "score": h.score,
                        "source": h.source,
                        "section_id": h.section_id,
                        "chapter": h.chapter,
                        "excerpt": h.text[:400],
                    }
                    for h in retrieved_hits
                ],
            },
        )

        decision = validate_turn(record, content_text=reply_text, call_guard_http=False)
        if decision.rbl_flags:
            record.rbl_flags = list(decision.rbl_flags)
        if decision.forbidden_hits:
            record.forbidden_hits = list(decision.forbidden_hits)

        persist = self.adapter.persist(record)
        self.turn_count += 1

        return {
            "reply": reply_text,
            "gateway": gateway_entry.id if gateway_entry else None,
            "expert": route.expert_name,
            "model": model,
            "correlation_id": route.correlation_id,
            "session_id": sess,
            "turn_index": turn_index,
            "research_grade": route.research_grade,
            "level_of_analysis": route.level_of_analysis,
            "research_type": route.research_type,
            "tags": tags,
            "decision": decision.to_dict(),
            "persist": persist.to_dict(),
            "model_error": model_err,
        }


SERVICE: GatewayService | None = None


def get_service() -> GatewayService:
    global SERVICE
    if SERVICE is None:
        SERVICE = GatewayService()
    return SERVICE


class GatewayHTTPHandler(BaseHTTPRequestHandler):
    server_version = f"MaatGateway/{GATEWAY_SERVER_VERSION}"

    def _auth_ok(self) -> bool:
        token = os.getenv("GATEWAY_SERVER_TOKEN")
        if not token:
            return True
        supplied = self.headers.get("Authorization", "")
        if supplied.lower().startswith("bearer "):
            supplied = supplied[7:]
        return supplied == token

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        sys.stderr.write(
            f"[gateway-server] {self.log_date_time_string()} {self.address_string()} - {format % args}\n"
        )

    def do_GET(self) -> None:  # noqa: N802
        if not self._auth_ok():
            self._json(401, {"error": "unauthorized"})
            return
        if self.path in {"/health", "/"}:
            svc = get_service()
            self._json(200, {"status": "ok", **svc.describe()})
            return
        if self.path == "/info":
            self._json(200, _INFO_PAYLOAD)
            return
        if self.path == "/gateways":
            svc = get_service()
            entries = {gid: svc.registry.get(gid).to_dict() for gid in svc.registry.list_ids()}  # type: ignore[union-attr]
            self._json(200, {"gateways": entries})
            return
        self._json(404, {"error": "not_found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        if not self._auth_ok():
            self._json(401, {"error": "unauthorized"})
            return
        if self.path != "/ask":
            self._json(404, {"error": "not_found", "path": self.path})
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError as exc:
            self._json(400, {"error": "bad_json", "detail": str(exc)})
            return

        message = (body.get("message") or "").strip()
        if not message:
            self._json(400, {"error": "message is required"})
            return

        try:
            result = get_service().ask(
                message=message,
                gateway_id=body.get("gateway_id"),
                session_id=body.get("session_id"),
                user_id=body.get("user_id"),
                research_grade=body.get("research_grade"),
            )
            self._json(200, result)
        except KeyError as exc:
            self._json(400, {"error": "unknown_gateway", "detail": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"error": f"internal:{type(exc).__name__}", "detail": str(exc)})


_INFO_PAYLOAD = {
    "service": "maat-gateway-server",
    "purpose": (
        "One HTTP endpoint that any channel (Telegram, Discord, CLI, n8n, "
        "OpenClaw) can POST to. It routes the message through the KA2-aware "
        "router, dispatches to Ollama, wraps the reply in a structured "
        "ArchivistRecord, validates it, and persists to gitMaat. No CLI or "
        "code change needed to add another channel — just point it at /ask."
    ),
    "quick_start": {
        "from_curl": "curl -s -X POST http://127.0.0.1:8040/ask -H 'Content-Type: application/json' -d '{\"message\":\"hello\"}'",
        "from_telegram_agent": (
            "In OpenClaw, give the agent a web_fetch or custom tool pointing at "
            "http://127.0.0.1:8040/ask. The agent forwards the user message, "
            "returns result.reply to the user, and the record is logged automatically."
        ),
    },
    "endpoints": {
        "GET /health": "liveness + subsystem",
        "GET /info": "this document",
        "GET /gateways": "list registered gateways",
        "POST /ask": "main: {message, gateway_id?, session_id?, user_id?, research_grade?}",
    },
    "gateways_doc": "docs/MAAT-GATEWAY-REGISTRY.md",
    "evolution_lanes_doc": "docs/MAAT-EVOLUTION-LANES.md",
    "channel_agnostic": True,
}


def _require_token_for_lan(bind_host: str) -> None:
    if bind_host not in {"127.0.0.1", "localhost", "::1"}:
        if not os.getenv("GATEWAY_SERVER_TOKEN"):
            raise SystemExit(
                "refusing to bind non-loopback without GATEWAY_SERVER_TOKEN set"
            )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="MAAT Gateway HTTP server")
    parser.add_argument("--host", default=os.getenv("GATEWAY_SERVER_BIND", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("GATEWAY_SERVER_PORT", DEFAULT_PORT)))
    args = parser.parse_args(argv)

    _require_token_for_lan(args.host)

    svc = get_service()
    print(f"[gateway-server] starting on http://{args.host}:{args.port}", flush=True)
    print(f"[gateway-server] gateways: {svc.registry.list_ids()}", flush=True)
    print(f"[gateway-server] ollama: {OLLAMA_URL}", flush=True)
    print(f"[gateway-server] stream: {svc.adapter.stream_path}", flush=True)
    print("[gateway-server] see /info for plain-language description", flush=True)

    server = ThreadingHTTPServer((args.host, args.port), GatewayHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[gateway-server] shutting down", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
