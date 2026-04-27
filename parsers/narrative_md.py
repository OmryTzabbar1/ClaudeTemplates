# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""narrative_md — HTML id-comment parser for markdown deliverables.

Detects markers of the form `<!-- id: <stable-id> -->` (case-sensitive
on the `id:` label). Returns a sorted, deduplicated list of IDs.
"""
import re

VERSION = "1.0.0"

_ID_PATTERN = re.compile(r"<!--\s*id:\s*([A-Za-z0-9_-]+)\s*-->")


def parse(file_contents: str) -> list[str]:
    """Return sorted unique list of IDs detected in `file_contents`."""
    return sorted(set(_ID_PATTERN.findall(file_contents)))
