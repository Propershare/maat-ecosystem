"""Tests for workspace_inventory.py — the script that powers refs/workspace-inventory-bom-2026-08-08."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "workspace_inventory.py"
)
PYTHON = sys.executable


def run_inventory(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd,
    )


def test_tsv_format_emits_header_and_rows(tmp_path):
    """TSV output has a known header + at least one data row."""
    (tmp_path / "marker.txt").write_text("x")
    result = run_inventory(str(tmp_path))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    lines = result.stdout.strip().splitlines()
    assert lines[0].startswith("depth\tpath\ttype\tbytes")
    assert len(lines) >= 2  # at least header + 1 row


def test_markdown_format_is_table(tmp_path):
    (tmp_path / "marker.txt").write_text("x")
    result = run_inventory(str(tmp_path), "--format", "markdown")
    assert result.returncode == 0
    assert result.stdout.startswith("| path | type |")
    assert "|------|" in result.stdout


def test_json_format_is_parseable(tmp_path):
    result = run_inventory(str(tmp_path), "--format", "json")
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert "count" in parsed
    assert "entries" in parsed
    assert parsed["count"] == len(parsed["entries"])


def test_rejects_nonexistent_root(tmp_path):
    result = run_inventory(str(tmp_path / "does-not-exist"))
    assert result.returncode != 0
    assert "not a directory" in result.stderr


def test_depth_two_includes_nested_dirs(tmp_path):
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "leaf.txt").write_text("hi")
    result = run_inventory(str(tmp_path), "--depth", "2")
    paths = [line.split("\t")[1] for line in result.stdout.splitlines()[1:]]
    assert any("subdir" in p for p in paths)
    assert any("leaf.txt" in p for p in paths)


def test_default_excludes_skip_node_modules(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "should_skip.js").write_text("x")
    (tmp_path / "kept.js").write_text("x")
    result = run_inventory(str(tmp_path))
    paths = [line.split("\t")[1] for line in result.stdout.splitlines()[1:]]
    assert not any("node_modules" in p for p in paths)
    assert any("kept.js" in p for p in paths)


def test_custom_exclude_via_flag(tmp_path):
    (tmp_path / "skipme").mkdir()
    (tmp_path / "skipme" / "x.txt").write_text("x")
    (tmp_path / "keepme.txt").write_text("x")
    result = run_inventory(str(tmp_path), "--exclude", "skipme")
    paths = [line.split("\t")[1] for line in result.stdout.splitlines()[1:]]
    assert not any("skipme" in p for p in paths)


def test_handles_permission_errors_gracefully(tmp_path, monkeypatch):
    """Permission-denied dirs should not crash the whole walk."""
    secret = tmp_path / "secret"
    secret.mkdir()
    secret.chmod(0o000)
    try:
        result = run_inventory(str(tmp_path))
        # Even with a fully-blocked subdir, we should get a clean exit
        assert result.returncode == 0
    finally:
        secret.chmod(0o755)


def test_size_field_is_integer(tmp_path):
    """The bytes column is a plain integer, not humanized."""
    f = tmp_path / "x.txt"
    f.write_text("hello")  # 5 bytes
    result = run_inventory(str(tmp_path))
    # find the line for x.txt
    for line in result.stdout.splitlines()[1:]:
        parts = line.split("\t")
        if "x.txt" in parts[1]:
            assert parts[3].isdigit(), f"bytes column must be int, got {parts[3]!r}"
            assert int(parts[3]) == 5
            return
    pytest.fail(f"x.txt not found in output: {result.stdout}")
