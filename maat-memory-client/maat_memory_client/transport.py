"""HTTP transport to mcpo Maat Memory tools."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


def call_tool(
    base_url: str,
    tool_name: str,
    arguments: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    url = f"{base_url.rstrip('/')}/{tool_name}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    payload = json.dumps(arguments).encode("utf-8")
    req = Request(url, data=payload, headers=headers, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def call_tool_safe(
    base_url: str,
    tool_name: str,
    arguments: Dict[str, Any],
    *,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    strict: bool = False,
) -> Any:
    try:
        return call_tool(base_url, tool_name, arguments, api_key=api_key, timeout=timeout)
    except HTTPError as e:
        err = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        msg = f"HTTP {e.code} for {tool_name}: {err[:500]}"
        log.warning(msg)
        if strict:
            raise RuntimeError(msg) from e
        return None
    except (URLError, TimeoutError, OSError) as e:
        msg = f"Maat Memory unreachable ({tool_name}): {e}"
        log.warning(msg)
        if strict:
            raise RuntimeError(msg) from e
        return None


def unwrap_search_results(raw: Any) -> list[dict]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("❌"):
            log.warning("Maat Memory tool error: %s", s[:300])
            return []
        try:
            parsed = json.loads(s)
        except json.JSONDecodeError:
            return [{"summary": s[:2000]}]
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
        if isinstance(parsed, dict):
            return [parsed]
    return []
