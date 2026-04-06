# CONTEXT.md

Version: 1.0.0

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

## Module Context Files

<!-- Mirror of the table in CLAUDE.md. Keep both in sync. -->

| File | Module | Status |
|------|--------|--------|
| `CONTEXT_[module1].md` | [Module 1] | planning |
| `CONTEXT_[module2].md` | [Module 2] | planning |

---

## Architecture & File Map

<!-- Every file in the project with line counts. Update after every change. -->

```
project/
├── CLAUDE.md                           # project rules
├── CONTEXT.md                          # this file — living project snapshot
├── CONTEXT_MODULE.md                   # template for new context files
├── ContextModuleDocumentation/
│   ├── CONTEXT_[module1].md           # [module 1] state
│   └── CONTEXT_[module2].md           # [module 2] state
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

<!-- Every file produced by one module and consumed by another. This is the single source of truth for filenames and formats. -->

| Producer | Output Location | Filename Pattern | Consumed By |
|----------|----------------|------------------|-------------|
| `[producer].py` | `[output/dir/]` | `[filename].csv` | `[consumer].py` |
| `[producer].py` | `[output/dir/]` | `[filename].json` | end user |

**Rules:**
- If you change a filename pattern, update this table AND every consumer listed in the "Consumed By" column.
- If you build a new consumer, verify the suffix you use against this table before writing code.

---

## Key Project Decisions

<!-- Decisions that affect the whole project, not just one module. Module-specific decisions go in CONTEXT_*.md files. -->

- **[Decision]** — [What was decided and why]
- **[Decision]** — [What was decided and why]
