# Claude Project Documentation Templates

Version: 2.1.0

Templates for structuring a project so Claude Code (and its subagents) can work effectively across multiple sessions — with layered enforcement via git hooks, Claude Code hooks, and a compliance monitor agent.

## Quick Start

1. Copy this repository or run `setup.sh` from your project root
2. Fill in `CLAUDE.md` placeholders (project name, description)
3. Fill in `CONTEXT.md` placeholders (architecture, terminology, data flow)
4. Add module entries to `compliance_config.yaml` → `read_gate.module_map`
5. Start your first Claude Code session

## Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Tiered project rules: non-negotiable (Tier 1), workflow (Tier 2), reference (Tier 3) |
| `CONTEXT.md` | Living project snapshot: state, architecture, terminology, file map, contracts, versioning rules |
| `CONTEXT_MODULE.md` | Template for per-module context files (includes version decision table) |
| `compliance_config.yaml` | Machine-readable policy: thresholds, patterns, module map, check definitions |
| `agents/compliance_monitor.md` | Read-only auditor agent definition (6 checks) |
| `hooks/pre-commit` | Git pre-commit: line count, header, hardcoded values, tests |
| `hooks/parse_config.py` | YAML parser fallback when yq is unavailable |
| `hooks/claude_read_gate.py` | Claude Code hook: blocks edits until CONTEXT file is confirmed read |
| `hooks/claude_advisory_scan.py` | Claude Code hook: warns on advisory-level hardcoded patterns |
| `setup.sh` | Project setup with safe hook installation |

## Enforcement Layers

| Layer | What it catches | When it runs |
|-------|----------------|-------------|
| **Git pre-commit** | Line count > 150, missing headers, hardcoded URLs/secrets, test failures | On every commit (hard gate) |
| **Claude Code hooks** | Unread CONTEXT files, advisory hardcoded patterns, approaching line limits | Mid-session (gate or warning) |
| **Compliance monitor** | CONTEXT drift, line count mismatches, stale references, contract inconsistencies | Session end (advisory report) |

## Parser-based provenance audit (CHECK 7)

The compliance monitor's CHECK 7 (`provenance_integrity`) compares parser-detected element IDs in each project's deliverable against rows in `docs/DELIVERABLE_PROVENANCE.md`. Configuration lives in `compliance_config.yaml` under `deliverable_inventory:` (a list of `{path, parser, parser_version, key?}` entries; `key` is required when ≥2 entries, all-or-nothing).

Parsers ship in `parsers/` (canonical) with project-local extensions in `parsers/local/`. The contract is one signature: `parse(file_contents: str) -> list[str]` plus a `VERSION` string. Local parsers use a `local-`-prefixed VERSION; canonical parsers must not. The audit refuses any parser whose VERSION-prefix doesn't match its location, surfacing silent forks in `compliance_config.yaml` itself.

The runner is `hooks/run_provenance_check.py`; the agent shells out to it and relays the JSON verdict. See `docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md` for the full audit logic, failure modes, and limitations.

`docs/DELIVERABLE_PROVENANCE.md` (downstream-installed by `setup.sh`) is the human-curated half. It replaces a prior `docs/SCRIPT_PURPOSES.md` whose two-section design is documented in `decisions/0001-cut-script-registry.md`.

## Customization

- **Line limit:** Change `pre_commit.max_file_lines` in `compliance_config.yaml`
- **Test commands:** Change `pre_commit.test_commands` list
- **Header format:** Adjust patterns in `pre_commit.file_header.patterns`
- **Source directories:** Change `pre_commit.source_dirs`
- **Advisory patterns:** Add/remove `advisory.hardcoded_values.warn` entries
- **Module mapping:** Add entries to `read_gate.module_map` as modules are created
