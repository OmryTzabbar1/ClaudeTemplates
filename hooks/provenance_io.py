# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""provenance_io — parse DELIVERABLE_PROVENANCE.md tables and load parser modules.

Two responsibilities: (1) extract structured rows from the provenance
markdown table, (2) load and validate parser modules from `parsers/`
and `parsers/local/`. Failure modes are spec'd in the design doc;
this module raises typed exceptions the runner converts to JSON.
"""
from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path


class ProvenanceError(Exception):
    """Base for provenance-parsing errors."""


class DuplicateIDError(ProvenanceError):
    """Raised when DELIVERABLE_PROVENANCE.md contains duplicate IDs."""


class MalformedRowError(ProvenanceError):
    """Raised when a row is missing its ID column or has empty ID."""


class ParserLoadError(ProvenanceError):
    """Raised on parser module load / interface contract violation."""


@dataclass(frozen=True)
class Row:
    id: str
    element: str
    script_paths: tuple[str, ...]


_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")
_SEPARATOR_CELL = re.compile(r"^[-:\s]+$")


def parse_provenance(text: str) -> list[Row]:
    """Extract rows from any pipe-table found in `text`.

    Header row is detected by `ID` in the first cell (case-insensitive).
    The separator row (e.g. `| --- | --- |`) is skipped.
    """
    rows: list[Row] = []
    in_table = False
    seen_ids: set[str] = set()

    for line in text.splitlines():
        m = _TABLE_ROW.match(line)
        if not m:
            in_table = False
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if all(_SEPARATOR_CELL.match(c) for c in cells):
            continue
        if not in_table:
            if cells and cells[0].strip().lower() == "id":
                in_table = True
            continue
        if len(cells) < 3:
            raise MalformedRowError(f"Row has fewer than 3 cells: {line!r}")
        rid, element, scripts_cell = cells[0], cells[1], cells[2]
        if not rid:
            raise MalformedRowError(f"Empty ID in row with element: {element!r}")
        if rid in seen_ids:
            raise DuplicateIDError(f"Duplicate ID: {rid!r}")
        seen_ids.add(rid)
        paths = tuple(p.strip().split(":")[0] for p in scripts_cell.split(",") if p.strip())
        rows.append(Row(id=rid, element=element, script_paths=paths))
    return rows
