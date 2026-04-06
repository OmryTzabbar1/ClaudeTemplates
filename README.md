# Claude Project Documentation Templates

Version: 1.0.0

Templates for structuring a project so Claude Code (and its subagents) can work effectively across multiple sessions.

## Files

| File | Purpose | Where to put it |
|------|---------|----------------|
| `CLAUDE.md` | Project rules, development principles, compliance checklist | Project root |
| `CONTEXT.md` | Living project snapshot — state, file map, interface contracts | Project root |
| `CONTEXT_MODULE.md` | Template for per-module context files | Project root |

## Setup

1. Copy all three files to your project root
2. Fill in `CLAUDE.md`:
   - Replace `[PROJECT_NAME]` and all `[placeholders]` with your project details
   - Customize Development Principles (e.g., change 150-line limit, file header format)
   - Add your project's terminology
   - Draw your architecture layers and data flow
   - Fill in the project structure tree
3. Fill in `CONTEXT.md`:
   - Write the project summary
   - Set up phase summary table
   - Create the initial Architecture & File Map
4. Create `ContextModuleDocumentation/` directory
5. As you add modules, copy `CONTEXT_MODULE.md` to `ContextModuleDocumentation/CONTEXT_[module].md` and fill it in

## How It Works

**CLAUDE.md** is the constitution — rules that never change within a session. It tells every agent:
- What the project is
- How to write code (principles)
- Where to find things (structure)
- What to check before reporting done (compliance checklist)

**CONTEXT.md** is the living state — updated after every meaningful change. It tells every agent:
- What phase the project is in
- What changed recently
- Where every file is (with line counts)
- How files connect (interface contracts)

**CONTEXT_MODULE.md** files are per-module snapshots. A subagent reads the relevant one before touching any code in that module.

## Key Principles

- **CONTEXT files are the first thing read** — they're the entry point for any session or subagent
- **Interface Contracts prevent bugs** — when Module A produces `output.csv` and Module B consumes it, both must agree on the filename. The table in CONTEXT.md is the single source of truth.
- **Line counts catch drift** — if a file's line count doesn't match, something changed without updating docs
- **The compliance checklist is mandatory** — it's the last thing run before any task is marked done
- **Versions track change** — every `.md` file has a semantic version. Increment on every edit.

## Customization

These templates are opinionated (150-line limit, TDD, file headers). Adjust to your project:

- **Line limit**: Change `150` in CLAUDE.md to whatever fits your project
- **File headers**: Change the header format in Development Principles
- **Testing framework**: Change `pytest` references if using another framework
- **Config approach**: Change `config.yaml` references if using env vars, `.env`, etc.
- **Language**: Templates assume Python but work for any language — just adjust the header format and test commands
