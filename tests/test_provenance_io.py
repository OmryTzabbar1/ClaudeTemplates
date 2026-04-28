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
