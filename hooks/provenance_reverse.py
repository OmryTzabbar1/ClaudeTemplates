# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""provenance_reverse — reverse-direction audit logic for CHECK 7.

Loads parsers, runs parse(), compares detected IDs to provenance rows.
Flat mode only; Task 11 will add namespaced mode.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from hooks import provenance_io

_FAIL_SUBSTRINGS = ("load failed", "raised", "non-list-of-str", "colon", "does not exist")


def _process_entry(entry):
    """Load parser for one inventory entry; return (detail_or_None, ids_set)."""
    name = entry["parser"]
    path = entry["path"]
    expected_ver = entry.get("parser_version", "")
    try:
        mod = provenance_io.load_parser(name)
    except provenance_io.ParserLoadError as exc:
        return f"parser {name!r}: load failed: {exc}", set()
    details = []
    if mod.VERSION != expected_ver:
        details.append(
            f"parser {name!r}: version mismatch: {mod.VERSION!r} != {expected_ver!r} (WARN only)"
        )
    fpath = Path.cwd() / path
    if not fpath.exists():
        details.append(f"entry path {path!r} does not exist")
        return "\n".join(details) if details else None, set()
    contents = fpath.read_text()
    try:
        ids = mod.parse(contents)
    except Exception:
        details.append(f"parser {name!r} raised on {path!r}: {traceback.format_exc()}")
        return "\n".join(details) if details else None, set()
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        details.append(f"parser {name!r} returned non-list-of-str for {path!r}")
        return "\n".join(details) if details else None, set()
    bad = [i for i in ids if ":" in i]
    if bad:
        details.append(f"parser {name!r} returned IDs containing colon: {bad}")
        return "\n".join(details) if details else None, set()
    return "\n".join(details) if details else None, set(ids)


def reverse_direction(inv, rows, strict):
    """Compare parser-detected IDs to provenance rows; return audit dict."""
    details: list[str] = []
    all_detected: set[str] = set()
    for entry in inv:
        detail, ids = _process_entry(entry)
        if detail:
            details.extend(detail.splitlines())
        all_detected.update(ids)
    provenance_ids = {row.id for row in rows}
    forward_misses = sorted(all_detected - provenance_ids)
    reverse_misses = sorted(provenance_ids - all_detected)
    is_hard_fail = any(
        any(sub in d for sub in _FAIL_SUBSTRINGS) for d in details
        if not d.endswith("(WARN only)")
    )
    if is_hard_fail:
        status = "FAIL"
    elif forward_misses or reverse_misses:
        status = "FAIL" if strict else "WARN"
    else:
        status = "PASS"
    return {
        "status": status,
        "details": details,
        "forward_misses": forward_misses,
        "reverse_misses": reverse_misses,
        "count_detected": len(all_detected),
        "count_provenance": len(provenance_ids),
    }
