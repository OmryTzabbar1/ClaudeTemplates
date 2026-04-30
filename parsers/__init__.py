# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Parser interface contract for the deliverable provenance audit (CHECK 7).

Each parser module under `parsers/` (or `parsers/local/`) MUST export:

    VERSION: str
        Semver string. Local parsers MUST use a `local-` prefix
        (e.g. `local-1.0.0`); canonical parsers MUST NOT.

    def parse(file_contents: str) -> list[str]:
        Return the list of stable ElementIDs found in the file.
        IDs are flat (no namespace prefix) — the audit applies the
        `<key>:` prefix in namespaced mode.

The contract is intentionally one signature, one return type. Parsers
that need richer output are the wrong abstraction; split into
multiple parsers or extend the audit, do not extend this interface.
"""
