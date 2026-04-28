# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for hooks/run_provenance_check.py — CHECK 7 audit runner."""
import json
import subprocess
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent.parent  # ClaudeTemplates root
RUNNER = HERE / "hooks" / "run_provenance_check.py"


def _run(cwd, *args):
    """Invoke runner; return (rc, parsed_json)."""
    result = subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=cwd, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, payload, result.stderr


def _fixture_repo(tmp_path, *, config_yaml="", provenance_md=None, parsers=None):
    """Create a minimal repo layout for the runner."""
    (tmp_path / "compliance_config.yaml").write_text(config_yaml)
    if provenance_md is not None:
        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "docs" / "DELIVERABLE_PROVENANCE.md").write_text(provenance_md)
    if parsers:
        (tmp_path / "parsers").mkdir(exist_ok=True)
        (tmp_path / "parsers" / "__init__.py").write_text("")
        for name, content in parsers.items():
            (tmp_path / "parsers" / f"{name}.py").write_text(content)
    return tmp_path


def test_runner_skips_when_no_inventory(tmp_path):
    cfg = """
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg)
    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "SKIP"
    assert "no deliverable_inventory" in payload["reason"].lower()


def test_runner_fails_on_mixed_key_inventory(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "key" in payload["details"][0].lower()
    assert "all-or-nothing" in payload["details"][0].lower()


def test_runner_fails_on_multi_entry_no_key(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "namespace" in payload["details"][0].lower() or "key" in payload["details"][0].lower()


def test_runner_fails_on_duplicate_keys(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: same
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: same
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "duplicate" in payload["details"][0].lower()


def test_runner_fails_on_missing_parser_version(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "parser_version" in payload["details"][0].lower()


def test_runner_forward_passes_when_all_paths_exist(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/a.py            |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["forward"]["status"] == "PASS"


def test_runner_forward_warns_on_missing_path_non_strict(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/missing.py      |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return ["foo"]\n'
    })
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0  # WARN does not fail in non-strict mode
    assert payload["forward"]["status"] == "WARN"
    assert any("src/missing.py" in d for d in payload["forward"]["details"])


def test_runner_forward_fails_on_missing_path_strict(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: true
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/missing.py      |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return ["foo"]\n'
    })
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["forward"]["status"] == "FAIL"
