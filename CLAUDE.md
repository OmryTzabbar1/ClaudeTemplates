# CLAUDE.md

**IMPORTANT: Read this entire file before making ANY code changes.**

Version: 2.1.0

---

## ⛔ TIER 1 — NON-NEGOTIABLE RULES

These rules are hard constraints. Violations are caught by hooks and block commits.

1. **TDD** — Write the test first. Then write the minimum code to make it pass. No untested code ships. No exceptions. Every source file that contains logic (classes, methods, functions) must have a corresponding test file. Do NOT skip tests for "thin wrappers." Do NOT skip tests because "the underlying class is already tested." Do NOT defer tests to "integration testing later." Do NOT create a source file without creating its test file in the same task. If a file is too simple to test meaningfully, write a trivial test — do not skip it. *Enforced by pre-commit hook.*

2. **150-line file limit** — All source files must stay under 150 lines. If a file exceeds this, refactor or split it before committing. *Enforced by pre-commit hook.*

3. **No hardcoded values** — Never hardcode secrets, credentials, file paths, URLs, API endpoints, model names, numeric thresholds, timeouts, or converter names in source code. Every such value must come from a config file, an environment variable, or a function parameter with a documented default. *Enforced by pre-commit hook.*

4. **File headers** — Every source file must open with an Area/PRD/NOTE header in the language's comment syntax. *Enforced by pre-commit hook.*

   | Language | Syntax |
   |----------|--------|
   | Python, Shell, Ruby, YAML | `# Area: ...` / `# PRD: ...` / `# NOTE: ...` |
   | JS, TS, Go, Rust, Java, C, C# | `// Area: ...` / `// PRD: ...` / `// NOTE: ...` |
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

### TDD in Plans

Do NOT write implementation plans where any task creates a source file without a corresponding test file. Do NOT use "thin wrapper," "trivial delegation," "already tested via X," or "will be integration-tested" as justification for omitting tests from a plan task. Every task that creates a source file must also create or update a test file in the same task. If a file genuinely cannot be tested (e.g., Unity Gizmos rendering with no callable API), the plan must explicitly state "UNTESTABLE: [reason]" — and this must be reviewed and approved before implementation begins.

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
