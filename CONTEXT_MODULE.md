# ContextModuleDocumentation/CONTEXT_[MODULE].md

Version: 1.0.0

---

## Module Summary

<!-- One paragraph. What this module does, what it owns, and what it does NOT do (boundaries). -->

The `[module]` module (`src/[package]/[module]/`) [what it manages/provides]. It provides [component A], [component B], and [component C].

---

## Current Module State

<!-- One of: planning | in-progress | stable | deprecated -->

**[State]** — [One sentence: e.g. "Initial implementation complete with full test coverage." or "Actively being refactored — do not rely on public API."]

---

## Recent Changes

<!-- Bulleted log. Keep last 5-10 entries. Oldest roll off. Include the file changed, not just the feature. -->

- **YYYY-MM-DD:** `[filename].py` — [What changed and why]
- **YYYY-MM-DD:** `[filename].py` — [What changed and why]
- **YYYY-MM-DD:** Created module. Design spec at `docs/superpowers/specs/[spec].md`.

---

## Pending Tasks

<!-- In priority order. Remove items when complete; don't let this become a graveyard. -->

- [Task 1]
- [Task 2]
- [Task 3]

---

## Architecture & File Map

<!-- Every file in the module. Line counts must match reality — update after every change. -->

```
src/[package]/[module]/
├── __init__.py      ([N] lines)  — Re-exports: [list public symbols]
├── models.py        ([N] lines)  — [What dataclasses/models live here]
├── [file].py        ([N] lines)  — [What this file is responsible for]
└── [file].py        ([N] lines)  — [What this file is responsible for]

tests/
├── test_[file].py   ([N] lines)  — [N] tests for [what]
└── test_[file].py   ([N] lines)  — [N] tests for [what]
```

Total: [N] lines across [N] files.

---

## Key Decisions & Notes

<!-- Decisions and constraints specific to this module. Anything a new session needs to know before touching this code. -->

- **[Decision title]** — [What was decided and why. Include rejected alternatives if useful.]
- **[Decision title]** — [What was decided and why.]
- **[External dependency]** — [What library is used, why, and any known quirks or constraints.]
- **[Default behavior]** — [What defaults exist and what callers must override in production.]

---

## Module Change Checklist

Run this checklist after every change to this module. Do not skip items.

- [ ] **Line counts** — Update every file's line count in the Architecture & File Map above (`wc -l` each file)
- [ ] **New files** — If you created a new file: add it to the File Map above, add it to `CONTEXT.md` Architecture & File Map, and ensure it has the `Area/PRD/NOTE` header
- [ ] **Removed files** — If you deleted a file: remove it from the File Map above and from `CONTEXT.md`
- [ ] **Split files** — If you split a file: update the original's line count, add the new file(s) everywhere, update imports in consumers
- [ ] **Interface changes** — If filenames or output formats changed: update the Interface Contracts table in `CONTEXT.md`
- [ ] **Version bump** — Increment this file's version (patch for line-count fixes, minor for new files or behavior changes)
- [ ] **Recent Changes** — Add a dated bullet to the Recent Changes section above
