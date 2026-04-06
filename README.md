# Claude Project Documentation Templates

Version: 2.0.0

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

## Customization

- **Line limit:** Change `pre_commit.max_file_lines` in `compliance_config.yaml`
- **Test commands:** Change `pre_commit.test_commands` list
- **Header format:** Adjust patterns in `pre_commit.file_header.patterns`
- **Source directories:** Change `pre_commit.source_dirs`
- **Advisory patterns:** Add/remove `advisory.hardcoded_values.warn` entries
- **Module mapping:** Add entries to `read_gate.module_map` as modules are created
