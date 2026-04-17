# [PROJECT_NAME]

Version: 0.1.0

<!--
This is the FRONT-DOOR README template for downstream projects scaffolded
from ClaudeTemplates. It is NOT this template repo's own README. Copy
this file to your new project as `README.md` and fill in the bracketed
fields.

Update triggers (per CONTEXT.md § README.md Maintenance): project phase
or status, tech stack, repo layout, getting-started steps, or module list.
Routine intra-module work does NOT require a README touch.
-->

[ONE-SENTENCE PITCH — what the project does and for whom.]

> Optional callout — working title, name-availability notes, audience caveats, etc.

---

## Status

**Phase: [planning | scaffolding | in-progress | stable].** [One sentence on what's currently runnable and what's still aspirational.]

| Phase | Status |
|---|---|
| [Phase 1] | [Not started / In progress / Complete] |
| [Phase 2] | [Not started / In progress / Complete] |
| [Phase 3] | [Not started / In progress / Complete] |
| [Phase 4] | [Not started / In progress / Complete] |

---

## Tech Stack

- **Language:** [e.g., Python 3.12, TypeScript 5.x, C# / Unity 6 (`6000.4.1f1`)]
- **Framework / runtime:** [e.g., FastAPI, Next.js, Unity 6 hybrid ECS]
- **Data layer:** [e.g., Postgres, ScriptableObjects, Firestore]
- **Other notable dependencies:** [list 2-4 high-impact libs/services]

See [`docs/superpowers/specs/[YYYY-MM-DD]-[design-spec].md`](docs/superpowers/specs/) for the full design.

---

## Repository Layout

```
[src or Assets]/
  [module1]/         [one-line description]
  [module2]/         [one-line description]

ContextModuleDocumentation/   Per-module CONTEXT_*.md (read first before
                              touching a module)

docs/superpowers/
  specs/    Design specifications
  plans/    Implementation plans (one per feature)

hooks/                 Pre-commit gate + Claude Code tool-use hooks
compliance_config.yaml Policy definitions consumed by hooks
CLAUDE.md              Project rules (TDD, 150-line cap, file headers, etc.)
CONTEXT.md             Architecture, terminology, module index, file map
```

Module-by-module file maps and recent-change logs live in [`ContextModuleDocumentation/`](ContextModuleDocumentation/).

---

## Development Conventions

This codebase enforces a small set of hard rules. **Read [`CLAUDE.md`](CLAUDE.md) before making changes** — pre-commit hooks block violations.

- **TDD.** Every source file with logic has a corresponding test file. Write the test first.
- **150-line cap** on source files (test files exempt). Refactor or split before committing.
- **No hardcoded values.** Numeric thresholds, paths, URLs, model names, etc. come from a config file, environment variable, or function parameter with a documented default.
- **File header** required on every source file (Area / PRD / NOTE).
- **CONTEXT files are the source of truth** for module state. Update the relevant `CONTEXT_*.md` after every meaningful change and bump its semantic version.

Before working on a module, read [`CONTEXT.md`](CONTEXT.md) and the module's `ContextModuleDocumentation/CONTEXT_<MODULE>.md`.

---

## Getting Started

1. [Install prerequisite — e.g., Python 3.12 / Node 20 / Unity Hub + Unity 6000.4.1f1].
2. Clone the repo and [open / cd into] the project root.
3. [One-line setup command — e.g., `pip install -e .`, `npm install`, "open the project in Unity Hub"].
4. [How to run the app/game/CLI — e.g., `pytest`, `npm run dev`, "open `Assets/Scenes/[scene].unity` and press Play"].
5. [How to run tests — e.g., `pytest tests/`, `npm test`, "Window → General → Test Runner"].

---

## Versioning

Every `.md` doc and `CONTEXT_*.md` carries a `Version: X.X.X`. Bump rules per file are listed in each doc's Version Decision Table.
