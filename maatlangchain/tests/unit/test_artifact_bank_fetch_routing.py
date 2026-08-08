"""
Regression tests for ArtifactBank.fetch() input routing.

These tests pin the routing contract:
  - maat://object/<sha>          -> _fetch_sha
  - maat://artifact/<slug>       -> _fetch_slug
  - bare sha (64 hex)            -> _fetch_sha
  - bare slug (refs/... shape)   -> _fetch_slug
  - file:// URI                  -> local file read
  - bare local path that exists  -> local file read
  - empty string                 -> {ok: False, error: empty_uri}

Bug history: 2026-08-08, fetch() routed bare slugs (no scheme) through the
file-path branch and returned not_found_on_this_host instead of slug_not_found.
The fix added a slug-shape detector between the maat:// branch and the
file:// branch. This file locks in the new contract.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Allow `from maat_memory.memory_plane import ArtifactBank` from a tests/ subdir
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from maat_memory.memory_plane import ArtifactBank  # noqa: E402


@pytest.fixture
def bank() -> ArtifactBank:
    return ArtifactBank()


# A canonical 64-hex sha used across tests. No real artifact with this sha
# exists; the _fetch_sha return value is mocked so the sha never reaches DB.
SHA = "a" * 64


@pytest.fixture
def patched_fetches(bank):
    """
    Patch _fetch_slug and _fetch_sha so tests assert routing without DB.

    Returns a dict that records which helper was called and with what args.
    The fake implementations always record the call; tests may override
    side_effect to simulate specific responses (the recording is preserved
    because we keep the closure-based recorder around).
    """
    calls = {"sha": [], "slug": []}

    def record_and_default(kind, key, default_response):
        calls[kind].append(key)
        return default_response

    def make_slug_default():
        def _impl(slug: str):
            return record_and_default("slug", slug, {
                "ok": True,
                "sha256": SHA,
                "bytes": 100,
                "text": "<fake>",
                "slug": slug,
                "source": "object_store",
            })
        return _impl

    def make_sha_default():
        def _impl(sha: str):
            return record_and_default("sha", sha, {
                "ok": True,
                "sha256": sha,
                "bytes": 100,
                "text": "<fake>",
                "source": "object_store",
            })
        return _impl

    # Use MagicMock so tests can override side_effect without losing our recording
    from unittest.mock import MagicMock
    m_slug = MagicMock(side_effect=make_slug_default())
    m_sha = MagicMock(side_effect=make_sha_default())

    with patch.object(bank, "_fetch_sha", m_sha), \
         patch.object(bank, "_fetch_slug", m_slug):
        yield bank, calls, m_sha, m_slug


# ----------------------------------------------------------------------
# maat:// URIs
# ----------------------------------------------------------------------

class TestMaatObjectUri:
    def test_routes_to_fetch_sha(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch(f"maat://object/{SHA}")
        assert r["ok"] is True
        assert calls["sha"] == [SHA]
        assert calls["slug"] == []

    def test_accepts_uppercase_hex(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch(f"maat://object/{SHA.upper()}")
        assert r["ok"] is True
        # sha should be lowercased before lookup
        assert calls["sha"] == [SHA]


class TestMaatArtifactUri:
    def test_routes_to_fetch_slug(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch("maat://artifact/refs/foo-bar-2026-08-08")
        assert r["ok"] is True
        assert calls["slug"] == ["refs/foo-bar-2026-08-08"]
        assert calls["sha"] == []


# ----------------------------------------------------------------------
# Bare SHA
# ----------------------------------------------------------------------

class TestBareSha:
    def test_routes_to_fetch_sha(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch(SHA)
        assert r["ok"] is True
        assert calls["sha"] == [SHA]
        assert calls["slug"] == []

    def test_accepts_uppercase(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch(SHA.upper())
        assert r["ok"] is True
        assert calls["sha"] == [SHA]


# ----------------------------------------------------------------------
# Bare slug — THE BUG WE FIXED
# ----------------------------------------------------------------------

class TestBareSlug:
    """Regression tests for the 2026-08-08 fetch() routing bug."""

    def test_refs_slug_routes_to_fetch_slug(self, patched_fetches):
        """The original symptom: refs/<slug> returned not_found_on_this_host."""
        bank, calls, _, _ = patched_fetches
        r = bank.fetch("refs/maat-scoring-canon-2026-08-08")
        assert r["ok"] is True, f"expected ok, got {r}"
        assert calls["slug"] == ["refs/maat-scoring-canon-2026-08-08"]
        assert calls["sha"] == []

    def test_two_segment_slug(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch("opencode/lab-powerup-2026-08-08")
        assert r["ok"] is True
        assert calls["slug"] == ["opencode/lab-powerup-2026-08-08"]

    def test_deeply_nested_slug(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        r = bank.fetch("a/b/c/d/e-f-2026-08-08")
        assert r["ok"] is True
        assert calls["slug"] == ["a/b/c/d/e-f-2026-08-08"]

    def test_non_existent_slug_returns_slug_not_found(self, patched_fetches):
        """Negative case: bogus slug still produces a slug-domain error,
        not a file-domain error. Distinguishes the fix from a wild redirect."""
        bank, calls, _, slug_mock = patched_fetches
        # Override the side_effect to simulate a not-found response.
        # The fixture's recorder is no longer in play, so we manually
        # track the call AND return the not-found dict.
        recorded = []

        def fake_not_found(slug: str):
            recorded.append(slug)
            return {"ok": False, "error": "slug_not_found", "slug": slug}

        slug_mock.side_effect = fake_not_found
        r = bank.fetch("refs/does-not-exist-2099-01-01")
        assert r["ok"] is False
        assert r["error"] == "slug_not_found"
        assert recorded == ["refs/does-not-exist-2099-01-01"]


# ----------------------------------------------------------------------
# Slug-shape detection — inputs that MUST NOT route to _fetch_slug
# ----------------------------------------------------------------------

class TestSlugShapeDetector:
    """The detector must reject ambiguous inputs (local files, absolute paths)."""

    def test_absolute_path_routes_to_local(self, patched_fetches, tmp_path):
        bank, calls, _, _ = patched_fetches
        f = tmp_path / "real_file.md"
        f.write_text("hello")
        r = bank.fetch(str(f))
        assert r["ok"] is True
        assert r["source"] == "local_file"
        assert calls["slug"] == []  # must NOT route to slug lookup
        assert calls["sha"] == []

    def test_relative_dot_path_routes_to_local(self, patched_fetches, tmp_path):
        bank, calls, _, _ = patched_fetches
        # cd into tmp_path so "./real.md" resolves
        import os
        old = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / "real.md").write_text("x")
            r = bank.fetch("./real.md")
            assert r["ok"] is True
            assert r["source"] == "local_file"
            assert calls["slug"] == []
        finally:
            os.chdir(old)

    def test_uri_with_uppercase_letters_is_NOT_a_slug(self, patched_fetches):
        """The slug sanitizer only accepts lowercase. Uppercase paths must
        fall through to the file branch (and 404 cleanly if not on disk)."""
        bank, calls, _, _ = patched_fetches
        r = bank.fetch("Refs/Has-Caps-2026-08-08")
        # It should not have hit _fetch_slug (slug regex is lowercase-only)
        assert calls["slug"] == []

    def test_uri_with_colon_is_NOT_a_slug(self, patched_fetches):
        bank, calls, _, _ = patched_fetches
        # A bare scheme-less input with characters the sanitizer strips
        # should not be mistaken for a slug.
        r = bank.fetch("weird name with spaces")
        assert calls["slug"] == []


# ----------------------------------------------------------------------
# Empty / malformed
# ----------------------------------------------------------------------

class TestEmptyAndMalformed:
    def test_empty_string(self, bank):
        r = bank.fetch("")
        assert r["ok"] is False
        assert r["error"] == "empty_uri"

    def test_whitespace_only(self, bank):
        r = bank.fetch("   ")
        # Stripped to "" internally; must produce empty_uri not crash
        assert r["ok"] is False
        assert r["error"] == "empty_uri"
