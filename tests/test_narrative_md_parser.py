# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for parsers/narrative_md.py — markdown parser for HTML id comments."""
import pytest


def test_version_is_semver_without_local_prefix():
    """Canonical parsers must NOT have a `local-` VERSION prefix."""
    from parsers import narrative_md
    assert hasattr(narrative_md, "VERSION")
    assert isinstance(narrative_md.VERSION, str)
    assert not narrative_md.VERSION.startswith("local-")


def test_parse_signature():
    """Contract: parse(str) -> list[str]."""
    from parsers import narrative_md
    import inspect
    sig = inspect.signature(narrative_md.parse)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].annotation in (str, "str")


def test_parse_extracts_single_id():
    from parsers.narrative_md import parse
    text = "Some finding **value 42** <!-- id: p5-chi -->"
    assert parse(text) == ["p5-chi"]


def test_parse_extracts_multiple_ids_sorted_unique():
    from parsers.narrative_md import parse
    text = """
**A** <!-- id: zebra -->
**B** <!-- id: alpha -->
**C** <!-- id: alpha -->
**D** <!-- id: middle -->
"""
    assert parse(text) == ["alpha", "middle", "zebra"]


def test_parse_returns_empty_on_no_ids():
    from parsers.narrative_md import parse
    assert parse("Plain markdown with no id markers.") == []


def test_parse_handles_whitespace_variants():
    from parsers.narrative_md import parse
    text = """
<!--id:no-spaces-->
<!--   id:   extra-spaces   -->
<!-- id: kebab-case -->
"""
    assert parse(text) == ["extra-spaces", "kebab-case", "no-spaces"]


def test_parse_ignores_malformed_markers():
    """Markers without `id:` prefix or with invalid chars must not match."""
    from parsers.narrative_md import parse
    text = """
<!-- not an id: foo -->
<!-- id: has space -->
<!-- id: has/slash -->
<!-- id: ok-id -->
"""
    assert parse(text) == ["ok-id"]


def test_parse_handles_uppercase_html_comment_label():
    """Spec uses lowercase `id:`. Uppercase ID: should NOT match (would be a different parser)."""
    from parsers.narrative_md import parse
    text = "<!-- ID: should-not-match -->"
    assert parse(text) == []
