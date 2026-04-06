# Area: Hooks
# PRD: plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.

"""Tests for hooks/parse_config.py — YAML config parser fallback for shell hooks."""

import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "hooks" / "parse_config.py"
CONFIG = PROJECT_ROOT / "compliance_config.yaml"


def run(key_path):
    """Run parse_config.py with the given key path and return (stdout, returncode)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), key_path],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    return result.stdout.strip(), result.returncode


class TestScalarValues:
    def test_integer_value(self):
        out, code = run("pre_commit.max_file_lines")
        assert code == 0
        assert out == "150"

    def test_boolean_required(self):
        out, code = run("pre_commit.file_header.required")
        assert code == 0
        assert out.lower() in ("true", "false")

    def test_version(self):
        out, code = run("version")
        assert code == 0
        assert out != ""


class TestListValues:
    def test_source_dirs_contains_src(self):
        out, code = run("pre_commit.source_dirs")
        assert code == 0
        assert "src/" in out.splitlines()

    def test_test_dirs_contains_tests(self):
        out, code = run("pre_commit.test_dirs")
        assert code == 0
        assert "tests/" in out.splitlines()

    def test_test_commands_contains_pytest(self):
        out, code = run("pre_commit.test_commands")
        assert code == 0
        assert any("pytest" in line for line in out.splitlines())


class TestDictValues:
    def test_dict_outputs_key_value_pairs(self):
        out, code = run("pre_commit.file_header")
        assert code == 0
        # Should contain key=value pairs
        assert "=" in out


class TestMissingKey:
    def test_nonexistent_key_exits_nonzero(self):
        _, code = run("nonexistent.key")
        assert code != 0

    def test_partial_path_nonexistent(self):
        _, code = run("pre_commit.does_not_exist")
        assert code != 0


class TestUsageError:
    def test_no_args_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0
