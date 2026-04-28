# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for hooks/provenance_io.py — provenance markdown parsing + parser loading."""
import pytest


SIMPLE_PROVENANCE = """\
# DELIVERABLE_PROVENANCE.md

Some intro prose.

## Deliverable → Code Provenance

| ID         | Deliverable element              | Producing script(s)                               |
| ---------- | -------------------------------- | ------------------------------------------------- |
| p5-chi     | P5 chi-square test               | src/propositions/p5_oliver.py:_chi_square         |
| fig2       | Figure 2 — sector × ban CIs      | src/descriptives/figures.py:fig2_sector_by_ban    |
| p1-ame     | P1 AME (sector × ban) = 0.1802   | src/propositions/p1_coercive.py:run, src/propositions/utils.py:compute_ames |
"""


def test_parse_provenance_extracts_ids_in_order():
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    assert [r.id for r in rows] == ["p5-chi", "fig2", "p1-ame"]


def test_parse_provenance_extracts_script_paths():
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    p1 = next(r for r in rows if r.id == "p1-ame")
    assert "src/propositions/p1_coercive.py" in p1.script_paths
    assert "src/propositions/utils.py" in p1.script_paths


def test_parse_provenance_skips_header_separator_row():
    """The | --- | --- | row must not become a Row object."""
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    assert all(r.id not in ("---", "----------") for r in rows)
    assert len(rows) == 3


def test_parse_provenance_returns_empty_when_no_table():
    from hooks.provenance_io import parse_provenance
    text = "# Title\n\nNo table here.\n"
    assert parse_provenance(text) == []


def test_parse_provenance_detects_duplicate_ids():
    from hooks.provenance_io import parse_provenance, DuplicateIDError
    text = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | A                   | src/a.py            |
| foo | B                   | src/b.py            |
"""
    with pytest.raises(DuplicateIDError) as exc:
        parse_provenance(text)
    assert "foo" in str(exc.value)


def test_parse_provenance_flags_empty_id():
    from hooks.provenance_io import parse_provenance, MalformedRowError
    text = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
|     | element with empty ID | src/a.py |
"""
    with pytest.raises(MalformedRowError):
        parse_provenance(text)


def test_load_parser_finds_canonical(tmp_path, monkeypatch):
    """Canonical parser loads when VERSION lacks 'local-' prefix."""
    pkg = tmp_path / "parsers"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "1.0.0"\n'
        'def parse(s: str) -> list[str]: return ["x"]\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser
    mod = load_parser("demo")
    assert mod.VERSION == "1.0.0"
    assert mod.parse("anything") == ["x"]


def test_load_parser_rejects_canonical_with_local_prefix(tmp_path, monkeypatch):
    pkg = tmp_path / "parsers"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "local-1.0.0"\n'
        'def parse(s: str) -> list[str]: return []\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("demo")
    assert "must not use a `local-`" in str(exc.value)


def test_load_parser_local_must_have_prefix(tmp_path, monkeypatch):
    pkg = tmp_path / "parsers" / "local"
    pkg.mkdir(parents=True)
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "1.0.0"\n'  # missing local- prefix
        'def parse(s: str) -> list[str]: return []\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("demo")
    assert "must use a `local-`" in str(exc.value)


def test_load_parser_local_shadows_canonical(tmp_path, monkeypatch):
    """parsers/local/<n>.py takes precedence on collision."""
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'VERSION = "1.0.0"\n'
        'def parse(s): return ["canonical"]\n'
    )
    (tmp_path / "parsers" / "local").mkdir()
    (tmp_path / "parsers" / "local" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "local" / "demo.py").write_text(
        'VERSION = "local-1.0.0"\n'
        'def parse(s): return ["local"]\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser
    mod = load_parser("demo")
    assert mod.parse("") == ["local"]


def test_load_parser_missing_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("nope")
    assert "unknown parser" in str(exc.value).lower()


def test_load_parser_missing_VERSION_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'def parse(s): return []\n'  # no VERSION
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError):
        load_parser("demo")


def test_load_parser_missing_parse_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'VERSION = "1.0.0"\n'  # no parse
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError):
        load_parser("demo")
