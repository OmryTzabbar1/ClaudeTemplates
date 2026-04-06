# ContextModuleDocumentation/CONTEXT_hooks.md

Version: 1.1.0

---

## Module Summary

The `hooks` module (`hooks/`) provides enforcement scripts for git pre-commit gates and Claude Code tool-use hooks. It owns the YAML config parser fallback (`parse_config.py`), the git pre-commit hard gate (`pre-commit`), and the Claude Code read gate and advisory scanner. It does NOT own policy definitions — those live in `compliance_config.yaml`.

---

## Current Module State

**in-progress** — `parse_config.py` implemented with full test coverage; remaining hooks pending.

---

## Recent Changes

- **2026-04-05:** `parse_config.py` — Created YAML dotted-key resolver for shell hook fallback (60 lines)
- **2026-04-05:** `tests/test_parse_config.py` — Created TDD test suite, 10 tests (88 lines)
- **2026-04-05:** Created module.

---

## Pending Tasks

- [ ] Create `hooks/pre-commit` (Task 6)
- [ ] Create `hooks/claude_read_gate.py` (Task 7)
- [ ] Create `hooks/claude_advisory_scan.py` (Task 8)

---

## Architecture & File Map

```
hooks/
├── parse_config.py      (60 lines)  — YAML dotted-key resolver; outputs shell-friendly values

tests/
└── test_parse_config.py (88 lines)  — 10 tests for parse_config.py
```

Total: 148 lines across 2 files.

---

## Key Decisions & Notes

- **Python fallback** — `parse_config.py` exists as a fallback for when `yq` is unavailable in the shell hook environment. Shell hook tries `yq` first, falls back to this script.
- **CWD dependency** — Script opens `compliance_config.yaml` relative to CWD. Must be invoked from project root (which git hooks always do).
- **List-of-dicts format** — When a YAML list contains dicts, outputs `key=value` pairs separated by `---` sentinel lines. Shell consumers must handle this format.
- **Exit code contract** — Exits 1 on missing key or usage error; exits 0 on success. Shell hooks rely on this to detect missing config keys.

---

## Version Decision Table

| Change type | Version bump |
|---|---|
| Line count correction only | patch |
| New file added to module | minor |
| File removed or renamed | minor |
| Module behavior/API changed | minor |
| Module removed or replaced | major |

---

## Module Change Checklist

Run this checklist after every change to this module. Do not skip items.

- [ ] **Line counts** — Update every file's line count in the Architecture & File Map above (`wc -l` each file)
- [ ] **New files** — If you created a new file: add it to the File Map above, add it to `CONTEXT.md` Architecture & File Map, and ensure it has the Area/PRD/NOTE header
- [ ] **Removed files** — If you deleted a file: remove it from the File Map above and from `CONTEXT.md`
- [ ] **Split files** — If you split a file: update the original's line count, add the new file(s) everywhere, update imports in consumers
- [ ] **Interface changes** — If filenames or output formats changed: update the Interface Contracts table in `CONTEXT.md`
- [ ] **Version bump** — Increment this file's version per the Version Decision Table above
- [ ] **Recent Changes** — Add a dated bullet to the Recent Changes section above
