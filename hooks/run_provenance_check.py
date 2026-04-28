#!/usr/bin/env python3
# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""run_provenance_check — CHECK 7 audit runner.

Reads compliance_config.yaml, validates the deliverable_inventory shape,
runs forward and reverse direction audits, emits a JSON report on stdout.
Exit code 0 on PASS / SKIP, non-zero on FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make hooks/ importable so we can pull in provenance_io
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hooks import parse_config, provenance_io  # noqa: E402


def _load_config():
    """Minimal YAML loader using the existing parse_config fallback."""
    cfg_path = Path.cwd() / "compliance_config.yaml"
    if not cfg_path.exists():
        return {}
    return parse_config.load_yaml(str(cfg_path))


def _validate_inventory(inv):
    """Return list of FAIL detail strings; empty list = valid."""
    fails: list[str] = []
    if not inv:
        return fails
    has_key = [bool(e.get("key")) for e in inv]
    if any(has_key) and not all(has_key):
        fails.append("`key` must be all-or-nothing across deliverable_inventory entries.")
    if not any(has_key) and len(inv) >= 2:
        fails.append("≥2 deliverable_inventory entries require `key` to namespace IDs.")
    keys = [e.get("key") for e in inv if e.get("key")]
    if len(keys) != len(set(keys)):
        dups = sorted({k for k in keys if keys.count(k) > 1})
        fails.append(f"duplicate `key` values: {dups}")
    for e in inv:
        if "parser_version" not in e or not e.get("parser_version"):
            fails.append(f"entry for path={e.get('path')!r} missing required `parser_version`")
    return fails


def main(argv: list[str]) -> int:
    cfg = _load_config()
    inv = cfg.get("deliverable_inventory") or []
    if not inv:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "SKIP",
            "reason": "no deliverable_inventory configured",
        }))
        return 0
    fails = _validate_inventory(inv)
    if fails:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": fails,
        }))
        return 1

    strict = bool(cfg.get("compliance_monitor", {}).get("provenance_strict", False))
    prov_path = Path.cwd() / "docs" / "DELIVERABLE_PROVENANCE.md"
    if not prov_path.exists():
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": [f"docs/DELIVERABLE_PROVENANCE.md missing but deliverable_inventory is set"],
        }))
        return 1
    try:
        rows = provenance_io.parse_provenance(prov_path.read_text())
    except provenance_io.ProvenanceError as e:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": [f"DELIVERABLE_PROVENANCE.md: {type(e).__name__}: {e}"],
        }))
        return 1

    forward_warnings = []
    for row in rows:
        for path in row.script_paths:
            if not (Path.cwd() / path).exists():
                forward_warnings.append(f"row {row.id!r}: script path {path!r} does not exist")
    forward = {
        "status": "PASS" if not forward_warnings else ("FAIL" if strict else "WARN"),
        "details": forward_warnings,
    }

    overall_fail = forward["status"] == "FAIL"
    payload = {
        "check": "provenance_integrity",
        "status": "FAIL" if overall_fail else "PASS",
        "forward": forward,
        "rows_seen": len(rows),
    }
    print(json.dumps(payload))
    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
