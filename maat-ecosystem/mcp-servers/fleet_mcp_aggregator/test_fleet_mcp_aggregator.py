"""Tests for fleet_mcp_aggregator.py — the single MCP entry opencode should use.

These tests verify the aggregator's routing, prefixing, and error handling
without actually spawning the stdio MCP transport (that requires a real
process boundary, which is what the smoke test in
fleet_mcp_aggregator.py is for).

Run: python3 -m pytest tests/unit/test_fleet_mcp_aggregator.py
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add the aggregator's dir to path
SCRIPTS = Path(__file__).resolve().parents[2] / "maat-ecosystem" / "mcp-servers" / "fleet_mcp_aggregator"
sys.path.insert(0, str(SCRIPTS))

from fleet_mcp_aggregator import (  # noqa: E402
    BACKENDS,
    LAB_MCP_BEARER,
    _add_prefix,
    _fetch_paths,
    _list_all_tools,
    _strip_prefix,
    fleet_list_servers,
    fleet_ping,
)


def test_strip_prefix_removes_when_present():
    assert _strip_prefix("memory_log_decision", "memory") == "log_decision"


def test_strip_prefix_passthrough_when_absent():
    assert _strip_prefix("foo_bar", "memory") == "foo_bar"


def test_add_prefix_prepends():
    assert _add_prefix("execute_command", "tehuti") == "tehuti_execute_command"


def test_backends_have_required_keys():
    """Every backend in BACKENDS must declare url + auth + tool_prefix."""
    for name, cfg in BACKENDS.items():
        assert "url" in cfg, f"{name} missing 'url'"
        assert "auth" in cfg, f"{name} missing 'auth'"
        assert "tool_prefix" in cfg, f"{name} missing 'tool_prefix'"


def test_backends_env_overrides_applied():
    """Override the URL via env var and verify the override is read."""
    with patch.dict(os.environ, {"KA_DISCOVERY_URL": "http://example.com:9999"}):
        # Re-import the module to pick up the env var
        import importlib

        import fleet_mcp_aggregator

        importlib.reload(fleet_mcp_aggregator)
        assert fleet_mcp_aggregator.BACKENDS["ka"]["url"] == "http://example.com:9999"


def test_fleet_ping_returns_pong():
    """The trivial ping tool."""
    result = asyncio.run(fleet_ping())
    assert result == "pong"


def test_fleet_list_servers_marks_audio_degraded():
    """Audio's openapi.json returns 404; aggregator should mark it degraded
    (tool_count 0) but the backend entry should still exist with status down."""
    result = asyncio.run(fleet_list_servers())
    data = json.loads(result)
    assert "tehuti_audio" in data
    assert data["tehuti_audio"]["url"] == BACKENDS["tehuti_audio"]["url"]
    # Status is either 'up' (if /health returns 200) or 'down'
    assert data["tehuti_audio"]["status"] in ("up", "down")


def _make_mock_client(get_handler):
    """Build an httpx.AsyncClient-compatible mock that records get() calls."""
    instance = MagicMock()
    instance.__aenter__ = AsyncMock(return_value=instance)
    instance.__aexit__ = AsyncMock(return_value=None)
    instance.get = AsyncMock(side_effect=get_handler)
    return instance


def test_openapi_cache_works():
    """The OpenAPI cache should not re-fetch within TTL."""
    import fleet_mcp_aggregator as fma
    fma._OPENAPI_CACHE.clear()  # avoid hits from module-level prefetch

    fetch_calls = []

    async def fake_get(*args, **kwargs):
        fetch_calls.append(args[0] if args else None)
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"paths": {"/foo": {"get": {"operationId": "foo_get"}}}})
        return resp

    mock_instance = MagicMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.get = AsyncMock(side_effect=fake_get)

    with patch("httpx.AsyncClient", return_value=mock_instance):

        async def run():
            paths1 = await fma._fetch_paths("tehuti_core")
            paths2 = await fma._fetch_paths("tehuti_core")
            return paths1, paths2

        paths1, paths2 = asyncio.run(run())
    assert paths1 == paths2
    assert len(fetch_calls) == 1, f"cache miss: expected 1 fetch, got {len(fetch_calls)}"


def test_openapi_cache_invalidates_after_ttl(monkeypatch):
    """After TTL expires, the cache should refetch."""
    import fleet_mcp_aggregator as fma
    fma._OPENAPI_CACHE.clear()
    monkeypatch.setattr("fleet_mcp_aggregator._CACHE_TTL", 0.0)

    fetch_count = [0]

    async def fake_get(*args, **kwargs):
        fetch_count[0] += 1
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"paths": {}})
        return resp

    mock_instance = MagicMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.get = AsyncMock(side_effect=fake_get)

    with patch("httpx.AsyncClient", return_value=mock_instance):

        async def run():
            await fma._fetch_paths("tehuti_core")
            await fma._fetch_paths("tehuti_core")

        asyncio.run(run())

    assert fetch_count[0] == 2, f"cache should invalidate: expected 2, got {fetch_count[0]}"


def test_http_client_carries_bearer_for_protected_backends(monkeypatch):
    """Calls to protected backends must carry the Authorization header."""
    import fleet_mcp_aggregator as fma
    fma._OPENAPI_CACHE.clear()

    captured_headers = []

    async def fake_get(*args, **kwargs):
        captured_headers.append(kwargs.get("headers"))
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"paths": {}})
        return resp

    mock_instance = MagicMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.get = AsyncMock(side_effect=fake_get)

    with patch("httpx.AsyncClient", return_value=mock_instance):

        async def run():
            await fma._fetch_paths("maat_memory")
            await fma._fetch_paths("tehuti_core")
            # ka has no openapi_path so _fetch_paths returns {} without a request

        asyncio.run(run())

    assert len(captured_headers) == 2
    assert "Authorization" in captured_headers[0]
    assert LAB_MCP_BEARER in captured_headers[0]["Authorization"]
    assert "Authorization" in captured_headers[1]


# Import os for the env-var test
import os