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

from hooks import parse_config  # noqa: E402


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
    # forward + reverse direction implemented in Tasks 9-10
    print(json.dumps({
        "check": "provenance_integrity",
        "status": "PASS",
        "reason": "inventory validated; full audit pending Tasks 9-10",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
