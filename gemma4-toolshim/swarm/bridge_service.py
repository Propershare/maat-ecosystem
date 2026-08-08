"""
Swarm bridge: router.route_message(), gitMaat + RAG prefetch, Ollama reply.

HTTP:
  POST /invoke — JSON { "message" } or { "text" }
  POST /telegram/webhook — Telegram Update (needs TELEGRAM_BOT_TOKEN)

Env:
  MAAT_MEMORY_MCP_* — maat_bridge.py
  PGVECTOR_DB_URL — RAG (maat_knowledge)
  SWARM_BRIDGE_HOST / SWARM_BRIDGE_PORT — bind (default 127.0.0.1:18080)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request

# Ensure swarm modules resolve when run as `uvicorn bridge_service:app`
_SWARM = Path(__file__).resolve().parent
if str(_SWARM) not in sys.path:
    sys.path.insert(0, str(_SWARM))

from expert_config import SETTINGS  # noqa: E402
from maat_bridge import query_memory  # noqa: E402
from router import route_message  # noqa: E402

app = FastAPI(title="Gemma4 Swarm Bridge", version="0.1.0")

_rag_maat: Any = None


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _rag_search_chunks(query: str, top_k: int = 5) -> str:
    """Similarity search maat_knowledge via MaatRAG (soft-fail)."""
    global _rag_maat
    try:
        if _rag_maat is None:
            root = _workspace_root()
            ml = root / "maatlangchain"
            if not ml.is_dir():
                return ""
            sys.path.insert(0, str(ml))
            os.environ.setdefault("PGVECTOR_DB_URL", _load_pgvector_url() or "")
            if not os.environ.get("PGVECTOR_DB_URL"):
                return ""
            from langchain_community.vectorstores import PGVector
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings

            from core.chains.maat_rag import MaatRAG

            emb = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )
            vs = PGVector(
                connection_string=os.environ["PGVECTOR_DB_URL"],
                embedding_function=emb,
                collection_name="maat_knowledge",
            )
            _rag_maat = MaatRAG(vs, emb)

        docs = _rag_maat.search_similar(query, "maat_knowledge", top_k=top_k)
        if not docs:
            return ""
        parts: List[str] = []
        for d in docs:
            src = (d.metadata or {}).get("source", "")
            parts.append(f"- ({src}) {d.page_content[:1200]}")
        return "\n".join(parts)
    except Exception as e:
        return f"[RAG unavailable: {e}]"


def _load_pgvector_url() -> Optional[str]:
    url = os.environ.get("PGVECTOR_DB_URL")
    if url:
        return url.strip().strip('"').strip("'")
    root = _workspace_root()
    for env_path in (root / ".env", root / "maatlangchain" / ".env"):
        if not env_path.exists():
            continue
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("PGVECTOR_DB_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _wants_gitmaat_prefetch(tools: List[str]) -> bool:
    def _hit(t: str) -> bool:
        tl = t.lower()
        return t == "query_gitmaat" or t == "memory_search" or "gitmaat" in tl

    return any(_hit(t) for t in tools)


def _wants_rag_prefetch(expert_name: str, tools: List[str]) -> bool:
    if expert_name == "rag-expert":
        return True
    return any("rag" in t.lower() for t in tools)


def _build_system_prompt(expert: Dict[str, Any]) -> str:
    tools = expert.get("tools") or []
    tool_line = ", ".join(tools) if tools else "(none listed)"
    return (
        f"You are the `{expert['name']}` expert in the Tehuti Lab swarm.\n"
        f"Role: {expert.get('description', '')}\n"
        "Declared tools (context is injected by the bridge): "
        f"{tool_line}\n"
        "Answer clearly. Use provided context blocks when present."
    )


def _augment_user_message(message: str, expert: Dict[str, Any]) -> str:
    blocks: List[str] = []
    tools: List[str] = list(expert.get("tools") or [])
    name = str(expert.get("name", ""))

    if _wants_gitmaat_prefetch(tools):
        mem = query_memory(message, limit=5)
        if mem:
            blob = json.dumps(mem, default=str)[:6000]
            blocks.append("[gitMaat memory_search]\n" + blob)

    if _wants_rag_prefetch(name, tools):
        rag = _rag_search_chunks(message, top_k=5)
        if rag:
            blocks.append("[RAG maat_knowledge]\n" + rag[:8000])

    if not blocks:
        return message
    return "\n\n".join(blocks) + "\n\n---\nUser message:\n" + message


def _ollama_chat(model: str, system: str, user: str) -> str:
    base = str(SETTINGS.get("ollama_url", "http://127.0.0.1:11434")).rstrip("/")
    url = f"{base}/api/chat"
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        snippet = e.read()[:500] if e.fp else b""
        detail = f"ollama HTTP {e.code}: {snippet!r}"
        raise HTTPException(status_code=502, detail=detail) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ollama error: {e}") from e

    msg = (data.get("message") or {}) if isinstance(data, dict) else {}
    content = msg.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    return json.dumps(data)[:8000]


def _invoke_message(message: str) -> Dict[str, Any]:
    text = (message or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="missing message")

    expert = route_message(text)
    model = str(expert.get("model") or SETTINGS.get("fallback_model") or "gemma4:e4b")
    system = _build_system_prompt(expert)
    user_augmented = _augment_user_message(text, expert)
    reply = _ollama_chat(model, system, user_augmented)

    return {
        "reply": reply,
        "expert": expert.get("name"),
        "model": model,
        "tools_declared": expert.get("tools"),
    }


@app.post("/invoke")
async def invoke(body: Dict[str, Any]) -> Dict[str, Any]:
    msg = body.get("message") if isinstance(body.get("message"), str) else None
    if msg is None and isinstance(body.get("text"), str):
        msg = body["text"]
    if msg is None:
        raise HTTPException(
            status_code=400,
            detail='expected JSON with "message" or "text"',
        )
    return _invoke_message(msg)


def _telegram_send(chat_id: int, text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN not set")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text[:4090],
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        d = f"telegram send failed: {e}"
        raise HTTPException(status_code=502, detail=d) from e
    if not raw.get("ok"):
        raise HTTPException(status_code=502, detail=f"telegram API: {raw}")


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> Dict[str, str]:
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if secret:
        hdr = "X-Telegram-Bot-Api-Secret-Token"
        got = request.headers.get(hdr, "")
        if got != secret:
            raise HTTPException(status_code=401, detail="invalid webhook secret")

    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    msg = update.get("message") or update.get("edited_message")
    if not isinstance(msg, dict):
        return {"ok": "true"}
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = msg.get("text") or msg.get("caption") or ""
    if chat_id is None or not str(text).strip():
        return {"ok": "true"}

    out = _invoke_message(str(text))
    _telegram_send(int(chat_id), out["reply"])
    return {"ok": "true"}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("SWARM_BRIDGE_HOST", "127.0.0.1")
    port = int(os.environ.get("SWARM_BRIDGE_PORT", "18080"))
    uvicorn.run(app, host=host, port=port)
