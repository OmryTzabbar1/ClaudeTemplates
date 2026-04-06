# Template Enforcement Overhaul — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the ClaudeTemplates system from self-reported compliance to a layered enforcement architecture with git hooks, Claude Code hooks, and a compliance monitor agent.

**Architecture:** Three enforcement layers — git pre-commit hooks as hard gates for mechanical checks, Claude Code hooks for workflow-aware mid-session feedback, and a compliance monitor agent for semantic auditing at session end. All hook behavior is driven by a central `compliance_config.yaml` policy file.

**Tech Stack:** Shell (POSIX), Python 3, YAML, Claude Code hooks API, git hooks

**Design spec:** `docs/superpowers/specs/2026-04-05-template-enforcement-overhaul-design.md`

---

## Session Scope Assessment

- Modules touched: templates (CLAUDE.md, CONTEXT.md, CONTEXT_MODULE.md), hooks, agents, setup
- Files created/modified: 10 (3 modified, 7 new)
- Reversible if incomplete: yes — each task produces independently valid files; incomplete work doesn't break existing templates
- Estimated completion confidence: high
- Split recommended: no
- Justification: All files are documentation/scripts with no runtime dependencies between them; each task is self-contained.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `CLAUDE.md` | Rewrite | Tiered project rules (Tier 1/2/3), pointer to CONTEXT.md for reference |
| `CONTEXT.md` | Rewrite | Expanded living snapshot: TOC, architecture, terminology, versioning rules, CONTEXT maintenance |
| `CONTEXT_MODULE.md` | Modify | Add version decision table, annotate checklist with enforcement mechanisms |
| `compliance_config.yaml` | Create | Machine-readable policy: thresholds, patterns, module map, check definitions |
| `hooks/parse_config.py` | Create | Python YAML→KEY=VALUE parser for shell hooks |
| `hooks/pre-commit` | Create | Git pre-commit: line count, header, hardcoded values, tests |
| `hooks/claude_read_gate.py` | Create | Claude Code PreToolUse: read confirmation gate |
| `hooks/claude_advisory_scan.py` | Create | Claude Code PostToolUse: advisory hardcoded value scanner |
| `agents/compliance_monitor.md` | Create | Compliance auditor agent definition |
| `setup.sh` | Create | Safe project setup with hook installation |

---

## Task 1: Rewrite CLAUDE.md with Tiered Structure

**Files:**
- Modify: `CLAUDE.md`

This is a full rewrite. The new file has three tiers, moves reference material out, and keeps a pointer to CONTEXT.md for the Module Context Files table.

- [ ] **Step 1: Read the current CLAUDE.md**

Read the full file to understand all content that needs to be reorganized or moved.

- [ ] **Step 2: Write the new CLAUDE.md**

Replace the entire file with the tiered structure. The content below is the complete file:

```markdown
# CLAUDE.md

**IMPORTANT: Read this entire file before making ANY code changes.**

Version: 2.0.0

---

## ⛔ TIER 1 — NON-NEGOTIABLE RULES

These rules are hard constraints. Violations are caught by hooks and block commits.

1. **TDD** — Write the test first. Then write the minimum code to make it pass. No untested code ships. No exceptions.

2. **150-line file limit** — All source files must stay under 150 lines. If a file exceeds this, refactor or split it before committing. *Enforced by pre-commit hook.*

3. **No hardcoded values** — Never hardcode secrets, credentials, file paths, URLs, API endpoints, model names, numeric thresholds, timeouts, or converter names in source code. Every such value must come from a config file, an environment variable, or a function parameter with a documented default. *Enforced by pre-commit hook.*

4. **File headers** — Every source file must open with an Area/PRD/NOTE header in the language's comment syntax. *Enforced by pre-commit hook.*

   | Language | Syntax |
   |----------|--------|
   | Python, Shell, Ruby, YAML | `# Area: ...` / `# PRD: ...` / `# NOTE: ...` |
   | JS, TS, Go, Rust, Java, C | `// Area: ...` / `// PRD: ...` / `// NOTE: ...` |
   | CSS | `/* Area: ... */` / `/* PRD: ... */` / `/* NOTE: ... */` |
   | HTML | `<!-- Area: ... -->` / `<!-- PRD: ... -->` / `<!-- NOTE: ... -->` |

   Header content:
   - **Area:** `<Module Name>`
   - **PRD:** `plans/<plan-filename>.md`
   - **NOTE:** `After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.`

---

## 📋 TIER 2 — BEFORE STARTING WORK

### Subagent Rules

Every subagent working on this project MUST, in this order:

1. Read this entire CLAUDE.md
2. Read `CONTEXT.md` — includes architecture, terminology, data flow, interface contracts, and the Module Context Files table
3. Read the `ContextModuleDocumentation/CONTEXT_*.md` for the module being worked on
4. Cross-reference dependencies against the Interface Contracts table in CONTEXT.md
5. Output structured read confirmation to the conversation immediately after reading each CONTEXT file, before any Edit or Write tool calls on files in that module:
   `CONTEXT READ: <file> | state: <phase> | last change: <date+desc> | open tasks: <N>`
6. If creating a new module, create its `CONTEXT_*.md` first using the template at `CONTEXT_MODULE.md`
7. Run the Pre-Completion Compliance Checklist (Tier 3) before reporting done
8. Do not report work as complete until all checklist items pass

### Behavioral Expectations

- **Modularity** — Single responsibility per module. If it needs a long explanation, it does too much.
- **Check existing code first** — Search the codebase before implementing. Never duplicate logic.
- **Reuse before writing** — Wire into existing functions and modules. New code is a last resort.
- **Register every new file** — When creating a new source file (including splits/extractions), immediately: add the file header, add it to the module's CONTEXT_*.md and CONTEXT.md file maps with line count, and add it to the Interface Contracts table if it produces or consumes files.

### Session Scope Assessment

Every implementation plan must open with:

- Modules touched: [list]
- Files created/modified: [N]
- Reversible if incomplete: [yes/no — why]
- Estimated completion confidence: [high/medium/low]
- Split recommended: [yes/no]
- Justification: [one sentence]

### Advisory Warning Response

When you see an `⚠ ADVISORY` warning from the post-edit hook, you must either fix the violation or output a DISMISS line before your next tool call:

`DISMISS: <file>:<line> | <matched pattern> | reason: <justification, 20+ chars>`

### Recovery

Git is the recovery path for incorrect CONTEXT updates. Use `git log`/`diff`/`blame` to identify drift. The compliance monitor writes its last report to `.claude/last_compliance_report.json` — check it at session start if the prior session ended with unresolved FAILs.

---

## 📎 TIER 3 — REFERENCE

### CONTEXT File Maintenance

- Update the relevant `CONTEXT_*.md` after every meaningful change to code, config, or docs
- Read the `CONTEXT_*.md` before touching any module *(enforced by Claude Code hook)*
- Module context files are listed in: CONTEXT.md → Module Context Files table
- Full maintenance rules, required sections, and update triggers: see CONTEXT.md § CONTEXT File Maintenance

### Documentation & Versioning

- Every `.md` file has a semantic version
- Version bump rules are in each `CONTEXT_*.md` file's Version Decision Table
- Plans live in `plans/`, one per module, with exact function signatures
- Full versioning rules: see CONTEXT.md § Versioning Rules

### Pre-Completion Compliance Checklist

Before marking any task complete, all of the following must be true.

**Blocking** (caught by git pre-commit — commit will fail):

- [ ] All tests pass (`pytest tests/` or per `compliance_config.yaml` test_commands)
- [ ] All source files are under 150 lines
- [ ] No hardcoded values introduced
- [ ] Every source file has the Area/PRD/NOTE header

**Advisory** (caught by compliance monitor — report injected at session end):

- [ ] Every new file registered in CONTEXT.md and its module's CONTEXT_*.md with correct line count
- [ ] Line counts in docs match `wc -l`
- [ ] Interface Contracts table matches actual filenames in code
- [ ] All `.md` files have semantic versions, incremented if touched
- [ ] Plans synced with code changes
```

- [ ] **Step 3: Verify the new file**

Read the rewritten CLAUDE.md and confirm:
- Three tiers are present with correct visual markers
- No Architecture, Data Flow, Terminology, Project Structure, or detailed versioning/maintenance sections remain (those moved to CONTEXT.md)
- Module Context Files table is replaced by a pointer to CONTEXT.md
- Language comment table covers all 4 syntax families
- Session Scope Assessment block is present in Tier 2
- Advisory warning DISMISS format is present in Tier 2
- Recovery section references `.claude/last_compliance_report.json`
- Compliance checklist is split into Blocking and Advisory categories

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "refactor: restructure CLAUDE.md into three enforcement tiers

Move reference material (architecture, terminology, data flow, project
structure, detailed versioning/maintenance rules) to CONTEXT.md. Keep
CLAUDE.md focused on rules, workflow, and the compliance checklist.
Split checklist into blocking (git hook) and advisory (compliance monitor)
categories."
```

---

## Task 2: Rewrite CONTEXT.md with Expanded Sections and TOC

**Files:**
- Modify: `CONTEXT.md`

CONTEXT.md absorbs the reference material from CLAUDE.md and gains a table of contents.

- [ ] **Step 1: Read the current CONTEXT.md**

Read the full file to understand existing structure.

- [ ] **Step 2: Write the new CONTEXT.md**

Replace the entire file with:

```markdown
# CONTEXT.md

Version: 2.0.0

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
| `CONTEXT_[module1].md` | [Module 1] | planning |
| `CONTEXT_[module2].md` | [Module 2] | planning |

### When to read which file

- Working on [module 1] → read `ContextModuleDocumentation/CONTEXT_[module1].md`
- Working on [module 2] → read `ContextModuleDocumentation/CONTEXT_[module2].md`

---

## Architecture & File Map

<!-- Every file in the project with line counts. Update after every change. -->

```
project/
├── CLAUDE.md                           # project rules (tiered)
├── CONTEXT.md                          # this file — living project snapshot
├── CONTEXT_MODULE.md                   # template for new context files
├── compliance_config.yaml              # machine-readable policy for hooks
├── setup.sh                            # project setup with safe hook install
├── ContextModuleDocumentation/
│   ├── CONTEXT_[module1].md           # [module 1] state
│   └── CONTEXT_[module2].md           # [module 2] state
├── agents/
│   └── compliance_monitor.md          # compliance auditor agent definition
├── hooks/
│   ├── pre-commit                     # git pre-commit hard gate
│   ├── parse_config.py                # YAML parser fallback for shell hooks
│   ├── claude_read_gate.py            # Claude Code PreToolUse read gate
│   └── claude_advisory_scan.py        # Claude Code PostToolUse advisory scanner
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
    ├── conftest.py        (XX lines)  — Shared test fixtures
    ├── test_[module1].py  (XX lines)  — X tests for [module 1]
    └── test_[module2].py  (XX lines)  — X tests for [module 2]
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

## Key Project Decisions

<!-- Decisions that affect the whole project, not just one module. Module-specific decisions go in CONTEXT_*.md files. -->

- **[Decision]** — [What was decided and why]
- **[Decision]** — [What was decided and why]
```

- [ ] **Step 3: Verify the new file**

Read the rewritten CONTEXT.md and confirm:
- Table of Contents is present as first section after version
- New sections present: Terminology, Architecture, Data Flow, Versioning Rules, CONTEXT File Maintenance
- Module Context Files table has note: "Canonical table. CLAUDE.md points here"
- Architecture & File Map includes hooks/, agents/, compliance_config.yaml, setup.sh
- CONTEXT File Maintenance Required Sections list includes Version Decision Table and Module Change Checklist

- [ ] **Step 4: Commit**

```bash
git add CONTEXT.md
git commit -m "refactor: expand CONTEXT.md with reference material from CLAUDE.md

Add TOC, Terminology, Architecture, Data Flow, Versioning Rules, and
CONTEXT File Maintenance sections. Architecture & File Map now includes
hooks, agents, and compliance infrastructure. Module Context Files table
is now the canonical source (CLAUDE.md points here)."
```

---

## Task 3: Update CONTEXT_MODULE.md Template

**Files:**
- Modify: `CONTEXT_MODULE.md`

Add the Version Decision Table and annotate the Module Change Checklist with enforcement mechanisms.

- [ ] **Step 1: Read the current CONTEXT_MODULE.md**

Read the full file.

- [ ] **Step 2: Add Version Decision Table above Module Change Checklist**

Insert this section immediately before `## Module Change Checklist`:

```markdown
---

## Version Decision Table

<!-- Project-level overrides to this table live in CONTEXT.md § Versioning Rules -->

| Change type | Version bump |
|---|---|
| Line count correction only | patch |
| New file added to module | minor |
| File removed or renamed | minor |
| Module behavior/API changed | minor |
| Module removed or replaced | major |
```

- [ ] **Step 3: Replace the Module Change Checklist**

Replace the existing checklist with the annotated version:

```markdown
## Module Change Checklist

Run this checklist after every change to this module. Do not skip items.

- [ ] **Line counts** — Update every file's line count in the Architecture & File Map above (`wc -l` each file) *(verified by compliance monitor)*
- [ ] **New files** — If you created a new file: add it to the File Map above, add it to `CONTEXT.md` Architecture & File Map, and ensure it has the Area/PRD/NOTE header *(header enforced by pre-commit)*
- [ ] **Removed files** — If you deleted a file: remove it from the File Map above and from `CONTEXT.md` *(verified by compliance monitor)*
- [ ] **Split files** — If you split a file: update the original's line count, add the new file(s) everywhere, update imports in consumers
- [ ] **Interface changes** — If filenames or output formats changed: update the Interface Contracts table in `CONTEXT.md` *(verified by compliance monitor)*
- [ ] **Version bump** — Increment this file's version per the Version Decision Table above
- [ ] **Recent Changes** — Add a dated bullet to the Recent Changes section above
```

- [ ] **Step 4: Update the version**

Change `Version: 1.0.0` to `Version: 1.1.0` at the top of the file.

- [ ] **Step 5: Verify**

Read the file and confirm:
- Version Decision Table appears between Key Decisions & Notes and Module Change Checklist
- Override escape hatch comment is present
- Each checklist item that has hook enforcement has an italic annotation
- Version is 1.1.0

- [ ] **Step 6: Commit**

```bash
git add CONTEXT_MODULE.md
git commit -m "feat: add version decision table and annotated checklist to template

Inline version bump rules (patch/minor/major) with project-level
override escape hatch. Annotate checklist items with enforcement
mechanism (pre-commit vs compliance monitor)."
```

---

## Task 4: Create compliance_config.yaml

**Files:**
- Create: `compliance_config.yaml`

- [ ] **Step 1: Write the file**

Create `compliance_config.yaml` at project root with this exact content:

```yaml
# compliance_config.yaml
# Machine-readable policy for git hooks and Claude Code hooks.
# Human-readable rules live in CLAUDE.md. This file drives enforcement.
# See design spec: docs/superpowers/specs/2026-04-05-template-enforcement-overhaul-design.md

version: "1.0.0"

# --- Git pre-commit: hard gates ---
pre_commit:
  max_file_lines: 150
  file_header:
    required: true
    patterns:
      python:    "^# Area: .+\\n# PRD: .+\\n# NOTE: .+"
      shell:     "^# Area: .+\\n# PRD: .+\\n# NOTE: .+"
      js:        "^// Area: .+\\n// PRD: .+\\n// NOTE: .+"
      ts:        "^// Area: .+\\n// PRD: .+\\n// NOTE: .+"
      go:        "^// Area: .+\\n// PRD: .+\\n// NOTE: .+"
      rust:      "^// Area: .+\\n// PRD: .+\\n// NOTE: .+"
      java:      "^// Area: .+\\n// PRD: .+\\n// NOTE: .+"
      css:       "^/\\* Area: .+\\n\\s*PRD: .+\\n\\s*NOTE: .+"
      html:      "^<!-- Area: .+\\n\\s*PRD: .+\\n\\s*NOTE: .+"
    extensions:
      python:  [".py"]
      shell:   [".sh", ".bash", ".zsh"]
      js:      [".js", ".jsx", ".mjs", ".cjs"]
      ts:      [".ts", ".tsx"]
      go:      [".go"]
      rust:    [".rs"]
      java:    [".java"]
      css:     [".css", ".scss", ".less"]
      html:    [".html", ".htm"]
  hardcoded_values:
    block:
      - pattern: "https?://[^\\s\"']+"
        description: "URL literal"
        exclude_files: ["**/test_*", "**/conftest.py", "**/*_test.*"]
      - pattern: "sk-[a-zA-Z0-9]{20,}"
        description: "API key pattern"
      - pattern: "(?:^|/)(?:Users|home)/\\w+"
        description: "Absolute home directory path"
      - pattern: "\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b"
        description: "IP address literal"
        exclude_files: ["**/test_*", "**/conftest.py", "**/*_test.*"]
      - pattern: "api[_-]?key\\s*=\\s*[\"'][^\"']+"
        description: "Inline API key assignment"
      - pattern: "password\\s*=\\s*[\"'][^\"']+"
        description: "Inline password assignment"
    allowlist:
      - pattern: "http://localhost"
        reason: "Local development server — not a production URL"
      - pattern: "http://127.0.0.1"
        reason: "Loopback address — not a production URL"
      - pattern: "https://example.com"
        reason: "RFC 2606 reserved domain for documentation examples"
  test_commands:
    - "pytest tests/"
  source_dirs: ["src/"]
  test_dirs: ["tests/"]
  exclude_dirs: [".git", "__pycache__", "node_modules", ".venv", "venv"]

# --- Claude Code PostToolUse: advisory warnings ---
advisory:
  hardcoded_values:
    warn:
      - pattern: "\\b[A-Z_]{2,}\\s*=\\s*\\d+"
        description: "Possible magic number assignment"
      - pattern: "timeout\\s*=\\s*\\d+"
        description: "Possible hardcoded timeout"
      - pattern: "\"(claude|gpt|gemini|llama|mistral)[\\w-]*\""
        description: "Possible hardcoded model name"
      - pattern: "\\bport\\s*=\\s*\\d+"
        description: "Possible hardcoded port"
      - pattern: "sleep\\(\\d+\\)"
        description: "Possible hardcoded delay"
      - pattern: "max_retries\\s*=\\s*\\d+"
        description: "Possible hardcoded retry count"
  dismissal_log: ".claude/advisory_dismissals.json"
  min_justification_length: 20

# --- Claude Code PreToolUse: read gate ---
read_gate:
  module_map:
    # Machine-readable source of truth for module-to-directory mapping.
    # CONTEXT.md Architecture & File Map is the human-readable view.
    # Keep both in sync. Add entries as modules are created.
    # Example:
    # ingestion:
    #   source_dir: "src/ingestion/"
    #   context_file: "ContextModuleDocumentation/CONTEXT_ingestion.md"
  confirmation_pattern: "^CONTEXT READ: .+ \\| state: .+ \\| last change: .+ \\| open tasks: \\d+"
  session_state_file: ".claude/session_reads.json"

# --- Claude Code Stop: compliance monitor ---
compliance_monitor:
  agent_definition: "agents/compliance_monitor.md"
  report_path: ".claude/last_compliance_report.json"
  checks:
    - id: "file_registration"
      description: "Every source file exists in CONTEXT.md and its module CONTEXT_*.md"
    - id: "line_count_accuracy"
      description: "Line counts in CONTEXT files match wc -l"
    - id: "interface_contracts"
      description: "Filenames in Interface Contracts table appear in producer/consumer files (signal check — dynamic filenames may not match)"
    - id: "version_incremented"
      description: "Every .md file touched has its version incremented vs last commit"
    - id: "removed_files_cleaned"
      description: "No deleted files still referenced in CONTEXT files"
    - id: "advisory_dismissals_reviewed"
      description: "Every dismissed advisory warning has a justification of min_justification_length+ chars"
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('compliance_config.yaml'))" && echo "VALID" || echo "INVALID"
```

Expected: `VALID`

- [ ] **Step 3: Commit**

```bash
git add compliance_config.yaml
git commit -m "feat: add compliance_config.yaml policy definition

Machine-readable policy for git hooks and Claude Code hooks. Defines
line limits, header patterns, hardcoded value detection (block + advisory),
read gate module map, and compliance monitor check definitions."
```

---

## Task 5: Create hooks/parse_config.py

**Files:**
- Create: `hooks/parse_config.py`

Python fallback for parsing compliance_config.yaml when `yq` is not available. Outputs flat KEY=VALUE pairs that the shell pre-commit hook can `eval`.

- [ ] **Step 1: Create the hooks directory**

```bash
mkdir -p hooks
```

- [ ] **Step 2: Write the parser**

Create `hooks/parse_config.py`:

```python
#!/usr/bin/env python3
"""Parse compliance_config.yaml and output KEY=VALUE pairs for shell hooks.

Usage: python3 hooks/parse_config.py <key_path>
Example: python3 hooks/parse_config.py pre_commit.max_file_lines
         → 150

For list values, outputs one item per line.
For dict values, outputs key=value per line.
"""
import sys
import yaml


def resolve(data, path):
    """Walk a dotted path into a nested dict."""
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_config.py <key_path>", file=sys.stderr)
        sys.exit(1)

    config_path = "compliance_config.yaml"
    key_path = sys.argv[1]

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    value = resolve(config, key_path)
    if value is None:
        sys.exit(1)

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"{k}={v}")
                print("---")
            else:
                print(item)
    elif isinstance(value, dict):
        for k, v in value.items():
            print(f"{k}={v}")
    else:
        print(value)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Make it executable and test**

```bash
chmod +x hooks/parse_config.py
python3 hooks/parse_config.py pre_commit.max_file_lines
```

Expected output: `150`

```bash
python3 hooks/parse_config.py pre_commit.source_dirs
```

Expected output: `src/`

- [ ] **Step 4: Commit**

```bash
git add hooks/parse_config.py
git commit -m "feat: add YAML config parser fallback for shell hooks

Lightweight Python script that resolves dotted key paths in
compliance_config.yaml and outputs values as shell-friendly
KEY=VALUE pairs. Used by pre-commit hook when yq is unavailable."
```

---

## Task 6: Create hooks/pre-commit

**Files:**
- Create: `hooks/pre-commit`

- [ ] **Step 1: Write the pre-commit hook**

Create `hooks/pre-commit`:

```bash
#!/usr/bin/env bash
# Git pre-commit hook — hard gate enforcement.
# Reads policy from compliance_config.yaml.
# See: docs/superpowers/specs/2026-04-05-template-enforcement-overhaul-design.md

set -euo pipefail

CONFIG="compliance_config.yaml"
FAIL_COUNT=0
PASS_COUNT=0
FAILURES=""

# --- Config reader ---
# Tries yq first, falls back to Python parser.
read_config() {
    local key="$1"
    if command -v yq &>/dev/null; then
        yq -r ".$key" "$CONFIG" 2>/dev/null
    elif [ -f "hooks/parse_config.py" ]; then
        python3 hooks/parse_config.py "$key" 2>/dev/null
    else
        echo "ERROR: No YAML parser available. Install yq or ensure hooks/parse_config.py exists." >&2
        exit 1
    fi
}

fail() {
    FAILURES="${FAILURES}\n✗ FAIL  $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

pass() {
    PASS_COUNT=$((PASS_COUNT + 1))
}

# --- Read config values ---
MAX_LINES=$(read_config "pre_commit.max_file_lines")
MAX_LINES="${MAX_LINES:-150}"

# --- Get staged files ---
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# --- Read source_dirs and exclude_dirs ---
SOURCE_DIRS=$(read_config "pre_commit.source_dirs")
EXCLUDE_DIRS=$(read_config "pre_commit.exclude_dirs")

# --- Filter to source files ---
is_source_file() {
    local file="$1"
    local in_source=false

    while IFS= read -r dir; do
        [ -z "$dir" ] && continue
        if [[ "$file" == "$dir"* ]]; then
            in_source=true
            break
        fi
    done <<< "$SOURCE_DIRS"

    if ! $in_source; then
        return 1
    fi

    while IFS= read -r dir; do
        [ -z "$dir" ] && continue
        if [[ "$file" == *"$dir"* ]]; then
            return 1
        fi
    done <<< "$EXCLUDE_DIRS"

    return 0
}

# --- Detect file language from extension ---
get_language() {
    local file="$1"
    case "$file" in
        *.py)                       echo "python" ;;
        *.sh|*.bash|*.zsh)          echo "shell" ;;
        *.js|*.jsx|*.mjs|*.cjs)     echo "js" ;;
        *.ts|*.tsx)                  echo "ts" ;;
        *.go)                       echo "go" ;;
        *.rs)                       echo "rust" ;;
        *.java)                     echo "java" ;;
        *.css|*.scss|*.less)        echo "css" ;;
        *.html|*.htm)               echo "html" ;;
        *)                          echo "" ;;
    esac
}

# --- Check: header pattern by language ---
check_header() {
    local file="$1"
    local lang
    lang=$(get_language "$file")
    [ -z "$lang" ] && return 0

    local has_header=false
    case "$lang" in
        python|shell)
            head -3 "$file" | grep -q "^# Area:" && \
            head -3 "$file" | grep -q "^# PRD:" && \
            head -3 "$file" | grep -q "^# NOTE:" && has_header=true
            ;;
        js|ts|go|rust|java)
            head -3 "$file" | grep -q "^// Area:" && \
            head -3 "$file" | grep -q "^// PRD:" && \
            head -3 "$file" | grep -q "^// NOTE:" && has_header=true
            ;;
        css)
            head -3 "$file" | grep -q "Area:" && \
            head -3 "$file" | grep -q "PRD:" && \
            head -3 "$file" | grep -q "NOTE:" && has_header=true
            ;;
        html)
            head -3 "$file" | grep -q "Area:" && \
            head -3 "$file" | grep -q "PRD:" && \
            head -3 "$file" | grep -q "NOTE:" && has_header=true
            ;;
    esac

    if ! $has_header; then
        fail "${file}:  missing Area/PRD/NOTE header"
        return 1
    fi
    return 0
}

# --- Check: hardcoded values (block patterns) ---
check_hardcoded() {
    local file="$1"
    local line_num match

    # URL literals (excluding allowlisted patterns and test files)
    if [[ "$file" != *test_* && "$file" != *conftest* && "$file" != *_test.* ]]; then
        while IFS=: read -r line_num match; do
            # Check against allowlist
            local allowed=false
            for pattern in "http://localhost" "http://127.0.0.1" "https://example.com"; do
                if [[ "$match" == *"$pattern"* ]]; then
                    allowed=true
                    break
                fi
            done
            if ! $allowed; then
                fail "${file}:${line_num}  URL literal: $(echo "$match" | head -c 60)"
            fi
        done < <(grep -n -E "https?://[^[:space:]\"']+" "$file" 2>/dev/null || true)
    fi

    # API key patterns
    while IFS=: read -r line_num match; do
        fail "${file}:${line_num}  API key pattern: $(echo "$match" | head -c 40)"
    done < <(grep -n -E "sk-[a-zA-Z0-9]{20,}" "$file" 2>/dev/null || true)

    # Absolute home directory paths
    while IFS=: read -r line_num match; do
        fail "${file}:${line_num}  Absolute home path: $(echo "$match" | head -c 60)"
    done < <(grep -n -E "(/Users|/home)/\w+" "$file" 2>/dev/null || true)

    # IP addresses (excluding test files)
    if [[ "$file" != *test_* && "$file" != *conftest* && "$file" != *_test.* ]]; then
        while IFS=: read -r line_num match; do
            local allowed=false
            if [[ "$match" == *"127.0.0.1"* ]]; then
                allowed=true
            fi
            if ! $allowed; then
                fail "${file}:${line_num}  IP address: $(echo "$match" | head -c 40)"
            fi
        done < <(grep -n -E "\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b" "$file" 2>/dev/null || true)
    fi

    # Inline API key/password assignments
    while IFS=: read -r line_num match; do
        fail "${file}:${line_num}  Inline secret: $(echo "$match" | head -c 50)"
    done < <(grep -n -E "(api[_-]?key|password)\s*=\s*[\"'][^\"']+" "$file" 2>/dev/null || true)
}

# --- Main: run checks on each staged source file ---
echo ""
echo "PRE-COMMIT CHECK"
echo "================"

for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    is_source_file "$file" || continue

    file_failed=false

    # Line count check
    line_count=$(wc -l < "$file" | tr -d ' ')
    if [ "$line_count" -gt "$MAX_LINES" ]; then
        fail "${file}:  ${line_count} lines (max: ${MAX_LINES})"
        file_failed=true
    fi

    # Header check
    check_header "$file" || file_failed=true

    # Hardcoded values check
    local_fails=$FAIL_COUNT
    check_hardcoded "$file"
    [ "$FAIL_COUNT" -gt "$local_fails" ] && file_failed=true

    if ! $file_failed; then
        echo "✓ PASS  $file"
        pass
    fi
done

# --- Run tests ---
TEST_CMDS=$(read_config "pre_commit.test_commands")
while IFS= read -r cmd; do
    [ -z "$cmd" ] && continue
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✓ PASS  tests passed ($cmd)"
        pass
    else
        fail "tests failed ($cmd)"
    fi
done <<< "$TEST_CMDS"

# --- Summary ---
if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "$FAILURES"
    echo ""
    echo "BLOCKED: ${FAIL_COUNT} violation(s) must be fixed before commit."
    exit 1
else
    echo ""
    echo "ALL CHECKS PASSED (${PASS_COUNT} items)"
    exit 0
fi
```

- [ ] **Step 2: Make executable**

```bash
chmod +x hooks/pre-commit
```

- [ ] **Step 3: Commit**

```bash
git add hooks/pre-commit
git commit -m "feat: add git pre-commit hook for hard-gate enforcement

Checks staged source files for: line count > 150, missing Area/PRD/NOTE
header, hardcoded URLs/secrets/paths/IPs, and test failures. Reads all
thresholds and patterns from compliance_config.yaml. Falls back to
Python parser when yq is unavailable."
```

---

## Task 7: Create hooks/claude_read_gate.py

**Files:**
- Create: `hooks/claude_read_gate.py`

Claude Code PreToolUse hook that blocks Edit/Write until the agent has confirmed reading the relevant CONTEXT file.

- [ ] **Step 1: Write the read gate**

Create `hooks/claude_read_gate.py`:

```python
#!/usr/bin/env python3
"""Claude Code PreToolUse hook: read gate.

Blocks Edit/Write tool calls on module source files until the agent has:
1. Called Read on the module's CONTEXT file in this session
2. Output the structured CONTEXT READ confirmation line

Reads module_map from compliance_config.yaml.
Tracks session state in .claude/session_reads.json.
"""
import json
import os
import sys
import time
import yaml


CONFIG_PATH = "compliance_config.yaml"
DEFAULT_SESSION_STATE = ".claude/session_reads.json"
# Sessions older than 4 hours are considered stale
SESSION_TIMEOUT_SECONDS = 4 * 60 * 60


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_session_state(state_path):
    """Load session reads, wiping if stale."""
    if not os.path.exists(state_path):
        return {"timestamp": time.time(), "reads": {}, "confirmations": []}

    with open(state_path, "r") as f:
        state = json.load(f)

    # Wipe if stale (from prior/crashed session)
    age = time.time() - state.get("timestamp", 0)
    if age > SESSION_TIMEOUT_SECONDS:
        return {"timestamp": time.time(), "reads": {}, "confirmations": []}

    return state


def save_session_state(state_path, state):
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def find_module_for_file(file_path, module_map):
    """Return the module name and context file for a given source file."""
    for module_name, module_info in module_map.items():
        source_dir = module_info.get("source_dir", "")
        if file_path.startswith(source_dir):
            return module_name, module_info.get("context_file", "")
    return None, None


def record_read(state_path, file_path):
    """Called by PostToolUse on Read to record a file was read."""
    state = load_session_state(state_path)
    state["reads"][file_path] = time.time()
    save_session_state(state_path, state)


def check_gate(state_path, target_file, module_map):
    """Check if the read gate allows editing target_file.

    Returns None if allowed, or an error message string if blocked.
    """
    module_name, context_file = find_module_for_file(target_file, module_map)

    # File not in any mapped module — allow
    if module_name is None:
        return None

    state = load_session_state(state_path)

    # Check if CONTEXT file was read
    if context_file not in state.get("reads", {}):
        return (
            f"⛔ READ GATE: You are editing {target_file} but have not confirmed "
            f"reading {os.path.basename(context_file)}. Read the file and output:\n"
            f"CONTEXT READ: {os.path.basename(context_file)} | state: <phase> "
            f"| last change: <date+desc> | open tasks: <N>"
        )

    return None


def main():
    """Entry point for hook invocation.

    Usage:
        Pre-edit check: python3 hooks/claude_read_gate.py check <target_file>
        Record a read:  python3 hooks/claude_read_gate.py record <file_path>
    """
    if len(sys.argv) < 3:
        print("Usage: claude_read_gate.py <check|record> <file_path>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    config = load_config()
    read_gate_config = config.get("read_gate", {})
    module_map = read_gate_config.get("module_map", {}) or {}
    state_path = read_gate_config.get("session_state_file", DEFAULT_SESSION_STATE)

    if action == "record":
        record_read(state_path, file_path)
    elif action == "check":
        error = check_gate(state_path, file_path, module_map)
        if error:
            print(error)
            sys.exit(1)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make executable**

```bash
chmod +x hooks/claude_read_gate.py
```

- [ ] **Step 3: Commit**

```bash
git add hooks/claude_read_gate.py
git commit -m "feat: add Claude Code read gate hook

PreToolUse hook that blocks Edit/Write until the agent confirms reading
the module's CONTEXT file. Tracks session reads in .claude/session_reads.json
with stale-session detection (4-hour timeout). Reads module_map from
compliance_config.yaml."
```

---

## Task 8: Create hooks/claude_advisory_scan.py

**Files:**
- Create: `hooks/claude_advisory_scan.py`

Claude Code PostToolUse hook that scans edited files for advisory-level hardcoded value patterns and approaching line count limits.

- [ ] **Step 1: Write the advisory scanner**

Create `hooks/claude_advisory_scan.py`:

```python
#!/usr/bin/env python3
"""Claude Code PostToolUse hook: advisory scanner.

Scans files after Edit/Write for:
1. Advisory hardcoded value patterns (non-blocking warnings)
2. Line count approaching the limit (warning at 90%+)

Reads patterns from compliance_config.yaml advisory section.
"""
import json
import os
import re
import sys
import time
import yaml


CONFIG_PATH = "compliance_config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def scan_hardcoded(file_path, warn_patterns):
    """Scan a file for advisory hardcoded value patterns.

    Returns list of (line_number, line_text, description) tuples.
    """
    matches = []
    with open(file_path, "r") as f:
        for i, line in enumerate(f, 1):
            for pattern_def in warn_patterns:
                pattern = pattern_def["pattern"]
                description = pattern_def["description"]
                if re.search(pattern, line):
                    matches.append((i, line.rstrip(), description))
    return matches


def check_line_count(file_path, max_lines):
    """Check if file is approaching line limit.

    Returns (current_count, remaining) or None if not near limit.
    """
    with open(file_path, "r") as f:
        count = sum(1 for _ in f)

    threshold = int(max_lines * 0.9)  # Warn at 90%
    if count >= threshold:
        return count, max_lines - count
    return None


def log_dismissal(dismissal_log, file_path, line_num, pattern, reason):
    """Append a dismissal to the advisory dismissals log."""
    os.makedirs(os.path.dirname(dismissal_log), exist_ok=True)

    dismissals = []
    if os.path.exists(dismissal_log):
        with open(dismissal_log, "r") as f:
            dismissals = json.load(f)

    dismissals.append({
        "file": file_path,
        "line": line_num,
        "pattern": pattern,
        "reason": reason,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

    with open(dismissal_log, "w") as f:
        json.dump(dismissals, f, indent=2)


def main():
    """Entry point.

    Usage:
        Scan:    python3 hooks/claude_advisory_scan.py scan <file_path>
        Dismiss: python3 hooks/claude_advisory_scan.py dismiss <file>:<line> <pattern> <reason>
    """
    if len(sys.argv) < 3:
        print("Usage: claude_advisory_scan.py <scan|dismiss> <args...>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    config = load_config()

    if action == "scan":
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            sys.exit(0)

        warn_patterns = config.get("advisory", {}).get("hardcoded_values", {}).get("warn", [])
        max_lines = config.get("pre_commit", {}).get("max_file_lines", 150)

        output_lines = []

        # Check hardcoded patterns
        matches = scan_hardcoded(file_path, warn_patterns)
        if matches:
            output_lines.append(f"⚠ ADVISORY: {file_path}")
            for line_num, line_text, description in matches:
                output_lines.append(f"  Line {line_num}: {line_text}  → {description}")
            output_lines.append("")
            output_lines.append(
                "Review each warning. Fix the violation or DISMISS before your next tool call."
            )

        # Check line count
        result = check_line_count(file_path, max_lines)
        if result:
            count, remaining = result
            output_lines.append(
                f"⚠ LINE COUNT: {file_path} is {count} lines "
                f"(limit: {max_lines}, {remaining} remaining)"
            )

        if output_lines:
            print("\n".join(output_lines))

    elif action == "dismiss":
        # Parse: dismiss <file>:<line> <pattern> <reason>
        if len(sys.argv) < 5:
            print("Usage: dismiss <file>:<line> <pattern> <reason>", file=sys.stderr)
            sys.exit(1)

        file_line = sys.argv[2]
        pattern = sys.argv[3]
        reason = sys.argv[4]

        file_path, line_num = file_line.rsplit(":", 1)
        dismissal_log = config.get("advisory", {}).get("dismissal_log", ".claude/advisory_dismissals.json")
        min_length = config.get("advisory", {}).get("min_justification_length", 20)

        if len(reason) < min_length:
            print(f"⛔ Justification too short ({len(reason)} chars, minimum {min_length})")
            sys.exit(1)

        log_dismissal(dismissal_log, file_path, int(line_num), pattern, reason)
        print(f"✓ Dismissal logged for {file_path}:{line_num}")

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make executable**

```bash
chmod +x hooks/claude_advisory_scan.py
```

- [ ] **Step 3: Commit**

```bash
git add hooks/claude_advisory_scan.py
git commit -m "feat: add Claude Code advisory scanner hook

PostToolUse hook that scans files for advisory-level hardcoded patterns
(magic numbers, timeouts, model names, ports, delays, retry counts) and
warns when line count exceeds 90% of limit. Supports structured dismissal
with minimum justification length enforcement."
```

---

## Task 9: Create agents/compliance_monitor.md

**Files:**
- Create: `agents/compliance_monitor.md`

- [ ] **Step 1: Create the agents directory**

```bash
mkdir -p agents
```

- [ ] **Step 2: Write the compliance monitor agent definition**

Create `agents/compliance_monitor.md`:

```markdown
# Compliance Monitor Agent

You are a compliance auditor. You receive a set of changed files and project documentation. Your ONLY job is to verify consistency between code and docs. You do not fix anything. You do not suggest improvements. You report PASS or FAIL for each check with evidence.

## Inputs

You receive:

1. A list of files changed in this session (from `git diff --name-only`)
2. The full content of `compliance_config.yaml`
3. The full content of `CONTEXT.md`
4. The full content of every `ContextModuleDocumentation/CONTEXT_*.md` file
5. The full content of `.claude/advisory_dismissals.json` (if it exists)

## Checks

Run each check independently. A failure in one check does not affect others.

### CHECK 1: file_registration

For every source file under `source_dirs` (from compliance_config.yaml):

- Verify it appears in CONTEXT.md Architecture & File Map
- Identify which module it belongs to (using `module_map` from compliance_config.yaml)
- Verify it appears in that module's CONTEXT_*.md Architecture & File Map
- For files in the git diff (newly created this session): flag if missing from either

**PASS:** all source files are registered in both locations
**FAIL:** list each unregistered file and where it's missing

### CHECK 2: line_count_accuracy

For every file listed in any CONTEXT_*.md or CONTEXT.md Architecture & File Map:

- Run `wc -l` on the actual file
- Compare to the count claimed in the docs
- Tolerance: 0 lines. Counts must be exact.

**PASS:** all documented line counts match reality
**FAIL:** list each mismatch with file, documented count, actual count, and which CONTEXT file

### CHECK 3: interface_contracts

Read the Interface Contracts table in CONTEXT.md. For each row:

- Verify the producer file exists on disk
- Verify the output location directory exists
- Grep the producer file for the filename pattern as a **signal** that the contract is implemented
- Verify each consumer file exists on disk
- Grep each consumer file for the filename pattern as a **signal** that it references the output

**This is a signal check, not proof.** Dynamically constructed filenames (e.g., `f"{date}_results.csv"`) won't match a literal grep. Pattern matches in comments or docstrings are false positives.

**PASS:** all contracts have signals present and all files exist
**WARNING:** pattern not found in producer/consumer — may be dynamically constructed. Report the file and pattern.
**FAIL:** producer or consumer file does not exist on disk

### CHECK 4: version_incremented

For every `.md` file in the git diff:

- Read its current `Version:` line
- Read its version from the last git commit: `git show HEAD:<filepath>` and extract the `Version:` line
- If the file was modified (not newly created), verify the version number increased

**If HEAD doesn't exist** (new repo, no prior commits): SKIP this check with note "no prior commit to compare against."

**PASS:** all modified .md files have bumped versions
**FAIL:** list each file where the version is unchanged, showing old and current version
**SKIP:** no prior commit exists

### CHECK 5: removed_files_cleaned

For every file path referenced in CONTEXT.md or any CONTEXT_*.md Architecture & File Map:

- Check if the file exists on disk

**PASS:** no references to non-existent files
**FAIL:** file is absent from disk AND is not in the current session's git diff as a deletion — this is a stale reference that must be cleaned up
**WARNING:** file is expected to exist only at runtime (generated/output files that are explicitly marked as such in the file map)

### CHECK 6: advisory_dismissals_reviewed

Read `.claude/advisory_dismissals.json`. For each entry:

- Verify the `reason` field exists
- Verify the reason is at least `min_justification_length` characters (from compliance_config.yaml, default 20)
- Do NOT evaluate whether the reason is correct — only that it exists and meets the length requirement

**PASS:** all dismissals have valid justifications
**FAIL:** list each dismissal with missing or too-short justification
**SKIP:** no dismissals file exists (nothing to check)

## Output

### JSON Report

Write to the path specified in `compliance_config.yaml` → `compliance_monitor.report_path` (default `.claude/last_compliance_report.json`):

```json
{
  "timestamp": "ISO-8601",
  "session_files_changed": ["list of changed files"],
  "checks": {
    "file_registration": {
      "status": "PASS|FAIL",
      "details": []
    },
    "line_count_accuracy": {
      "status": "PASS|FAIL",
      "details": [
        {
          "file": "path/to/file",
          "documented": 89,
          "actual": 94,
          "context_file": "CONTEXT_module.md"
        }
      ]
    },
    "interface_contracts": {
      "status": "PASS|FAIL|WARNING",
      "details": []
    },
    "version_incremented": {
      "status": "PASS|FAIL|SKIP",
      "details": []
    },
    "removed_files_cleaned": {
      "status": "PASS|FAIL|WARNING",
      "details": []
    },
    "advisory_dismissals_reviewed": {
      "status": "PASS|FAIL|SKIP",
      "details": []
    }
  },
  "summary": {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "skipped": 0
  }
}
```

### Conversation Output

Also output a human-readable summary:

```
COMPLIANCE REPORT — YYYY-MM-DD
===============================
✓ PASS  file_registration: {summary}
✗ FAIL  line_count_accuracy: {file} documented {N}, actual {N}
⚠ WARN  interface_contracts: {summary}
✓ PASS  version_incremented: {summary}
✓ PASS  removed_files_cleaned: {summary}
— SKIP  advisory_dismissals_reviewed: {reason}

{N} issue(s) to resolve before marking work complete.
```

## Constraints

- **Read-only.** Do not modify any files.
- **Do not suggest fixes.** Report facts only.
- **Run all six checks** regardless of earlier failures.
- If a CONTEXT file is malformed or unparseable: report FAIL on the relevant check with "could not parse" as the detail, not as an exception that stops the audit.
- If compliance_config.yaml is missing or unparseable: report all checks as FAIL with "missing compliance_config.yaml" and exit.
```

- [ ] **Step 3: Commit**

```bash
git add agents/compliance_monitor.md
git commit -m "feat: add compliance monitor agent definition

Read-only auditor that runs 6 checks at session end: file registration,
line count accuracy, interface contracts (signal check), version
increments, stale references, and advisory dismissal review. Writes
JSON report to .claude/last_compliance_report.json."
```

---

## Task 10: Create setup.sh

**Files:**
- Create: `setup.sh`

- [ ] **Step 1: Write setup.sh**

Create `setup.sh`:

```bash
#!/usr/bin/env bash
# setup.sh — Set up ClaudeTemplates enforcement infrastructure in a project.
# Safe: checks for existing hooks, merges settings, deduplicates .gitignore entries.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "ClaudeTemplates Setup"
echo "====================="
echo ""

# --- 1. Prerequisites ---
echo "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    error "Python 3 is required but not found."
    exit 1
fi
info "Python 3 found"

if [ ! -d ".git" ]; then
    error "Not a git repository. Run 'git init' first."
    exit 1
fi
info "Git repository found"

if command -v yq &>/dev/null; then
    info "yq found (preferred YAML parser)"
else
    warn "yq not found — will use Python fallback parser"
    echo "  Install yq for faster hook execution: brew install yq"
fi

echo ""

# --- 2. Copy template files ---
echo "Copying template files..."

copy_if_missing() {
    local src="$1"
    local dest="$2"
    if [ -f "$dest" ]; then
        warn "Skipping $dest (already exists)"
    else
        cp "$src" "$dest"
        info "Created $dest"
    fi
}

copy_if_missing "${SCRIPT_DIR}/CLAUDE.md" "CLAUDE.md"
copy_if_missing "${SCRIPT_DIR}/CONTEXT.md" "CONTEXT.md"
copy_if_missing "${SCRIPT_DIR}/CONTEXT_MODULE.md" "CONTEXT_MODULE.md"
copy_if_missing "${SCRIPT_DIR}/compliance_config.yaml" "compliance_config.yaml"

mkdir -p hooks agents
for hook_file in parse_config.py pre-commit claude_read_gate.py claude_advisory_scan.py; do
    if [ -f "${SCRIPT_DIR}/hooks/${hook_file}" ]; then
        cp "${SCRIPT_DIR}/hooks/${hook_file}" "hooks/${hook_file}"
        chmod +x "hooks/${hook_file}"
        info "Copied hooks/${hook_file}"
    fi
done

if [ -f "${SCRIPT_DIR}/agents/compliance_monitor.md" ]; then
    cp "${SCRIPT_DIR}/agents/compliance_monitor.md" "agents/compliance_monitor.md"
    info "Copied agents/compliance_monitor.md"
fi

echo ""

# --- 3. Create directories ---
echo "Creating directories..."

for dir in ContextModuleDocumentation plans docs/superpowers/specs .claude; do
    mkdir -p "$dir"
    info "Directory: $dir/"
done

echo ""

# --- 4. Git hook installation ---
echo "Installing git hooks..."

HOOK_TARGET=".git/hooks/pre-commit"
HOOK_SOURCE="hooks/pre-commit"

if [ -f "$HOOK_TARGET" ]; then
    warn "Existing pre-commit hook found at $HOOK_TARGET"
    echo ""
    echo "  Options:"
    echo "    1) Chain — rename existing to pre-commit.local, run it before template checks"
    echo "    2) Append — add template checks to end of existing hook"
    echo "    3) Skip — don't install, show manual instructions"
    echo ""
    read -rp "  Choose [1/2/3]: " choice

    case "$choice" in
        1)
            mv "$HOOK_TARGET" "${HOOK_TARGET}.local"
            info "Renamed existing hook to pre-commit.local"
            cat > "$HOOK_TARGET" << 'CHAINED_HOOK'
#!/usr/bin/env bash
# Chained pre-commit: runs existing hook first, then template checks.
HOOK_DIR="$(dirname "$0")"

if [ -x "${HOOK_DIR}/pre-commit.local" ]; then
    "${HOOK_DIR}/pre-commit.local" || exit $?
fi

exec "$(git rev-parse --show-toplevel)/hooks/pre-commit"
CHAINED_HOOK
            chmod +x "$HOOK_TARGET"
            info "Installed chained pre-commit hook"
            ;;
        2)
            echo "" >> "$HOOK_TARGET"
            echo "# --- ClaudeTemplates enforcement ---" >> "$HOOK_TARGET"
            echo "exec \"\$(git rev-parse --show-toplevel)/hooks/pre-commit\"" >> "$HOOK_TARGET"
            info "Appended template checks to existing hook"
            ;;
        3)
            warn "Skipped git hook installation"
            echo "  Manual: copy hooks/pre-commit to .git/hooks/pre-commit and chmod +x"
            ;;
        *)
            warn "Invalid choice — skipping git hook installation"
            ;;
    esac
else
    cp "$HOOK_SOURCE" "$HOOK_TARGET"
    chmod +x "$HOOK_TARGET"
    info "Installed pre-commit hook"
fi

echo ""

# --- 5. Claude Code settings ---
echo "Configuring Claude Code hooks..."

SETTINGS_FILE=".claude/settings.json"
HOOKS_CONFIG='{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "python3 hooks/claude_read_gate.py check \"$FILE_PATH\""
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Read",
        "command": "python3 hooks/claude_read_gate.py record \"$FILE_PATH\""
      },
      {
        "matcher": "Edit|Write",
        "command": "python3 hooks/claude_advisory_scan.py scan \"$FILE_PATH\""
      }
    ]
  }
}'

if [ -f "$SETTINGS_FILE" ]; then
    warn "Existing $SETTINGS_FILE found — please merge hooks manually:"
    echo "$HOOKS_CONFIG"
else
    mkdir -p .claude
    echo "$HOOKS_CONFIG" > "$SETTINGS_FILE"
    info "Created $SETTINGS_FILE with hook configuration"
fi

echo ""

# --- 6. Update .gitignore ---
echo "Updating .gitignore..."

add_gitignore() {
    local entry="$1"
    if [ -f ".gitignore" ] && grep -qF "$entry" ".gitignore"; then
        return  # Already present
    fi
    echo "$entry" >> ".gitignore"
    info "Added $entry to .gitignore"
}

add_gitignore ".claude/session_reads.json"
add_gitignore ".claude/advisory_dismissals.json"
add_gitignore ".claude/last_compliance_report.json"

echo ""

# --- 7. Summary ---
echo "Setup complete!"
echo "==============="
echo ""
echo "Next steps:"
echo "  1. Fill in CLAUDE.md placeholders (project name, description)"
echo "  2. Fill in CONTEXT.md placeholders (architecture, terminology)"
echo "  3. Add module entries to compliance_config.yaml read_gate.module_map"
echo "  4. Run your first Claude Code session"
echo ""
```

- [ ] **Step 2: Make executable**

```bash
chmod +x setup.sh
```

- [ ] **Step 3: Commit**

```bash
git add setup.sh
git commit -m "feat: add setup.sh for safe project bootstrapping

Copies template files, creates directories, installs git hooks (with
safe chaining for existing hooks), configures Claude Code hook settings,
and updates .gitignore with deduplication checks."
```

---

## Task 11: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current README.md**

Read the full file.

- [ ] **Step 2: Rewrite to reflect the new system**

Replace the entire file with:

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for enforcement overhaul

Reflect new tiered CLAUDE.md, compliance_config.yaml, hooks, and
compliance monitor. Add quick start, file table, enforcement layers
summary, and customization guide."
```

---

## Self-Review

**Spec coverage:**
- Gap 1 (self-reported checklist) → Tasks 6, 8, 9, 10 (hooks + monitor)
- Gap 2 (CLAUDE.md bloated) → Task 1 (tiered rewrite)
- Gap 3 (read-before-touch) → Task 7 (read gate)
- Gap 4 (version bumping) → Task 3 (decision table)
- Gap 5 (150-line unenforced) → Task 6 (pre-commit)
- Gap 6 (session splits) → Task 1 (Session Scope Assessment in Tier 2)
- Gap 7 (duplicated tables) → Tasks 1+2 (pointer in CLAUDE.md, canonical in CONTEXT.md)
- Gap 8 (no last known good) → Task 9 (compliance report to .claude/) + Task 1 (Recovery section)
- Gap 9 (Python-specific headers) → Task 1 (language table) + Task 6 (multi-language header check)
- Gap 10 (blocking vs non-blocking) → Task 1 (checklist split) + Tasks 6-9 (enforcement layers)

**Placeholder scan:** No TBD, TODO, "implement later", "similar to Task N", or missing code blocks found.

**Type consistency:** Checked all function names, file paths, config key paths, and CLI argument formats across tasks. `check_gate`, `record_read`, `scan_hardcoded`, `log_dismissal`, `check_line_count` — all consistent between definition and usage.
