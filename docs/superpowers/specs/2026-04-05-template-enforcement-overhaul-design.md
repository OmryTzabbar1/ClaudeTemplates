# Template Enforcement Overhaul — Design Spec

Version: 1.0.0

---

## Summary

Overhaul the ClaudeTemplates system to close 10 identified gaps in enforcement, structure, and automation. The core change is moving from self-reported compliance to a layered enforcement architecture: git pre-commit hooks as hard gates for mechanical checks, Claude Code hooks for workflow-aware mid-session feedback, and a compliance monitor agent for semantic auditing at session end.

---

## Problems Addressed

| # | Gap | Root Cause | Fix |
|---|-----|-----------|-----|
| 1 | Self-reported checklist | No verification, no oracle | Non-blocking compliance monitor + git hooks as hard gate |
| 2 | CLAUDE.md doing too many jobs | Flat structure, reference material mixed with rules | Tiered restructure, move reference content to CONTEXT.md |
| 3 | "Read before touching" unenforceable | No mechanism to confirm | PreToolUse read gate with structured proof-of-read |
| 4 | Version bumping undefined | No patch/minor/major decision table | Inline decision table in CONTEXT_MODULE.md template |
| 5 | 150-line limit unenforced | Self-checked only | Git pre-commit hard gate |
| 6 | Session splits vague | No heuristic, no mandatory assessment | Structured Session Scope Assessment in every plan |
| 7 | Duplicated Module Context Files table | Two sources of truth | CONTEXT.md canonical, CLAUDE.md pointer only |
| 8 | No "last known good" state | No recovery path documented | Persisted compliance report + git as recovery path |
| 9 | Python-specific file headers | Only `#` comment syntax shown | Language-comment-style table in CLAUDE.md |
| 10 | No blocking vs non-blocking distinction | All checklist items treated equal | Git hooks = blocking, compliance monitor = advisory |

---

## Enforcement Architecture

### Division of Responsibility

| Check | Git Pre-Commit | Claude Code Hook | Compliance Monitor |
|-------|:-:|:-:|:-:|
| File > 150 lines | **BLOCK** | warn at 140+ | — |
| Missing Area/PRD/NOTE header | **BLOCK** | — | — |
| Hardcoded values (URLs, secrets, paths, IPs) | **BLOCK** | — | — |
| Hardcoded values (magic numbers, timeouts, model names) | — | **WARN** | — |
| Tests pass | **BLOCK** | — | — |
| CONTEXT file read before edit | — | **GATE** | — |
| Line counts in docs match reality | — | — | **REPORT** |
| Files in code ↔ files in CONTEXT.md | — | — | **REPORT** |
| Interface Contracts vs actual filenames | — | — | **REPORT** (signal, not proof) |
| Version incremented on touched .md files | — | — | **REPORT** |
| Removed files cleaned from CONTEXT | — | — | **REPORT** |
| Advisory dismissals have justifications | — | — | **REPORT** |

**Principle:** Git hooks are stateless gatekeepers — they catch violations regardless of who made the change. Claude Code hooks are workflow-aware assistants — they provide mid-session feedback meaningful only in agent context. The compliance monitor catches semantic violations that neither can detect mechanically.

---

## Design: Restructured Templates

### CLAUDE.md — Tiered Structure

Shrinks from ~200 lines to ~120 by moving reference material to CONTEXT.md. Three tiers with explicit visual separation.

#### TIER 1 — NON-NEGOTIABLE RULES

Hard constraints. Violations caught by hooks and block commits.

1. **TDD** — Test first, then implementation. No exceptions.
2. **150-line file limit** — Enforced by pre-commit hook.
3. **No hardcoded values** — Secrets, paths, URLs, endpoints, model names, thresholds, timeouts → config/env/parameter. Enforced by pre-commit hook.
4. **File headers** — Every source file opens with Area/PRD/NOTE in the language's comment syntax. Enforced by pre-commit hook.

   | Language | Syntax |
   |----------|--------|
   | Python, Shell, Ruby, YAML | `# Area: ...` |
   | JS, TS, Go, Rust, Java, C | `// Area: ...` |
   | CSS | `/* Area: ... */` |
   | HTML | `<!-- Area: ... -->` |

#### TIER 2 — BEFORE STARTING WORK

Behavioral expectations and workflow rules.

**Subagent rules (in order):**
1. Read this CLAUDE.md
2. Read CONTEXT.md (includes architecture, terminology, interface contracts)
3. Read the CONTEXT_*.md for the module being worked on
4. Cross-reference dependencies against the Interface Contracts table
5. Output structured read confirmation to the conversation immediately after reading each CONTEXT file, before any Edit or Write tool calls on files in that module:
   `CONTEXT READ: <file> | state: <phase> | last change: <date+desc> | open tasks: <N>`
6. If creating a new module, create its CONTEXT_*.md first from the template
7. Run Pre-Completion Compliance Checklist before reporting done

**Behavioral expectations:**
- **Modularity** — Single responsibility per module. If it needs a long explanation, it does too much.
- **Check existing code first** — Search before implementing. Never duplicate logic.
- **Reuse before writing** — Wire into existing code. New code is a last resort.

**Session Scope Assessment** — every implementation plan must open with:
- Modules touched: [list]
- Files created/modified: [N]
- Reversible if incomplete: [yes/no — why]
- Estimated completion confidence: [high/medium/low]
- Split recommended: [yes/no]
- Justification: [one sentence]

**Advisory warning response** — when you see an `⚠ ADVISORY` warning from the post-edit hook, you must either fix the violation or output a DISMISS line before your next tool call:
`DISMISS: <file>:<line> | <matched pattern> | reason: <justification, 20+ chars>`

**Recovery** — git is the recovery path for incorrect CONTEXT updates. Use `git log`/`diff`/`blame` to identify drift. The compliance monitor writes its last report to `.claude/last_compliance_report.json` — check it at session start if the prior session ended with unresolved FAILs.

#### TIER 3 — REFERENCE

**CONTEXT file maintenance (brief):**
- Update the relevant CONTEXT_*.md after every meaningful change
- Read the CONTEXT_*.md before touching any module (enforced by hook)
- Module context files listed in: CONTEXT.md → Module Context Files table
- Full maintenance rules: see CONTEXT.md § CONTEXT File Maintenance

**Documentation & versioning (brief):**
- Every .md file has a semantic version
- Version bump rules are in each CONTEXT_*.md file's decision table
- Plans live in `plans/`, one per module, with exact function signatures
- Full versioning rules: see CONTEXT.md § Versioning Rules

**Pre-Completion Compliance Checklist:**

Blocking (caught by git pre-commit — commit will fail):
- [ ] All tests pass
- [ ] All source files under 150 lines
- [ ] No hardcoded values detected
- [ ] Every source file has Area/PRD/NOTE header

Advisory (caught by compliance monitor — report injected):
- [ ] Every new file registered in CONTEXT.md and module CONTEXT_*.md
- [ ] Line counts in docs match `wc -l`
- [ ] Interface Contracts table matches actual filenames in code
- [ ] All .md files have semantic versions, incremented if touched
- [ ] Plans synced with code changes

### What Moves to CONTEXT.md

| Section | New home in CONTEXT.md |
|---------|----------------------|
| Architecture Layers + rules | New `§ Architecture` section |
| Key Data Flow diagram | New `§ Data Flow` section |
| Terminology glossary | New `§ Terminology` section |
| Project Structure tree | Merges into existing `§ Architecture & File Map` |
| Module Context Files table (full) | Already there — CLAUDE.md gets pointer only |
| Detailed versioning rules | New `§ Versioning Rules` section |
| Detailed CONTEXT maintenance rules | New `§ CONTEXT File Maintenance` section |

CONTEXT.md gains a `## Table of Contents` as its first section after the version line so agents can navigate directly to the section they need.

### CONTEXT_MODULE.md — Additions

**Version Decision Table** (added above Module Change Checklist):

```
<!-- Project-level overrides to this table live in CONTEXT.md -->
| Change type                | Version bump |
|----------------------------|-------------|
| Line count correction only | patch        |
| New file added to module   | minor        |
| File removed or renamed    | minor        |
| Module behavior/API changed | minor       |
| Module removed or replaced | major        |
```

**Updated Module Change Checklist** — same items, annotated with enforcement mechanism:

- [ ] **Line counts** — `wc -l` each file, update File Map *(verified by compliance monitor)*
- [ ] **New files** — registered in this file + CONTEXT.md + has header *(header enforced by pre-commit)*
- [ ] **Removed files** — removed from this file + CONTEXT.md *(verified by compliance monitor)*
- [ ] **Split files** — counts updated, new files registered, imports updated
- [ ] **Interface changes** — Interface Contracts table in CONTEXT.md updated *(verified by compliance monitor)*
- [ ] **Version bump** — per decision table above
- [ ] **Recent Changes** — dated bullet added

---

## Design: compliance_config.yaml

Machine-readable policy definition. Lives at project root. Hooks read this file for all thresholds, patterns, and check definitions.

```yaml
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

### Key Design Decisions

- **`module_map` is explicit in this file** — not parsed from CONTEXT.md markdown. CONTEXT.md's Architecture & File Map is the human-readable view; this is the machine-readable truth. Both must be kept in sync, but hook reliability doesn't depend on markdown formatting.
- **Allowlist entries have a required `reason` field** — the compliance monitor can surface stale allowlist entries by checking whether the reason still applies. Prevents the allowlist from becoming a graveyard of unaudited exceptions.
- **`test_commands` is a list** — supports polyglot projects and multiple test suites without migration later.
- **`min_justification_length: 20`** — gives the advisory dismissal review check actual teeth. `reason: "ok"` doesn't satisfy it.

---

## Design: Hook Scripts

### Git Pre-Commit Hook

**File:** `hooks/pre-commit`

POSIX-compatible shell script. Reads `compliance_config.yaml` for all thresholds and patterns.

**Dependencies:** Requires a YAML parser. Ships two options:
- **`yq`** — lightweight single binary (brew/apt). Hook checks for it first.
- **`hooks/parse_config.py`** — 30-line Python fallback that reads compliance_config.yaml and outputs KEY=VALUE pairs. Ships with the template; no external dependency beyond Python.

The hook tries `yq` first, falls back to the Python parser.

**Execution flow:**

1. Parse compliance_config.yaml
2. Get staged files: `git diff --cached --name-only --diff-filter=ACM`
3. Filter to `source_dirs`, excluding `exclude_dirs`
4. For each staged source file:
   - **LINE COUNT:** `wc -l` > `max_file_lines` → FAIL
   - **HEADER CHECK:** match extension → language → regex pattern → FAIL if missing
   - **HARDCODED VALUES (block patterns):** run each pattern, skip files matching `exclude_files` globs, check against allowlist → FAIL with line number and description
5. **RUN TESTS:** execute each command in `test_commands` → FAIL on non-zero exit
6. Any FAIL → print structured summary, exit 1 (commit blocked). All PASS → exit 0.

**Output format:**

```
PRE-COMMIT CHECK
================
✗ FAIL  src/ingestion/loader.py:  167 lines (max: 150)
✗ FAIL  src/ingestion/parser.py:  missing Area/PRD/NOTE header
✗ FAIL  src/ingestion/writer.py:12  URL literal: "https://api.example.com/v2"
✓ PASS  src/ingestion/models.py
✓ PASS  tests passed (pytest tests/)

BLOCKED: 3 violations must be fixed before commit.
```

### Claude Code Hook 1: PreToolUse Read Gate

**Triggers on:** `Edit`, `Write` tool calls

**File:** `hooks/claude_read_gate.py`

**Execution flow:**

1. Read `module_map` from compliance_config.yaml
2. Get target file path from the tool call
3. Read `.claude/session_reads.json`:
   - If the file's timestamp is older than the current session start → wipe it (stale from prior/crashed session)
   - Check whether the CONTEXT file for the target file's module has been Read AND the structured confirmation line emitted
4. If not confirmed → output blocking message:

```
⛔ READ GATE: You are editing src/ingestion/loader.py but have not confirmed
reading CONTEXT_ingestion.md. Read the file and output:
CONTEXT READ: CONTEXT_ingestion.md | state: <phase> | last change: <date+desc> | open tasks: <N>
```

**Session state tracking:**
- A companion `PostToolUse` hook on `Read` calls appends the file path and timestamp to `.claude/session_reads.json`
- The PreToolUse gate checks both the reads list AND the confirmation pattern
- `.claude/session_reads.json` is in `.gitignore` — never persisted across sessions in version control

### Claude Code Hook 2: PostToolUse Advisory Scanner

**Triggers on:** `Edit`, `Write` tool calls

**File:** `hooks/claude_advisory_scan.py`

**Execution flow:**

1. Read `advisory.hardcoded_values.warn` patterns from compliance_config.yaml
2. Read the file that was just written/edited
3. Run each warn pattern against file content
4. If matches found → output non-blocking warnings:

```
⚠ ADVISORY: src/ingestion/loader.py
  Line 23: timeout = 30  → Possible hardcoded timeout
  Line 47: "claude-sonnet-4-20250514"  → Possible hardcoded model name

Review each warning. Fix the violation or DISMISS before your next tool call.
```

5. Also run `wc -l` and warn if approaching the limit:

```
⚠ LINE COUNT: src/ingestion/loader.py is 142 lines (limit: 150, 8 remaining)
```

**Dismissal flow:** The agent outputs a structured DISMISS line per CLAUDE.md Tier 2 rules. The hook appends each dismissal to `.claude/advisory_dismissals.json` with file, line, pattern, reason, and timestamp. The compliance monitor later verifies all dismissals meet `min_justification_length`.

### Claude Code Hook 3: Stop Compliance Monitor

**Triggers on:** `Stop` (session end)

**Execution flow:**

1. Run `git diff --name-only` to get files changed in the session
2. Collect full paths to compliance_config.yaml, CONTEXT.md, and all `ContextModuleDocumentation/CONTEXT_*.md` files
3. Collect `.claude/advisory_dismissals.json` if it exists
4. Spawn the compliance monitor agent with all inputs
5. Monitor writes JSON report to `.claude/last_compliance_report.json`
6. Monitor outputs human-readable summary to the conversation

---

## Design: Compliance Monitor Agent

**File:** `agents/compliance_monitor.md`

A read-only auditor agent spawned by the Stop hook. It receives changed files and project documentation, verifies consistency, and reports PASS/FAIL per check.

### Inputs

1. List of files changed in this session (from `git diff --name-only`)
2. Full content of compliance_config.yaml
3. Full content of CONTEXT.md
4. Full content of every `ContextModuleDocumentation/CONTEXT_*.md` file
5. Full content of `.claude/advisory_dismissals.json` (if it exists)

### Checks

**CHECK 1: file_registration**
For every source file under `source_dirs`: verify it appears in CONTEXT.md Architecture & File Map, identify its module via `module_map`, verify it appears in that module's CONTEXT_*.md. For files in the git diff (newly created): flag if missing from either.
- PASS: all source files registered in both locations
- FAIL: list each unregistered file and where it's missing

**CHECK 2: line_count_accuracy**
For every file listed in any CONTEXT file's Architecture & File Map: run `wc -l`, compare to documented count. Tolerance: 0 lines.
- PASS: all counts match
- FAIL: list each mismatch with file, documented count, actual count, and which CONTEXT file

**CHECK 3: interface_contracts**
Read the Interface Contracts table in CONTEXT.md. For each row: verify producer and consumer files exist on disk, grep each for the filename pattern as a signal that the contract is implemented. **This is a signal check, not proof** — dynamically constructed filenames won't match a literal grep, and pattern matches in comments/docstrings are false positives.
- PASS: all contracts have signals present
- WARNING: pattern not found in producer/consumer — may be dynamically constructed
- FAIL: producer or consumer file does not exist on disk

**CHECK 4: version_incremented**
For every .md file in the git diff: read current version, read version from last commit via `git show HEAD:<filepath>`. If the file was modified (not newly created), verify the version increased. **If HEAD doesn't exist** (new repo, no prior commits): SKIP this check with note "no prior commit to compare against."
- PASS: all modified .md files have bumped versions
- FAIL: list each file with unchanged version
- SKIP: no prior commit exists

**CHECK 5: removed_files_cleaned**
For every file path referenced in any CONTEXT file's Architecture & File Map: check if the file exists on disk.
- PASS: no references to non-existent files
- FAIL: file absent from disk AND not in current session's git diff as a deletion (stale reference)
- WARNING: file expected to exist only at runtime (generated/output files explicitly marked as such)

**CHECK 6: advisory_dismissals_reviewed**
Read `.claude/advisory_dismissals.json`. For each entry: verify `reason` field exists and is at least `min_justification_length` characters (from compliance_config.yaml, default 20). Does NOT evaluate whether the reason is correct.
- PASS: all dismissals have valid justifications
- FAIL: list each dismissal with missing or too-short justification
- SKIP: no dismissals file exists

### Report Format

JSON written to `.claude/last_compliance_report.json`:

```json
{
  "timestamp": "2026-04-05T14:30:00Z",
  "session_files_changed": ["src/ingestion/loader.py"],
  "checks": {
    "file_registration": {
      "status": "PASS|FAIL",
      "details": []
    },
    "line_count_accuracy": {
      "status": "PASS|FAIL",
      "details": [
        {
          "file": "src/ingestion/loader.py",
          "documented": 89,
          "actual": 94,
          "context_file": "CONTEXT_ingestion.md"
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

Human-readable summary also output to conversation:

```
COMPLIANCE REPORT — 2026-04-05
===============================
✓ PASS  file_registration: all 3 new files registered
✗ FAIL  line_count_accuracy: CONTEXT_ingestion.md lists loader.py as 89 lines, actual 94
✓ PASS  interface_contracts: all filenames match
✓ PASS  version_incremented: 2 .md files touched, both bumped
✓ PASS  removed_files_cleaned: no stale references
— SKIP  advisory_dismissals_reviewed: no dismissals this session

1 issue to resolve before marking work complete.
```

### Constraints

- Read-only. Does not modify any files.
- Does not suggest fixes. Reports facts only.
- Runs all six checks regardless of earlier failures.
- If a CONTEXT file is malformed or unparseable: report FAIL on the relevant check with "could not parse" as the detail.
- If compliance_config.yaml is missing or unparseable: report all checks as FAIL with "missing compliance_config.yaml."

---

## Design: setup.sh

**File:** `setup.sh` at template root

### Execution Flow

**1. Check prerequisites:**
- Python 3.x available
- Git repo initialized (`.git/` exists)
- `yq` available (offer to skip — fallback parser works without it)

**2. Copy template files to project root:**
- CLAUDE.md, CONTEXT.md, CONTEXT_MODULE.md
- compliance_config.yaml
- agents/compliance_monitor.md
- hooks/ (all hook scripts)

**3. Create directories:**
- `ContextModuleDocumentation/`
- `plans/`
- `docs/superpowers/specs/`
- `.claude/`

**4. Git hook installation (safe):**
- Check if `.git/hooks/pre-commit` exists
- **If YES** — print: "Existing pre-commit hook found at .git/hooks/pre-commit" and offer three options:
  1. **Chain:** rename existing to `pre-commit.local`, install new hook that runs `pre-commit.local` first, then template checks
  2. **Append:** add template checks to end of existing hook
  3. **Skip:** don't install git hook, print manual instructions
- **If NO** — install `hooks/pre-commit` to `.git/hooks/pre-commit`, `chmod +x`
- Print confirmation of what was installed

**5. Claude Code settings:**
- Check if `.claude/settings.json` exists
- Merge hook configuration into existing settings (don't overwrite other settings)
- Print what was added

**6. Update .gitignore (safe):**
- For each of these entries, check if already present before appending:
  - `.claude/session_reads.json`
  - `.claude/advisory_dismissals.json`
  - `.claude/last_compliance_report.json`

**7. Print summary:**
- Files created
- Hooks installed
- Next steps: "Fill in CLAUDE.md placeholders, then run your first session"

---

## File Inventory

| File | Purpose | New/Modified |
|------|---------|:---:|
| `CLAUDE.md` | Tiered project rules | Modified |
| `CONTEXT.md` | Expanded living snapshot with TOC | Modified |
| `CONTEXT_MODULE.md` | Template + version table + annotated checklist | Modified |
| `compliance_config.yaml` | Machine-readable policy | New |
| `agents/compliance_monitor.md` | Compliance auditor agent definition | New |
| `hooks/pre-commit` | Git pre-commit hard gate | New |
| `hooks/parse_config.py` | YAML parser fallback for shell hooks | New |
| `hooks/claude_read_gate.py` | PreToolUse read confirmation gate | New |
| `hooks/claude_advisory_scan.py` | PostToolUse advisory warning scanner | New |
| `setup.sh` | Project setup with safe hook installation | New |

Total: 3 modified files, 7 new files.

---

## Implementation Priority

1. **Restructured templates** (CLAUDE.md, CONTEXT.md, CONTEXT_MODULE.md) — everything else references them
2. **compliance_config.yaml** — hooks read from it, must exist first
3. **Git pre-commit hook + parse_config.py** — highest ROI, catches the most common violations immediately
4. **Claude Code hooks** (read gate, advisory scanner) — mid-session feedback
5. **Compliance monitor agent** — end-of-session semantic audit
6. **setup.sh** — ties everything together for new projects
