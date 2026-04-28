# 0001 — Cut Script Registry from `docs/SCRIPT_PURPOSES.md`

Version: 1.0.0

Status: accepted
Date: 2026-04-27

## Context

The template formerly shipped `templates/SCRIPT_PURPOSES.md` with two sections: a `Deliverable → Code Provenance` map (forward index from a finding/screen/endpoint to the producing script) and a `Script Registry` (per-file inventory: line count, public symbols, one-line purpose, what each file backs).

The Script Registry duplicated information already authoritative elsewhere:

- Line counts: `CONTEXT.md` Architecture & File Map and per-module `CONTEXT_*.md` File Maps.
- Public symbols: source code function and class signatures.
- One-line purposes: per-module `CONTEXT_*.md` and module docstrings.

Triple-bookkeeping created two failure modes:

1. The compliance monitor audited CONTEXT files (CHECK 1, 2, 5) but not `SCRIPT_PURPOSES.md`, so Script Registry drift went silently uncaught.
2. Hand-updating three places on every refactor invited skipped updates.

## Decision

Cut the Script Registry section. Rename the file to `docs/DELIVERABLE_PROVENANCE.md` to signal the change. Wire the surviving `Deliverable → Code Provenance` map into a new compliance check (CHECK 7 `provenance_integrity`).

## Alternatives considered

- **Wire SCRIPT_PURPOSES.md into compliance unchanged** — would mechanically enforce the duplication rather than eliminate it. Audit catches drift but bookkeeping cost stays.
- **Auto-generate the Script Registry from source via AST** — would automate the redundant half (Script Registry) while leaving the unique half (Deliverable Provenance) hand-maintained. Solves a less valuable problem.
- **Keep a stripped Script Registry** (file → `Backs:` only, no line counts/symbols/purpose) — the `Backs:` field is derivable from the forward index by grep; convenience-only, not unique value.

## Consequences

**Becomes harder:**
- Reverse-direction queries ("what report content does this file back?") require grepping the provenance map rather than reading a per-file row.
- Adding a new source file no longer auto-registers in `SCRIPT_PURPOSES.md`; it registers in CONTEXT files only (which the existing CHECK 1 already enforces).

**Becomes easier:**
- Line counts and public symbols live in one place (CONTEXT files) instead of three.
- The provenance map is small enough that hand-maintenance is realistic.
- The new audit (CHECK 7) is a tighter, more meaningful check than "every source file is registered in three places."

## If you find yourself wanting to do X, look at Y

This ADR exists to prevent re-introduction of the Script Registry. Below are the needs that Script Registry was answering, and where to satisfy them now:

- **"What scripts exist in this project?"** → `CONTEXT.md` § Architecture & File Map (project-level) or `ContextModuleDocumentation/CONTEXT_<module>.md` § Architecture & File Map (module-level). These are mechanically audited (line counts, registration).
- **"What does this script do?"** → The module's `CONTEXT_*.md` (one-line description in the File Map) or the source file's docstring / Area-PRD-NOTE header.
- **"What public symbols does this file export?"** → The source file's module docstring (top-of-file summary of public API) and `ContextModuleDocumentation/CONTEXT_<module>.md` § Architecture & File Map (one-line per-file description). Function and class signatures in the source itself are the authoritative reference; any standalone table duplicating them goes stale.
- **"Where is this script tested?"** → Grep `tests/` for the file's basename, or check the module's `ContextModuleDocumentation/CONTEXT_<module>.md` § Architecture & File Map (the file map lists test files alongside source files in the same module). If you want a permanent index, that belongs in the module's CONTEXT file, not in a new top-level registry.
- **"What changed about this script recently, and why?"** → `git log --follow <path>` for commits; the module's `ContextModuleDocumentation/CONTEXT_<module>.md` § Recent Changes block for human-written rationale on the changes that warranted explanation. The git history is the authoritative log; CONTEXT files annotate.
- **"What report content (or screen / endpoint / library function) depends on this script?"** → Grep the `ID` column of `docs/DELIVERABLE_PROVENANCE.md` or the `Producing script(s)` column for the file path. This is the reverse-direction query the Script Registry tried to serve directly; the grep is fast and the answer is current.
- **"Did the new file I added land in all the right places?"** → The Stop-hook compliance monitor reports CHECK 1 (file registration in CONTEXT files), CHECK 7 (provenance integrity). If both pass, the file is correctly wired.

**This redirect block is intended to be living.** Adding new redirects when a new genuine need emerges is welcome and does NOT require a superseding ADR — append a bullet, commit. Only structural changes — removing a redirect, repointing one at a different artifact, or revisiting the underlying decision (cutting Script Registry) — require a new ADR per § Supersede protocol in `decisions/README.md`.

If you find a need that is not on this list and you are tempted to reintroduce a per-file registry to satisfy it, **write a new ADR superseding this one** rather than editing this file or quietly re-creating the structure.
