#!/usr/bin/env python3
"""
Local regression tests for gemma4:e2b (no Docker).

Usage:
  python3 test_gemma4_e2b_local.py

Env:
  OLLAMA_BASE  default http://127.0.0.1:11434
  SHIM_BASE    optional, e.g. http://127.0.0.1:11435 — if set, runs OpenAI-format shim check
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
SHIM_BASE = os.environ.get("SHIM_BASE", "").rstrip("/")
MODEL = os.environ.get("OLLAMA_TEST_MODEL", "gemma4:e2b")


def _post(url: str, payload: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST", headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(url: str, timeout: int = 10) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_tags() -> None:
    tags = _get(f"{OLLAMA_BASE}/api/tags")
    names = {m["name"] for m in tags.get("models", [])}
    if MODEL not in names:
        raise SystemExit(f"FAIL: {MODEL} not in ollama list. Run: ollama pull {MODEL}")


def test_simple_chat() -> None:
    r = _post(
        f"{OLLAMA_BASE}/api/chat",
        {
            "model": MODEL,
            "stream": False,
            "messages": [{"role": "user", "content": "Reply with exactly: E2B_OK"}],
            "options": {"num_predict": 96},
        },
    )
    msg = r.get("message") or {}
    content = msg.get("content") or ""
    thinking = msg.get("thinking") or ""
    blob = f"{content}\n{thinking}"
    if "E2B_OK" not in blob:
        raise SystemExit(
            f"FAIL: expected E2B_OK in content or thinking, got content={content!r} thinking_snip={thinking[:200]!r}"
        )


def test_native_tool_calls() -> None:
    r = _post(
        f"{OLLAMA_BASE}/api/chat",
        {
            "model": MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "Call the bash tool to list /tmp using command ls /tmp",
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "bash",
                        "description": "Run shell",
                        "parameters": {
                            "type": "object",
                            "properties": {"command": {"type": "string"}},
                            "required": ["command"],
                        },
                    },
                }
            ],
        },
    )
    msg = r.get("message") or {}
    tcs = msg.get("tool_calls") or []
    if not tcs:
        raise SystemExit(f"FAIL: no tool_calls in Ollama response: {json.dumps(msg)[:500]}")
    fn = (tcs[0].get("function") or {})
    if fn.get("name") != "bash":
        raise SystemExit(f"FAIL: expected bash, got {fn.get('name')!r}")
    args = fn.get("arguments") or {}
    if isinstance(args, str):
        args = json.loads(args)
    cmd = (args.get("command") or "").strip()
    if "ls" not in cmd or "/tmp" not in cmd:
        raise SystemExit(f"FAIL: bad command args: {args!r}")


def test_shim_openai() -> None:
    if not SHIM_BASE:
        print("SKIP: SHIM_BASE not set (optional shim OpenAI-format test)")
        return
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "Call bash with command: ls /tmp",
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "Run shell",
                    "parameters": {
                        "type": "object",
                        "properties": {"command": {"type": "string"}},
                        "required": ["command"],
                    },
                },
            }
        ],
    }
    r = _post(f"{SHIM_BASE}/v1/chat/completions", payload)
    choice = (r.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    tcs = msg.get("tool_calls") or []
    if not tcs:
        raise SystemExit(f"FAIL: shim returned no tool_calls: {json.dumps(r)[:600]}")
    fn = tcs[0].get("function") or {}
    if fn.get("name") != "bash":
        raise SystemExit(f"FAIL: shim tool name {fn.get('name')!r}")


def main() -> int:
    try:
        test_tags()
        print(f"OK  tags: {MODEL} present")
        test_simple_chat()
        print("OK  simple chat")
        test_native_tool_calls()
        print("OK  native tool_calls via Ollama /api/chat")
        test_shim_openai()
        if SHIM_BASE:
            print("OK  shim /v1/chat/completions")
    except urllib.error.URLError as e:
        print(f"FAIL: network: {e}", file=sys.stderr)
        return 1
    print("\nAll required tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
