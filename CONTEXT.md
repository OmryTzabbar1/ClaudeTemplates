# CONTEXT.md

Version: 2.6.0

---

## Table of Contents

- [Project Summary](#project-summary)
- [Current Project State](#current-project-state)
- [Recent Changes](#recent-changes)
- [Pending Tasks](#pending-tasks)
- [Terminology](#terminology)
- [Architecture](#architecture)
- [Data Flow](#data-flow)
- [Module Context Files](#module-context-files)
- [Architecture & File Map](#architecture--file-map)
- [Interface Contracts](#interface-contracts)
- [Versioning Rules](#versioning-rules)
- [CONTEXT File Maintenance](#context-file-maintenance)
- [Key Project Decisions](#key-project-decisions)

---

## Project Summary

<!-- 2-3 sentences. What the project does, key tech, scale. -->

[PROJECT_NAME] [what it does]. Built with [key technologies]. [Scale/scope note].

---

## Current Project State

**Phase: planning**

<!-- Update this as phases complete. -->

### Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Design | Architecture, specs, pipeline design | Not started |
| Scaffolding | Directories, config, tests, CONTEXT files | Not started |
| [Phase 3] | [Description] | Not started |
| [Phase 4] | [Description] | Not started |

---

## Recent Changes

<!-- Most recent first. Keep 10-20 entries. Oldest roll off. Include file names and test counts. -->

- **2026-04-17:** Added `templates/CONTEXT_MODULE_EXAMPLE.md` — populated example of a per-module CONTEXT file (fictional Config module, ~120 lines) showing what real Recent Changes, File Map line counts, Key Decisions, and a checked-off Module Change Checklist look like. Added a header pointer in `CONTEXT_MODULE.md` (v1.2.0→v1.3.0) directing users to the example. Bumped CONTEXT.md to v2.6.0.
- **2026-04-17:** Backported `.gitignore` from TowerDefense — added `.gitignore` at CT root (Python + Claude session files + IDE + OS) and a generic `templates/gitignore` (same content plus a commented Unity section for downstream Unity projects). Updated `setup.sh` (246→255 lines): if the downstream project has no `.gitignore`, seed it from `templates/gitignore`; the existing per-entry append for Claude session files now acts as an idempotent backstop. Bumped CONTEXT.md to v2.5.0.
- **2026-04-17:** Accuracy sweep — `setup.sh` (213→246 lines): (1) added `claude_token_monitor.py` to the hook copy loop — was missing despite being part of the live hook set, (2) replaced `HOOKS_CONFIG` with the actual nested `{matcher, hooks: [{type, command}]}` JSON shape used by `.claude/settings.json` and added the token-monitor PostToolUse entry, (3) added a `copy_if_missing` step that places `templates/PROJECT_README.md` as the new project's `README.md`, (4) renumbered Next Steps to put README customization first. CONTEXT.md file map: synced hooks/ section — added `claude_subagent_gate.py` and `claude_token_monitor.py`, corrected pre-commit/parse_config/read_gate/advisory_scan line counts to match `wc -l`. Bumped CONTEXT.md to v2.4.0.
- **2026-04-17:** Added `templates/PROJECT_README.md` — front-door README template for downstream projects scaffolded from this repo (separate from the meta-template's own README). Mirrors the structure used in TowerDefense's README: pitch, status table, tech stack, repo layout, conventions, getting-started, versioning. Includes a header comment explaining its purpose and the README update triggers. Bumped CONTEXT.md to v2.3.0.
- **2026-04-17:** Backported `CONTEXT_FILEMAP.md` extraction pattern from TowerDefense — added pointer line above the Architecture & File Map and a new "CONTEXT_FILEMAP.md Extraction" subsection with the trigger threshold (~200 lines), step-by-step extraction recipe, and "when NOT to extract" guidance. Bumped CONTEXT.md to v2.2.0.
- **2026-04-17:** Backported README.md update reminders from TowerDefense — added bullet to CLAUDE.md Tier 3 Pre-Completion Compliance Checklist, new "README.md Maintenance" subsection in CONTEXT.md, README checklist item in CONTEXT_MODULE.md template. Bumped CLAUDE.md to v2.2.0, CONTEXT.md to v2.1.0, CONTEXT_MODULE.md to v1.2.0.
- **2026-04-05:** Created `setup.sh` — safe project bootstrapping script; copies templates, installs hooks, configures .claude/settings.json and .gitignore (213 lines)
- **2026-04-05:** Created `hooks/claude_advisory_scan.py` — Claude Code PostToolUse advisory scanner (149 lines)
- **2026-04-05:** Created `hooks/claude_read_gate.py` — Claude Code PreToolUse read gate (127 lines)
- **2026-04-05:** Created `hooks/parse_config.py` — YAML dotted-key resolver for shell hook fallback (60 lines); `tests/test_parse_config.py` — 10 tests (88 lines)
- **2026-04-05:** Created `ContextModuleDocumentation/CONTEXT_hooks.md` — hooks module context file
- **2026-04-05:** Created compliance_config.yaml — machine-readable policy for git hooks and Claude Code hooks (114 lines)
- **YYYY-MM-DD:** Created project scaffolding — CLAUDE.md, CONTEXT.md, CONTEXT_MODULE.md, directory structure

---

## Pending Tasks

<!-- High-level project tasks. Module-level tasks go in CONTEXT_*.md files. -->

- [ ] Complete design spec
- [ ] Create implementation plan
- [ ] [Task 3]

---

## Terminology

<!-- Define project-specific terms that Claude or subagents need to understand. -->

- **Term 1** — Definition
- **Term 2** — Definition
- **Term 3** — Definition

---

## Architecture

<!-- Describe your system's layers. Adjust the number of layers to your project. -->

- **Layer 1 — [Name]:** [What it does]
- **Layer 2 — [Name]:** [What it does]
- **Layer 3 — [Name]:** [What it does]

**Rules:**
- [Rule about what belongs in which layer]
- [Rule about data flow between layers]

---

## Data Flow

<!-- Show the end-to-end data pipeline. Use ASCII art or a simple diagram. -->

```
Input → Processing → Output
```

---

## Module Context Files

<!-- Canonical table. CLAUDE.md points here — do not duplicate this table elsewhere. -->

| File | Module | Status |
|------|--------|--------|
| `CONTEXT_hooks.md` | Hooks | stable |
| `CONTEXT_[module1].md` | [Module 1] | planning |
| `CONTEXT_[module2].md` | [Module 2] | planning |

### When to read which file

- Working on hooks → read `ContextModuleDocumentation/CONTEXT_hooks.md`
- Working on [module 1] → read `ContextModuleDocumentation/CONTEXT_[module1].md`
- Working on [module 2] → read `ContextModuleDocumentation/CONTEXT_[module2].md`

---

## Architecture & File Map

<!-- Every file in the project with line counts. Update after every change. -->

> **When this file map gets large** (~200+ lines, or when subagents start reading CONTEXT.md just to find a file), extract it to a sibling `CONTEXT_FILEMAP.md` and replace this section with a one-line pointer plus an aggregate summary. See § CONTEXT_FILEMAP.md Extraction below for the convention. CONTEXT.md should stay readable in a single screen for subagents.

```
project/
├── CLAUDE.md                           # project rules (tiered)
├── CONTEXT.md                          # this file — living project snapshot
├── CONTEXT_MODULE.md                   # template for new context files
├── compliance_config.yaml (114 lines)  # machine-readable policy for hooks
├── setup.sh              (255 lines)    # project setup with safe hook install
├── .gitignore                          # CT's own ignore rules (Python, IDE, OS, Claude session files)
├── templates/
│   ├── PROJECT_README.md               # front-door README template for downstream projects
│   ├── gitignore                        # generic .gitignore template (downstream projects; setup.sh seeds it)
│   └── CONTEXT_MODULE_EXAMPLE.md        # populated worked example of a per-module CONTEXT file
├── ContextModuleDocumentation/
│   ├── CONTEXT_hooks.md               # hooks module state
│   ├── CONTEXT_[module1].md           # [module 1] state
│   └── CONTEXT_[module2].md           # [module 2] state
├── agents/
│   └── compliance_monitor.md          # compliance auditor agent definition
├── hooks/
│   ├── pre-commit                  (285 lines)  # git pre-commit hard gate
│   ├── parse_config.py             (72 lines)   # YAML parser fallback for shell hooks
│   ├── claude_read_gate.py         (143 lines)  # Claude Code PreToolUse read gate
│   ├── claude_subagent_gate.py     (121 lines)  # Claude Code PreToolUse subagent compliance gate
│   ├── claude_advisory_scan.py     (148 lines)  # Claude Code PostToolUse advisory scanner
│   └── claude_token_monitor.py     (114 lines)  # Claude Code PostToolUse token-size monitor for critical .md files
├── plans/
│   └── YYYY-MM-DD-[plan-name].md      # implementation plan
├── docs/superpowers/specs/
│   └── YYYY-MM-DD-[spec-name].md      # design spec
├── src/
│   ├── config/
│   │   └── config.yaml    (XX lines)  — All paths & settings
│   ├── [module1]/
│   │   └── [file].py      (XX lines)  — [Description]
│   └── [module2]/
│       └── [file].py      (XX lines)  — [Description]
├── scripts/
│   └── [script].py        (XX lines)  — [Description]
└── tests/
    ├── conftest.py           (XX lines)   — Shared test fixtures
    ├── test_parse_config.py  (88 lines)   — 10 tests for hooks/parse_config.py
    ├── test_[module1].py     (XX lines)   — X tests for [module 1]
    └── test_[module2].py     (XX lines)   — X tests for [module 2]
```

---

## Interface Contracts

<!-- Every file produced by one module and consumed by another. Single source of truth for filenames and formats. -->

| Producer | Output Location | Filename Pattern | Consumed By |
|----------|----------------|------------------|-------------|
| `[producer].py` | `[output/dir/]` | `[filename].csv` | `[consumer].py` |
| `[producer].py` | `[output/dir/]` | `[filename].json` | end user |

**Rules:**
- If you change a filename pattern, update this table AND every consumer listed in the "Consumed By" column.
- If you build a new consumer, verify the suffix you use against this table before writing code.

---

## Versioning Rules

### Semantic Versions

Every `.md` doc (README, plans, CONTEXT files) must have a `Version: X.X.X` line near the top.

### When to Bump

Version bump rules for CONTEXT files are defined in each `CONTEXT_*.md`'s Version Decision Table. The default table (from the template) is:

| Change type | Version bump |
|---|---|
| Line count correction only | patch |
| New file added to module | minor |
| File removed or renamed | minor |
| Module behavior/API changed | minor |
| Module removed or replaced | major |

Projects may override this table by adding a `## Version Decision Table Override` section below. If present, that override applies to all modules in this project.

### Plan Versioning

- Each module has its own plan in `plans/`
- When code changes, update the corresponding plan: increment the version, update content, update any affected sections
- Exact function signatures in plans — copy-paste from source, never paraphrase
- Every source file whose header references a plan must appear in that plan's File Mapping table

---

## CONTEXT File Maintenance

Each `ContextModuleDocumentation/CONTEXT_*.md` is the **living snapshot** of its module. It is what a subagent or new session reads *first* to understand a module's current state.

### Required Sections

1. **Module Summary** — What the module does and its core purpose
2. **Current State** — Phase: `planning` / `in-progress` / `stable` / `deprecated`
3. **Recent Changes** — Bulleted log of the last 5-10 meaningful changes with dates. Oldest roll off.
4. **Pending Tasks** — Priority order. Remove completed items next session.
5. **Architecture & File Map** — Directory tree with line counts and one-line description per file
6. **Key Decisions & Notes** — Design decisions, open questions, constraints
7. **Version Decision Table** — Patch/minor/major rules (from template)
8. **Module Change Checklist** — Run after every change (from template)

### When to Update

- After any code, config, or doc change in that module
- After adding or removing files
- At the end of every session, even if only to update "Current State"

### Rules

- Bullet points and tables over prose — keep it scannable
- Version it like every other doc
- CONTEXT files are for **module state**; development rules live in CLAUDE.md

---

## CONTEXT_FILEMAP.md Extraction

When `CONTEXT.md`'s Architecture & File Map grows past ~200 lines (it crowds out other sections and burns subagent tokens on lookup), extract the full file tree to a sibling `CONTEXT_FILEMAP.md` at the repo root. Subagents that need an overview keep reading CONTEXT.md; subagents that need an exact line count or a specific file path read CONTEXT_FILEMAP.md.

### How to extract

1. Move the entire `\`\`\`...\`\`\`` directory tree out of CONTEXT.md and into a new top-level `CONTEXT_FILEMAP.md` (with its own `Version: 1.0.0` header).
2. Replace the file map in CONTEXT.md with:
   - One-line pointer: `> **Full file tree with line counts extracted to \`CONTEXT_FILEMAP.md\`** to keep this file under token limits for subagent reads. When adding/removing/modifying files, update CONTEXT_FILEMAP.md.`
   - An aggregate count line: `**Source file counts:** Module A (N), Module B (N), … = **N source files**` and the same for tests.
3. From this point on, file additions/removals update `CONTEXT_FILEMAP.md` (not CONTEXT.md) — except the aggregate count, which still lives here.
4. Bump CONTEXT.md's version (minor — structural change) and bump CONTEXT_FILEMAP.md per its own Version Decision Table on every subsequent edit.

### When NOT to extract

- The file map fits comfortably above the Interface Contracts table.
- The project has fewer than ~30 source files.
- Premature extraction adds an indirection without saving tokens.

---

## README.md Maintenance

`README.md` is the project front door for newcomers and external readers. It is NOT a per-change log — most module work does not touch it. Update it (and bump its version) when any of the following changes:

- **Project phase or status** (e.g., a phase moves from "Not started" to "In progress" or "Complete")
- **Tech stack** (language version bump, new core dependency, framework swap)
- **Repo layout** (new top-level directory, module added/removed/renamed)
- **Getting-started steps** (anything a fresh clone needs to do differently)
- **The module list** in CONTEXT.md grows or shrinks (the README's repo-layout module list should match)

Routine intra-module work — adding a feature, fixing a bug, refactoring a file — does NOT require a README touch. CONTEXT.md and the relevant `CONTEXT_*.md` are sufficient.

---

## Key Project Decisions

<!-- Decisions that affect the whole project, not just one module. Module-specific decisions go in CONTEXT_*.md files. -->

- **[Decision]** — [What was decided and why]
- **[Decision]** — [What was decided and why]
