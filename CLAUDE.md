# CLAUDE.md

**IMPORTANT: Read this entire file before making ANY code changes.**

Version: 1.0.0

---

## Project Overview

<!-- Replace with your project description. 2-3 sentences: what it does, who it's for, what tech stack. -->

[PROJECT_NAME] is a [brief description]. It [what it does] using [key technologies].

**Design spec:** `docs/superpowers/specs/YYYY-MM-DD-[project]-design.md`

---

## Subagent Rules

Every subagent working on this project MUST:

1. Read this entire CLAUDE.md before making ANY changes
2. Read `CONTEXT.md` for project state — including the **Interface Contracts** table
3. Read the `ContextModuleDocumentation/CONTEXT_*.md` for the module being worked on
4. **Cross-reference dependencies** — When your module consumes or references output from another module, read that module's CONTEXT file to verify filenames, formats, and schemas. Never guess at filenames or suffixes; always confirm against the producing module's documentation and the Interface Contracts table in CONTEXT.md.
5. If creating a new module, create its `CONTEXT_*.md` first using the template at `CONTEXT_MODULE.md`
6. Follow all Development Principles below
7. As the FINAL task before completion, re-read this CLAUDE.md and run the Pre-Completion Compliance Checklist
8. Do not report work as complete until all checklist items pass

---

## Terminology

<!-- Define project-specific terms that Claude or subagents need to understand. -->

- **Term 1** — Definition
- **Term 2** — Definition
- **Term 3** — Definition

---

## Architecture Layers

<!-- Describe your system's layers. Adjust the number of layers to your project. -->

- **Layer 1 — [Name]:** [What it does]
- **Layer 2 — [Name]:** [What it does]
- **Layer 3 — [Name]:** [What it does]

**Rules:**
- [Rule about what belongs in which layer]
- [Rule about data flow between layers]

---

## Key Data Flow

<!-- Show the end-to-end data pipeline. Use ASCII art or a simple diagram. -->

```
Input → Processing → Output
```

---

## Development Principles

1. **Modularity** — Small, focused modules with single, clear responsibilities. If a module needs a long explanation of what it does, it does too much.

2. **Check existing code first** — Before implementing any function, search the codebase for an existing implementation. Never duplicate logic.

3. **Reuse before writing** — Wire into existing functions and modules. New code is a last resort, not a first instinct.

4. **TDD** — Write the test first. Then write the minimum code to make it pass. No untested code ships. Must be 100% TDD. DO NOT stop TDD prematurely. 

5. **150-line file limit** — All source files must stay under 150 lines. If a file exceeds this, refactor or split it before committing.

6. **No hardcoded values** — Never hardcode secrets, credentials, file paths, URLs, API endpoints, model names, numeric thresholds, timeouts, or converter names in source code. Every such value must come from a config file, an environment variable, or a function parameter with a documented default.

7. **File headers** — Every source file must open with:
   ```python
   # Area: <Module Name>
   # PRD: plans/<plan-filename>.md
   # NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
   ```

8. **Keep CONTEXT files current** — After every meaningful change to code, config, or docs, update the relevant `ContextModuleDocumentation/CONTEXT_*.md` file. An outdated CONTEXT file is worse than none.

9. **Read before touching** — Before working on any module, read the `ContextModuleDocumentation/CONTEXT_*.md` file for that module. Do not rely on memory or assumptions from a prior session.

10. **Recommend session splits** — If a task is too large for one session, say so and propose a split before starting.

11. **Register every new file** — When creating a new source file (including splits/extractions from existing files), immediately:
    - Add the `Area/PRD/NOTE` header
    - Add it to the module's `CONTEXT_*.md` Architecture & File Map (with line count)
    - Add it to `CONTEXT.md` Architecture & File Map (with line count)
    - Add it to the Interface Contracts table in `CONTEXT.md` if it produces or consumes files
    - If it's a new module with no CONTEXT file, create one from `CONTEXT_MODULE.md` and add it to both the CLAUDE.md and CONTEXT.md Module Context Files tables

---

## Module Context Files

<!-- List all CONTEXT files. Add rows as you create new modules. -->

| File | Module | Covers |
|------|--------|--------|
| `CONTEXT_[module1].md` | [Module 1] | [Brief description] |
| `CONTEXT_[module2].md` | [Module 2] | [Brief description] |

### When to read which file

- Working on [module 1] → read `CONTEXT_[module1].md`
- Working on [module 2] → read `CONTEXT_[module2].md`

---

## Documentation & Versioning

1. **Semantic versions everywhere** — Every `.md` doc (README, plans, CONTEXT files) must have a version at the top (e.g. `Version: 1.0.0`).

2. **Plan per module** — Each module has its own plan in `plans/`. Modules map to one or more source files.

3. **Sync on change** — When code changes, update the corresponding plan: increment the version, update content, update any affected sections.

4. **Exact function signatures in plans** — Copy-paste signatures from source. Never paraphrase. Include all parameters and defaults.

5. **Line count accuracy** — After any file modification, verify and update line counts in the corresponding plan and CONTEXT file.

6. **Plan mapping completeness** — Every source file whose header references a plan must appear in that plan's File Mapping table.

---

## CONTEXT.md Maintenance

Each `ContextModuleDocumentation/CONTEXT_*.md` is the **living snapshot** of its module. It is what a subagent or new session reads *first* to understand a module's current state.

### Required Sections

1. **Module Summary** — What the module does and its core purpose.
2. **Current State** — Phase: `planning` / `in-progress` / `stable` / `deprecated`.
3. **Recent Changes** — Bulleted log of the last 5-10 meaningful changes with dates. Oldest roll off as new ones are added.
4. **Pending Tasks** — What still needs to be done, in priority order. Strike through completed items; remove them next session.
5. **Architecture & File Map** — Directory tree with line counts and one-line description per file.
6. **Key Decisions & Notes** — Design decisions, open questions, and constraints future sessions must know.

### When to Update

- After any code, config, or doc change in that module
- After adding or removing files
- At the end of every session, even if only to update "Current State"

### Module Change Checklist

Every CONTEXT file includes a Module Change Checklist at the bottom (see `CONTEXT_MODULE.md` template). **Run it after every change to the module.** The checklist covers line counts, new/removed/split files, interface changes, and version bumps. Do not mark a task complete without running the checklist for every module you touched.

### Rules

- Bullet points and tables over prose — keep it scannable
- Version it like every other doc
- This file is for **module state**; development rules live here in CLAUDE.md

---

## Project Structure

<!-- Replace with your actual directory tree. Keep it current. -->

```
project/
├── CLAUDE.md                           # this file — project rules
├── CONTEXT.md                          # living project snapshot
├── CONTEXT_MODULE.md                   # template for new context files
├── ContextModuleDocumentation/         # one CONTEXT_*.md per module
├── plans/                              # implementation plans
├── docs/superpowers/specs/             # design specs
├── src/                                # source code
│   ├── config/
│   │   └── config.yaml                # all paths & settings
│   ├── [module1]/                     # module 1 files
│   └── [module2]/                     # module 2 files
├── scripts/                            # standalone utility scripts
└── tests/                              # test suite
```

---

## Testing

- **Framework:** pytest
- **Location:** `tests/`
- **Coverage:** Every source module must have a corresponding test file
- **Run:** `pytest tests/` from project root
- **TDD required:** Write test first, then implementation

---

## Pre-Completion Compliance Checklist

Before marking any task complete, all of the following must be true:

**Code quality:**
- [ ] All tests pass (`pytest tests/`)
- [ ] All source files are under 150 lines
- [ ] No hardcoded values introduced
- [ ] Every source file has the `Area/PRD/NOTE` header pointing to a valid plan

**File accounting (run after ANY file creation, split, or rename):**
- [ ] Every source file appears in `CONTEXT.md` Architecture & File Map with correct line count
- [ ] Every test file appears in `CONTEXT.md` Architecture & File Map with correct line count
- [ ] Every script file appears in `CONTEXT.md` Architecture & File Map with correct line count
- [ ] Every source file appears in its module's `CONTEXT_*.md` Architecture & File Map with correct line count
- [ ] Every `CONTEXT_*.md` file appears in both the CLAUDE.md and CONTEXT.md Module Context Files tables

**Documentation sync:**
- [ ] Every `.md` file has a semantic version
- [ ] Every source file referencing a plan appears in that plan's mapping table
- [ ] Line counts in plans match actual file lengths
- [ ] All filenames/suffixes for consumed outputs match the Interface Contracts table in CONTEXT.md
- [ ] Relevant `ContextModuleDocumentation/CONTEXT_*.md` files updated (version incremented)
- [ ] Relevant plan versions incremented and content synced
- [ ] `CONTEXT.md` updated if project-level state changed
