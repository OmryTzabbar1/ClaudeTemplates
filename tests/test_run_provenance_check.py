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


def test_runner_fails_when_provenance_empty_but_inventory_set(tmp_path):
    """Spec § Failure modes: empty Provenance file + configured inventory → FAIL."""
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    # Empty provenance file (header text only, no rows)
    prov = "# DELIVERABLE_PROVENANCE.md\n\nNo table here yet.\n"
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    (tmp_path / "docs" / "d.md").write_text("")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert any("no rows" in d.lower() for d in payload["details"])


def test_runner_reverse_passes_when_ids_align(tmp_path):
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
| bar | B                   | src/a.py            |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n<!-- id: bar -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["reverse"]["status"] == "PASS"
    assert payload["reverse"]["count_detected"] == 2
    assert payload["reverse"]["count_provenance"] == 2


def test_runner_reverse_warns_on_forward_miss(tmp_path):
    """Detected ID with no Provenance row → WARN (FAIL in strict)."""
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
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n<!-- id: orphan -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["reverse"]["status"] == "WARN"
    assert "orphan" in str(payload["reverse"]["forward_misses"])


def test_runner_reverse_warns_on_reverse_miss(tmp_path):
    """Provenance row with no detected ID → WARN."""
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID    | Deliverable element | Producing script(s) |
| ----- | ------------------- | ------------------- |
| foo   | F                   | src/a.py            |
| stale | S                   | src/a.py            |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["reverse"]["status"] == "WARN"
    assert "stale" in str(payload["reverse"]["reverse_misses"])


def test_runner_fails_when_parser_returns_colon(tmp_path):
    """Spec § Failure modes: parser returning ':' in an ID → FAIL."""
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
    # Parser stub deliberately returns a colon-containing ID
    bad_parser = 'VERSION = "1.0.0"\ndef parse(s): return ["bad:thing"]\n'
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": bad_parser,
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("colon" in d.lower() or ":" in d for d in payload["reverse"]["details"])


def test_runner_namespaced_passes_when_keys_align(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
  - path: docs/dash.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: dash
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID            | Deliverable element | Producing script(s) |
| ------------- | ------------------- | ------------------- |
| paper:foo     | F in paper          | src/a.py            |
| dash:foo      | F in dash           | src/a.py            |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("<!-- id: foo -->\n")
    (tmp_path / "docs" / "dash.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["reverse"]["count_detected"] == 2
    assert payload["reverse"]["count_provenance"] == 2


def test_runner_namespaced_fails_on_flat_provenance_id(tmp_path):
    """Provenance row with flat ID in namespaced mode → FAIL."""
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | flat ID in namespaced mode | src/a.py     |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("flat" in d.lower() or "namespaced" in d.lower() for d in payload["reverse"]["details"])


def test_runner_namespaced_fails_on_unknown_key_prefix(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID            | Deliverable element        | Producing script(s) |
| ------------- | -------------------------- | ------------------- |
| ghost:foo     | row with unknown key prefix | src/a.py           |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("ghost" in d for d in payload["reverse"]["details"])


def test_runner_self_check_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc, payload, stderr = _run(tmp_path, "--self-check")
    assert rc == 0, f"self-check failed: {payload} / {stderr}"
    assert payload["status"] == "PASS"
    assert payload.get("mode") == "self-check"
