# Parser Changelog

Version: 1.0.0

Per-parser version history. One section per parser, ordered by parser name. Entries within a section ordered newest-first.

When updating a parser's `VERSION`, add an entry here in the same commit. The bump rule (MAJOR / MINOR / PATCH) is in the spec — see `docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md` § Parser versioning protocol.

## narrative_md

### 1.0.0 — 2026-04-27

Initial. Detects `<!-- id: <stable-id> -->` markers in markdown via regex `<!--\s*id:\s*([A-Za-z0-9_-]+)\s*-->`. Returns sorted unique list of IDs.
