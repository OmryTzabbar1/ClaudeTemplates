# Deliverable Provenance Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `templates/SCRIPT_PURPOSES.md` with a parser-audited `templates/DELIVERABLE_PROVENANCE.md` system in the ClaudeTemplates repo, mechanically enforced by a new `compliance_monitor` CHECK 7 that compares parser-detected element IDs in each project's deliverable against rows in the provenance map.

**Architecture:** A new `parsers/` directory houses one-sentence-interface parser modules (`parse(str) -> list[str]` plus `VERSION`); a new `hooks/run_provenance_check.py` runner emits structured JSON; `agents/compliance_monitor.md` gains CHECK 7 that shells out to the runner. A new `decisions/` directory holds ADRs; ADR-0001 records why the Script Registry was cut and answers the needs it was serving. `setup.sh` detects existing `docs/SCRIPT_PURPOSES.md` and migrates conservatively (rename + strip Script Registry section) with `--dry-run` and abort-on-customization safety.

**Tech Stack:** Python 3 (pytest), YAML config, markdown, shell. No new external dependencies.

**Spec:** `docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md` (v1.2.0)

**Out of scope (covered by separate plans):**
- Backport to the EO14173 project (separate brainstorm + plan after this template work stabilizes)
- Template self-test (`tests/test_template_meta.py`)

---

## Session Scope Assessment

- **Modules touched:** `parsers/` (new), `hooks/`, `agents/`, `decisions/` (new), `templates/`, top-level docs
- **Files created/modified:** ~17 (8 new files, 9 modifications)
- **Reversible if incomplete:** Yes through Task 19. Tasks 20-22 (setup.sh integration test + version bumps) are reversible via git.
- **Estimated completion confidence:** medium. Multi-phase work with parser ↔ runner ↔ agent integration; failure modes are spec'd but the cross-component glue is the risky part.
- **Split recommended:** No. Eight-artifact scope per spec § Components is single-plan-sized; phases 1-3 are independently testable, which limits blast radius.
- **Justification:** Every component has a test path or dry-run path before integration.

---

## Plan-Level Verification (run before declaring done)

- [ ] `pytest tests/` passes from the ClaudeTemplates repo root (all new tests + the existing `test_parse_config.py`)
- [ ] `python3 hooks/run_provenance_check.py --self-check` runs the audit against a synthetic fixture and exits 0
- [ ] `bash setup.sh --dry-run` invoked in a scratch directory containing a synthetic `docs/SCRIPT_PURPOSES.md` prints the expected migration diff and exits 0 without touching files
- [ ] `bash setup.sh` (interactive run) on the same scratch fixture migrates the file and confirms the result on disk
- [ ] ADR-0001 user-review checkpoint passed (Task 2)
- [ ] Every modified `.md` file has its version bumped per its own decision table (CLAUDE.md, CONTEXT.md, CONTEXT_MODULE.md, README.md, ContextModuleDocumentation/CONTEXT_hooks.md, templates/PROJECT_README.md)
- [ ] Compliance monitor (Stop hook) self-runs cleanly on the post-implementation repo state

---

## File Structure

**New files (8):**

| Path | Responsibility |
|---|---|
| `decisions/README.md` | ADR discipline (numbering, status field, supersede protocol) |
| `decisions/0001-cut-script-registry.md` | Rationale for cutting Script Registry + redirect block answering needs it served |
| `parsers/__init__.py` | Parser interface contract (declarative; no logic) |
| `parsers/narrative_md.py` | First parser. Detects `<!-- id: ... -->` markers in markdown. |
| `parsers/CHANGELOG.md` | Per-parser version history (single shared file, see spec § Parser versioning) |
| `hooks/provenance_io.py` | Markdown table parsing + parser-module loading + version-prefix enforcement |
| `hooks/run_provenance_check.py` | CHECK 7 entrypoint: validates inventory, runs forward + reverse direction, emits JSON |
| `templates/DELIVERABLE_PROVENANCE.md` | Replaces `templates/SCRIPT_PURPOSES.md`. Single section: `Deliverable → Code Provenance` table. |

**New test files (3):**

| Path | Tests |
|---|---|
| `tests/test_narrative_md_parser.py` | `parsers/narrative_md.py` happy path + edge cases + contract |
| `tests/test_provenance_io.py` | `hooks/provenance_io.py` markdown parsing + parser loading |
| `tests/test_run_provenance_check.py` | `hooks/run_provenance_check.py` end-to-end audit on fixtures |

**Modified files (9):**

| Path | Change |
|---|---|
| `templates/SCRIPT_PURPOSES.md` | DELETE (replaced by `templates/DELIVERABLE_PROVENANCE.md`) |
| `compliance_config.yaml` | ADD: `deliverable_inventory:`, `compliance_monitor.provenance_strict:`, `compliance_monitor.checks` adds `provenance_integrity` |
| `agents/compliance_monitor.md` | ADD: CHECK 7 spec + new Inputs lines for `docs/DELIVERABLE_PROVENANCE.md`, `parsers/`, the runner script |
| `setup.sh` | ADD: migration block, copy `decisions/`, copy `parsers/`, copy `hooks/run_provenance_check.py` + `hooks/provenance_io.py` |
| `CLAUDE.md` | UPDATE: Tier 2 "Register every new file" rewrite; Pre-Completion Checklist Advisory tier rewrite. Bump 2.3.0 → 2.4.0. |
| `CONTEXT_MODULE.md` | UPDATE: Module Change Checklist item rewrite. Bump per its own table. |
| `README.md` | UPDATE: New section "Parser-based provenance audit." Bump version. |
| `templates/PROJECT_README.md` | UPDATE: Replace any `SCRIPT_PURPOSES.md` reference with `DELIVERABLE_PROVENANCE.md`. Bump version. |
| `CONTEXT.md` | UPDATE: Architecture & File Map adds new files; Recent Changes; Module Context Files unchanged. Bump version. |
| `ContextModuleDocumentation/CONTEXT_hooks.md` | UPDATE: File Map adds `run_provenance_check.py` + `provenance_io.py`. Bump version. |

---

## Task 1: Create `decisions/` directory + ADR README

**Files:**
- Create: `decisions/README.md`

The `decisions/` directory was created by an earlier mkdir but is empty. This task populates the discipline doc.

- [ ] **Step 1: Write `decisions/README.md`**

Path: `decisions/README.md`. Content:

```markdown
# Architecture Decision Records (ADRs)

Version: 1.0.0

This directory holds load-bearing structural decisions made about the template. Each ADR captures **what was decided, why, and what was rejected**. The `Recent Changes` blocks in CONTEXT files capture *what* changed; ADRs capture *why and what alternatives were considered*.

## Numbering

Zero-padded sequential: `0001-cut-script-registry.md`, `0002-…`, `0003-…`. Never reuse a number.

## Status field

Every ADR has a `Status:` line in its header. Allowed values:

- `proposed` — under discussion, not yet load-bearing
- `accepted` — load-bearing; future work conforms to it
- `superseded by NNNN` — replaced by a later ADR; do not edit accepted ADRs in place

## Supersede protocol

To revise an accepted ADR:

1. Write a new ADR with a new number that explains the change.
2. Update the original ADR's `Status:` line to `superseded by NNNN`.
3. Add a `Superseded by:` link at the top of the original.
4. Do not edit the original's body — its purpose is to record what was thought at the time.

## When to write an ADR

Write an ADR when a decision:

- changes a load-bearing structural choice (file layout, audit shape, naming convention used across projects)
- forecloses an option that future-you might otherwise reintroduce
- depends on a tradeoff that is not visible from the code

A bug fix is not an ADR. A refactor is not an ADR. A choice between two options where one is obviously better is not an ADR.

## ADR template

Each ADR contains:

- `# Title — what was decided` (one line)
- `Status: <value>`, `Date: YYYY-MM-DD`
- `## Context` — what problem prompted this decision
- `## Decision` — what was decided
- `## Alternatives considered` — what was rejected and why
- `## Consequences` — what becomes harder, what becomes easier
- `## If you find yourself wanting to do X, look at Y` — the redirect block. Especially important for "we removed X" decisions.
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add decisions/README.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: add decisions/README.md — ADR discipline doc

Numbering, status field, supersede protocol, ADR template. First in
the new decisions/ directory referenced by the deliverable provenance
audit spec."
```

---

## Task 2: Write ADR-0001 (cut Script Registry) + user-review checkpoint

**Files:**
- Create: `decisions/0001-cut-script-registry.md`

The redirect block is the most-likely-to-rot part of this artifact. Per the spec brainstorm, this task includes an explicit user-review checkpoint before completion.

- [ ] **Step 1: Write `decisions/0001-cut-script-registry.md`**

```markdown
# 0001 — Cut Script Registry from `docs/SCRIPT_PURPOSES.md`

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
- **"What public symbols does this file export?"** → Read the source file. Function and class signatures are the authoritative reference; any duplication into a markdown table is by definition stale.
- **"What report content (or screen / endpoint / library function) depends on this script?"** → Grep the `ID` column of `docs/DELIVERABLE_PROVENANCE.md` or the `Producing script(s)` column for the file path. This is the reverse-direction query the Script Registry tried to serve directly; the grep is fast and the answer is current.
- **"Did the new file I added land in all the right places?"** → The Stop-hook compliance monitor reports CHECK 1 (file registration in CONTEXT files), CHECK 7 (provenance integrity). If both pass, the file is correctly wired.

If you find a need that is not on this list and you are tempted to reintroduce a per-file registry to satisfy it, **write a new ADR superseding this one** rather than editing this file or quietly re-creating the structure.
```

- [ ] **Step 2: Pause for user review**

Before committing, post the file path to the user and ask for review of the redirect block specifically (it is the highest-risk-of-being-wrong part):

> "ADR-0001 drafted at `decisions/0001-cut-script-registry.md`. Please review the **'If you find yourself wanting to do X, look at Y'** block — five entries cover the needs Script Registry was serving. Tell me if a real need is missing or a redirect points at the wrong place. Reply 'approved' to commit."

Wait for explicit user approval before Step 3.

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add decisions/0001-cut-script-registry.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: ADR-0001 — cut Script Registry; redirect block

First ADR in decisions/. Records what was decided, what was rejected
(wire-unchanged, AST-generation, stripped-registry), what becomes
harder and easier, and answers each need that Script Registry was
serving with a redirect to the surviving artifact.

User-reviewed redirect block before commit."
```

---

## Task 3: Create `parsers/__init__.py` (interface contract, declarative)

**Files:**
- Create: `parsers/__init__.py`

Per CLAUDE.md the `__init__.py` re-export carveout applies; this file is declarative (docstring + nothing) and has no dedicated test. The contract enforcement test goes in Task 4 alongside the first parser.

- [ ] **Step 1: Write `parsers/__init__.py`**

```python
# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Parser interface contract for the deliverable provenance audit (CHECK 7).

Each parser module under `parsers/` (or `parsers/local/`) MUST export:

    VERSION: str
        Semver string. Local parsers MUST use a `local-` prefix
        (e.g. `local-1.0.0`); canonical parsers MUST NOT.

    def parse(file_contents: str) -> list[str]:
        Return the list of stable ElementIDs found in the file.
        IDs are flat (no namespace prefix) — the audit applies the
        `<key>:` prefix in namespaced mode.

The contract is intentionally one signature, one return type. Parsers
that need richer output are the wrong abstraction; split into
multiple parsers or extend the audit, do not extend this interface.
"""
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add parsers/__init__.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: parsers/__init__.py — interface contract docstring

Declarative only. Contract is parse(str) -> list[str] + VERSION
constant; local parsers must use a local- VERSION prefix. No logic
in this file; tests live in tests/test_narrative_md_parser.py."
```

---

## Task 4: TDD `parsers/narrative_md.py` (happy path + contract)

**Files:**
- Create: `parsers/narrative_md.py`
- Create: `tests/test_narrative_md_parser.py`

- [ ] **Step 1: Write the failing test**

Path: `tests/test_narrative_md_parser.py`. Content:

```python
# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for parsers/narrative_md.py — markdown parser for HTML id comments."""
import pytest


def test_version_is_semver_without_local_prefix():
    """Canonical parsers must NOT have a `local-` VERSION prefix."""
    from parsers import narrative_md
    assert hasattr(narrative_md, "VERSION")
    assert isinstance(narrative_md.VERSION, str)
    assert not narrative_md.VERSION.startswith("local-")


def test_parse_signature():
    """Contract: parse(str) -> list[str]."""
    from parsers import narrative_md
    import inspect
    sig = inspect.signature(narrative_md.parse)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].annotation in (str, "str")


def test_parse_extracts_single_id():
    from parsers.narrative_md import parse
    text = "Some finding **value 42** <!-- id: p5-chi -->"
    assert parse(text) == ["p5-chi"]


def test_parse_extracts_multiple_ids_sorted_unique():
    from parsers.narrative_md import parse
    text = """
**A** <!-- id: zebra -->
**B** <!-- id: alpha -->
**C** <!-- id: alpha -->
**D** <!-- id: middle -->
"""
    assert parse(text) == ["alpha", "middle", "zebra"]


def test_parse_returns_empty_on_no_ids():
    from parsers.narrative_md import parse
    assert parse("Plain markdown with no id markers.") == []


def test_parse_handles_whitespace_variants():
    from parsers.narrative_md import parse
    text = """
<!--id:no-spaces-->
<!--   id:   extra-spaces   -->
<!-- id: kebab-case -->
"""
    assert parse(text) == ["extra-spaces", "kebab-case", "no-spaces"]


def test_parse_ignores_malformed_markers():
    """Markers without `id:` prefix or with invalid chars must not match."""
    from parsers.narrative_md import parse
    text = """
<!-- not an id: foo -->
<!-- id: has space -->
<!-- id: has/slash -->
<!-- id: ok-id -->
"""
    assert parse(text) == ["ok-id"]


def test_parse_handles_uppercase_html_comment_label():
    """Spec uses lowercase `id:`. Uppercase ID: should NOT match (would be a different parser)."""
    from parsers.narrative_md import parse
    text = "<!-- ID: should-not-match -->"
    assert parse(text) == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_narrative_md_parser.py -v
```

Expected: All eight tests FAIL with `ModuleNotFoundError: No module named 'parsers.narrative_md'` (or similar import error).

- [ ] **Step 3: Implement minimal parser**

Path: `parsers/narrative_md.py`. Content:

```python
# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""narrative_md — HTML id-comment parser for markdown deliverables.

Detects markers of the form `<!-- id: <stable-id> -->` (case-sensitive
on the `id:` label). Returns a sorted, deduplicated list of IDs.
"""
import re

VERSION = "1.0.0"

_ID_PATTERN = re.compile(r"<!--\s*id:\s*([A-Za-z0-9_-]+)\s*-->")


def parse(file_contents: str) -> list[str]:
    """Return sorted unique list of IDs detected in `file_contents`."""
    return sorted(set(_ID_PATTERN.findall(file_contents)))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_narrative_md_parser.py -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add parsers/narrative_md.py tests/test_narrative_md_parser.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: parsers/narrative_md.py — HTML id-comment parser

Detects <!-- id: <stable-id> --> markers in markdown. Case-sensitive
on label, tolerant of whitespace, ignores malformed markers. VERSION
1.0.0. Eight tests covering happy path, sort/dedup, edge cases."
```

---

## Task 5: Create `parsers/CHANGELOG.md`

**Files:**
- Create: `parsers/CHANGELOG.md`

Per spec § Parser versioning, a single shared CHANGELOG (not per-parser) is the discoverability choice.

- [ ] **Step 1: Write `parsers/CHANGELOG.md`**

```markdown
# Parser Changelog

Version: 1.0.0

Per-parser version history. One section per parser, ordered by parser name. Entries within a section ordered newest-first.

When updating a parser's `VERSION`, add an entry here in the same commit. The bump rule (MAJOR / MINOR / PATCH) is in the spec — see `docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md` § Parser versioning protocol.

## narrative_md

### 1.0.0 — 2026-04-27

Initial. Detects `<!-- id: <stable-id> -->` markers in markdown via regex `<!--\s*id:\s*([A-Za-z0-9_-]+)\s*-->`. Returns sorted unique list of IDs.
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add parsers/CHANGELOG.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "docs: parsers/CHANGELOG.md — initial entry for narrative_md 1.0.0

Single shared CHANGELOG per spec § Parser versioning. Future parser
version bumps add entries here in the same commit as the VERSION
constant change."
```

---

## Task 6: TDD `hooks/provenance_io.py` — markdown table row parser

**Files:**
- Create: `hooks/provenance_io.py`
- Create: `tests/test_provenance_io.py`

`provenance_io.py` houses two responsibilities: parsing the DELIVERABLE_PROVENANCE.md table to extract IDs and `path:symbol` cells, and loading parser modules. Task 6 covers the markdown half; Task 7 covers parser loading.

- [ ] **Step 1: Write the failing test**

Path: `tests/test_provenance_io.py`. Content:

```python
# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for hooks/provenance_io.py — provenance markdown parsing + parser loading."""
import pytest


SIMPLE_PROVENANCE = """\
# DELIVERABLE_PROVENANCE.md

Some intro prose.

## Deliverable → Code Provenance

| ID         | Deliverable element              | Producing script(s)                               |
| ---------- | -------------------------------- | ------------------------------------------------- |
| p5-chi     | P5 chi-square test               | src/propositions/p5_oliver.py:_chi_square         |
| fig2       | Figure 2 — sector × ban CIs      | src/descriptives/figures.py:fig2_sector_by_ban    |
| p1-ame     | P1 AME (sector × ban) = 0.1802   | src/propositions/p1_coercive.py:run, src/propositions/utils.py:compute_ames |
"""


def test_parse_provenance_extracts_ids_in_order():
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    assert [r.id for r in rows] == ["p5-chi", "fig2", "p1-ame"]


def test_parse_provenance_extracts_script_paths():
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    p1 = next(r for r in rows if r.id == "p1-ame")
    assert "src/propositions/p1_coercive.py" in p1.script_paths
    assert "src/propositions/utils.py" in p1.script_paths


def test_parse_provenance_skips_header_separator_row():
    """The | --- | --- | row must not become a Row object."""
    from hooks.provenance_io import parse_provenance
    rows = parse_provenance(SIMPLE_PROVENANCE)
    assert all(r.id not in ("---", "----------") for r in rows)
    assert len(rows) == 3


def test_parse_provenance_returns_empty_when_no_table():
    from hooks.provenance_io import parse_provenance
    text = "# Title\n\nNo table here.\n"
    assert parse_provenance(text) == []


def test_parse_provenance_detects_duplicate_ids():
    from hooks.provenance_io import parse_provenance, DuplicateIDError
    text = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | A                   | src/a.py            |
| foo | B                   | src/b.py            |
"""
    with pytest.raises(DuplicateIDError) as exc:
        parse_provenance(text)
    assert "foo" in str(exc.value)


def test_parse_provenance_flags_empty_id():
    from hooks.provenance_io import parse_provenance, MalformedRowError
    text = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
|     | element with empty ID | src/a.py |
"""
    with pytest.raises(MalformedRowError):
        parse_provenance(text)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_provenance_io.py -v
```

Expected: All six tests FAIL with `ModuleNotFoundError: No module named 'hooks.provenance_io'`.

- [ ] **Step 3: Implement minimal markdown parser**

Path: `hooks/provenance_io.py`. Content:

```python
# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""provenance_io — parse DELIVERABLE_PROVENANCE.md tables and load parser modules.

Two responsibilities: (1) extract structured rows from the provenance
markdown table, (2) load and validate parser modules from `parsers/`
and `parsers/local/`. Failure modes are spec'd in the design doc;
this module raises typed exceptions the runner converts to JSON.
"""
from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path


class ProvenanceError(Exception):
    """Base for provenance-parsing errors."""


class DuplicateIDError(ProvenanceError):
    """Raised when DELIVERABLE_PROVENANCE.md contains duplicate IDs."""


class MalformedRowError(ProvenanceError):
    """Raised when a row is missing its ID column or has empty ID."""


class ParserLoadError(ProvenanceError):
    """Raised on parser module load / interface contract violation."""


@dataclass(frozen=True)
class Row:
    id: str
    element: str
    script_paths: tuple[str, ...]


_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")
_SEPARATOR_CELL = re.compile(r"^[-:\s]+$")


def parse_provenance(text: str) -> list[Row]:
    """Extract rows from any pipe-table found in `text`.

    Header row is detected by `ID` in the first cell (case-insensitive).
    The separator row (e.g. `| --- | --- |`) is skipped.
    """
    rows: list[Row] = []
    in_table = False
    seen_ids: set[str] = set()

    for line in text.splitlines():
        m = _TABLE_ROW.match(line)
        if not m:
            in_table = False
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if all(_SEPARATOR_CELL.match(c) for c in cells):
            continue
        if not in_table:
            if cells and cells[0].strip().lower() == "id":
                in_table = True
            continue
        if len(cells) < 3:
            raise MalformedRowError(f"Row has fewer than 3 cells: {line!r}")
        rid, element, scripts_cell = cells[0], cells[1], cells[2]
        if not rid:
            raise MalformedRowError(f"Empty ID in row with element: {element!r}")
        if rid in seen_ids:
            raise DuplicateIDError(f"Duplicate ID: {rid!r}")
        seen_ids.add(rid)
        paths = tuple(p.strip().split(":")[0] for p in scripts_cell.split(",") if p.strip())
        rows.append(Row(id=rid, element=element, script_paths=paths))
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_provenance_io.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/provenance_io.py tests/test_provenance_io.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: hooks/provenance_io.py — markdown table row parser

Extracts (id, element, script_paths) tuples from DELIVERABLE_PROVENANCE.md
pipe-tables. Detects header row by 'ID' cell, skips separator row,
raises DuplicateIDError / MalformedRowError on shape violations.
Six tests covering header detection, sort, duplicates, malformed rows."
```

---

## Task 7: TDD `hooks/provenance_io.py` — parser module loader

**Files:**
- Modify: `hooks/provenance_io.py` (add `load_parser` + version-prefix enforcement)
- Modify: `tests/test_provenance_io.py` (add load_parser tests)

- [ ] **Step 1: Write the failing tests (append to test file)**

Append to `tests/test_provenance_io.py`:

```python
def test_load_parser_finds_canonical(tmp_path, monkeypatch):
    """Canonical parser loads when VERSION lacks 'local-' prefix."""
    pkg = tmp_path / "parsers"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "1.0.0"\n'
        'def parse(s: str) -> list[str]: return ["x"]\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser
    mod = load_parser("demo")
    assert mod.VERSION == "1.0.0"
    assert mod.parse("anything") == ["x"]


def test_load_parser_rejects_canonical_with_local_prefix(tmp_path, monkeypatch):
    pkg = tmp_path / "parsers"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "local-1.0.0"\n'
        'def parse(s: str) -> list[str]: return []\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("demo")
    assert "must not use a `local-`" in str(exc.value)


def test_load_parser_local_must_have_prefix(tmp_path, monkeypatch):
    pkg = tmp_path / "parsers" / "local"
    pkg.mkdir(parents=True)
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (pkg / "__init__.py").write_text("")
    (pkg / "demo.py").write_text(
        'VERSION = "1.0.0"\n'  # missing local- prefix
        'def parse(s: str) -> list[str]: return []\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("demo")
    assert "must use a `local-`" in str(exc.value)


def test_load_parser_local_shadows_canonical(tmp_path, monkeypatch):
    """parsers/local/<n>.py takes precedence on collision."""
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'VERSION = "1.0.0"\n'
        'def parse(s): return ["canonical"]\n'
    )
    (tmp_path / "parsers" / "local").mkdir()
    (tmp_path / "parsers" / "local" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "local" / "demo.py").write_text(
        'VERSION = "local-1.0.0"\n'
        'def parse(s): return ["local"]\n'
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser
    mod = load_parser("demo")
    assert mod.parse("") == ["local"]


def test_load_parser_missing_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError) as exc:
        load_parser("nope")
    assert "unknown parser" in str(exc.value).lower()


def test_load_parser_missing_VERSION_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'def parse(s): return []\n'  # no VERSION
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError):
        load_parser("demo")


def test_load_parser_missing_parse_raises(tmp_path, monkeypatch):
    (tmp_path / "parsers").mkdir()
    (tmp_path / "parsers" / "__init__.py").write_text("")
    (tmp_path / "parsers" / "demo.py").write_text(
        'VERSION = "1.0.0"\n'  # no parse
    )
    monkeypatch.chdir(tmp_path)

    from hooks.provenance_io import load_parser, ParserLoadError
    with pytest.raises(ParserLoadError):
        load_parser("demo")
```

- [ ] **Step 2: Run tests to verify failures**

```bash
pytest tests/test_provenance_io.py -v -k load_parser
```

Expected: 7 FAIL with `ImportError: cannot import name 'load_parser' from 'hooks.provenance_io'`.

- [ ] **Step 3: Append `load_parser` to `hooks/provenance_io.py`**

Add to the end of `hooks/provenance_io.py`:

```python
def load_parser(name: str):
    """Resolve and load a parser by name. Local parsers shadow canonical.

    Raises ParserLoadError on:
      - unknown parser (neither parsers/<name>.py nor parsers/local/<name>.py exists)
      - missing VERSION or parse symbols
      - VERSION/path inconsistency (canonical with local- prefix or vice versa)
    """
    cwd = Path.cwd()
    local_path = cwd / "parsers" / "local" / f"{name}.py"
    canonical_path = cwd / "parsers" / f"{name}.py"

    if local_path.exists():
        path = local_path
        is_local = True
    elif canonical_path.exists():
        path = canonical_path
        is_local = False
    else:
        available = []
        if (cwd / "parsers").exists():
            available += sorted(p.stem for p in (cwd / "parsers").glob("*.py") if p.stem != "__init__")
        if (cwd / "parsers" / "local").exists():
            available += sorted(f"local/{p.stem}" for p in (cwd / "parsers" / "local").glob("*.py") if p.stem != "__init__")
        raise ParserLoadError(f"unknown parser: {name!r}. Available: {available}")

    spec = importlib.util.spec_from_file_location(f"_loaded_parser_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not hasattr(mod, "VERSION"):
        raise ParserLoadError(f"parser {name!r} at {path} is missing `VERSION`")
    if not hasattr(mod, "parse"):
        raise ParserLoadError(f"parser {name!r} at {path} is missing `parse`")

    has_local_prefix = isinstance(mod.VERSION, str) and mod.VERSION.startswith("local-")
    if is_local and not has_local_prefix:
        raise ParserLoadError(
            f"parsers/local/{name}.py must use a `local-`-prefixed VERSION (e.g. local-1.0.0); got {mod.VERSION!r}"
        )
    if (not is_local) and has_local_prefix:
        raise ParserLoadError(
            f"parsers/{name}.py must not use a `local-` VERSION (canonical parsers); got {mod.VERSION!r}"
        )
    return mod
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_provenance_io.py -v
```

Expected: 13 passed (6 from Task 6 + 7 new).

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/provenance_io.py tests/test_provenance_io.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: hooks/provenance_io.py — load_parser with local- prefix enforcement

Resolves parsers/<n>.py and parsers/local/<n>.py with local shadowing.
Enforces the v1.1.0 spec rule: canonical parsers must not use local-
VERSION prefix; local parsers must. Surfaces silent-fork risk in the
parser_version config field. Seven tests covering shadowing, version
prefix mismatch, missing VERSION/parse, unknown parser."
```

---

## Task 8: TDD `hooks/run_provenance_check.py` — main entrypoint + inventory validation

**Files:**
- Create: `hooks/run_provenance_check.py`
- Create: `tests/test_run_provenance_check.py`

The runner is a CLI that reads `compliance_config.yaml`, runs the audit, and emits JSON. Task 8 covers config loading + inventory shape validation.

- [ ] **Step 1: Write the failing tests**

Path: `tests/test_run_provenance_check.py`. Content:

```python
# Area: Tests
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Tests for hooks/run_provenance_check.py — CHECK 7 audit runner."""
import json
import subprocess
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent.parent  # ClaudeTemplates root
RUNNER = HERE / "hooks" / "run_provenance_check.py"


def _run(cwd, *args):
    """Invoke runner; return (rc, parsed_json)."""
    result = subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=cwd, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, payload, result.stderr


def _fixture_repo(tmp_path, *, config_yaml="", provenance_md=None, parsers=None):
    """Create a minimal repo layout for the runner."""
    (tmp_path / "compliance_config.yaml").write_text(config_yaml)
    if provenance_md is not None:
        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "docs" / "DELIVERABLE_PROVENANCE.md").write_text(provenance_md)
    if parsers:
        (tmp_path / "parsers").mkdir(exist_ok=True)
        (tmp_path / "parsers" / "__init__.py").write_text("")
        for name, content in parsers.items():
            (tmp_path / "parsers" / f"{name}.py").write_text(content)
    return tmp_path


def test_runner_skips_when_no_inventory(tmp_path):
    cfg = """
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg)
    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "SKIP"
    assert "no deliverable_inventory" in payload["reason"].lower()


def test_runner_fails_on_mixed_key_inventory(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "key" in payload["details"][0].lower()
    assert "all-or-nothing" in payload["details"][0].lower()


def test_runner_fails_on_multi_entry_no_key(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "namespace" in payload["details"][0].lower() or "key" in payload["details"][0].lower()


def test_runner_fails_on_duplicate_keys(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: same
  - path: b.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: same
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "duplicate" in payload["details"][0].lower()


def test_runner_fails_on_missing_parser_version(tmp_path):
    cfg = """
deliverable_inventory:
  - path: a.md
    parser: narrative_md
compliance_monitor:
  provenance_strict: false
"""
    _fixture_repo(tmp_path, config_yaml=cfg, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["status"] == "FAIL"
    assert "parser_version" in payload["details"][0].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 5 FAIL with FileNotFoundError on the runner script.

- [ ] **Step 3: Implement minimal runner**

Path: `hooks/run_provenance_check.py`. Content:

```python
#!/usr/bin/env python3
# Area: Hooks
# PRD: docs/superpowers/plans/2026-04-27-deliverable-provenance-audit.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""run_provenance_check — CHECK 7 audit runner.

Reads compliance_config.yaml, validates the deliverable_inventory shape,
runs forward and reverse direction audits, emits a JSON report on stdout.
Exit code 0 on PASS / SKIP, non-zero on FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make hooks/ importable so we can pull in provenance_io
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hooks import provenance_io  # noqa: E402


def _load_config():
    """Minimal YAML loader using the existing parse_config fallback."""
    from hooks import parse_config
    cfg_path = Path.cwd() / "compliance_config.yaml"
    if not cfg_path.exists():
        return {}
    return parse_config.load_yaml(str(cfg_path))


def _validate_inventory(inv):
    """Return list of FAIL detail strings; empty list = valid."""
    fails: list[str] = []
    if not inv:
        return fails
    has_key = [bool(e.get("key")) for e in inv]
    if any(has_key) and not all(has_key):
        fails.append("`key` must be all-or-nothing across deliverable_inventory entries.")
    if not any(has_key) and len(inv) >= 2:
        fails.append("≥2 deliverable_inventory entries require `key` to namespace IDs.")
    keys = [e.get("key") for e in inv if e.get("key")]
    if len(keys) != len(set(keys)):
        dups = sorted({k for k in keys if keys.count(k) > 1})
        fails.append(f"duplicate `key` values: {dups}")
    for e in inv:
        if "parser_version" not in e or not e.get("parser_version"):
            fails.append(f"entry for path={e.get('path')!r} missing required `parser_version`")
    return fails


def main(argv: list[str]) -> int:
    cfg = _load_config()
    inv = cfg.get("deliverable_inventory") or []
    if not inv:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "SKIP",
            "reason": "no deliverable_inventory configured",
        }))
        return 0
    fails = _validate_inventory(inv)
    if fails:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": fails,
        }))
        return 1
    # forward + reverse direction implemented in Tasks 9-10
    print(json.dumps({
        "check": "provenance_integrity",
        "status": "PASS",
        "reason": "inventory validated; full audit pending Tasks 9-10",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/run_provenance_check.py tests/test_run_provenance_check.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: hooks/run_provenance_check.py — entrypoint + inventory validation

CHECK 7 runner. Reads compliance_config.yaml, validates
deliverable_inventory shape (mixed key, multi-entry no-key, duplicate
keys, missing parser_version) and emits JSON. Exit 0 on PASS/SKIP.
Forward + reverse direction in subsequent tasks. Five tests on shape
validation."
```

---

## Task 9: TDD `run_provenance_check.py` — forward direction

**Files:**
- Modify: `hooks/run_provenance_check.py` (add forward direction)
- Modify: `tests/test_run_provenance_check.py` (add forward tests)

- [ ] **Step 1: Append forward-direction tests**

Append to `tests/test_run_provenance_check.py`:

```python
def test_runner_forward_passes_when_all_paths_exist(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/a.py            |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return []\n'
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    # forward passes (path exists), reverse passes (foo detected, foo provenanced)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["forward"]["status"] == "PASS"


def test_runner_forward_warns_on_missing_path_non_strict(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/missing.py      |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return ["foo"]\n'
    })
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0  # WARN does not fail in non-strict mode
    assert payload["forward"]["status"] == "WARN"
    assert any("src/missing.py" in d for d in payload["forward"]["details"])


def test_runner_forward_fails_on_missing_path_strict(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: true
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/missing.py      |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): return ["foo"]\n'
    })
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["forward"]["status"] == "FAIL"
```

- [ ] **Step 2: Run tests to verify failure**

```bash
pytest tests/test_run_provenance_check.py -v -k forward
```

Expected: 3 FAIL — runner does not yet emit `forward` field.

- [ ] **Step 3: Add forward-direction logic to `run_provenance_check.py`**

Replace the post-validation section of `main()` (the part after `fails = _validate_inventory(inv)` and the early-return PASS) with:

```python
    strict = bool(cfg.get("compliance_monitor", {}).get("provenance_strict", False))
    prov_path = Path.cwd() / "docs" / "DELIVERABLE_PROVENANCE.md"
    if not prov_path.exists():
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": [f"docs/DELIVERABLE_PROVENANCE.md missing but deliverable_inventory is set"],
        }))
        return 1
    try:
        rows = provenance_io.parse_provenance(prov_path.read_text())
    except provenance_io.ProvenanceError as e:
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "FAIL",
            "details": [f"DELIVERABLE_PROVENANCE.md: {type(e).__name__}: {e}"],
        }))
        return 1

    forward_warnings = []
    for row in rows:
        for path in row.script_paths:
            if not (Path.cwd() / path).exists():
                forward_warnings.append(f"row {row.id!r}: script path {path!r} does not exist")
    forward = {
        "status": "PASS" if not forward_warnings else ("FAIL" if strict else "WARN"),
        "details": forward_warnings,
    }

    overall_fail = forward["status"] == "FAIL"
    payload = {
        "check": "provenance_integrity",
        "status": "FAIL" if overall_fail else "PASS",
        "forward": forward,
        "rows_seen": len(rows),
    }
    print(json.dumps(payload))
    return 1 if overall_fail else 0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 8 passed (5 from Task 8 + 3 new).

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/run_provenance_check.py tests/test_run_provenance_check.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: forward direction — verify Provenance script paths exist

WARN by default; FAIL if compliance_monitor.provenance_strict is true.
Reads docs/DELIVERABLE_PROVENANCE.md, parses rows via provenance_io,
checks each path:symbol entry. Three tests covering pass / warn / strict-fail."
```

---

## Task 10: TDD `run_provenance_check.py` — reverse direction (flat mode)

**Files:**
- Modify: `hooks/run_provenance_check.py` (add reverse direction, flat-only)
- Modify: `tests/test_run_provenance_check.py` (add reverse-flat tests)

- [ ] **Step 1: Append reverse-flat tests**

Append to `tests/test_run_provenance_check.py`:

```python
def test_runner_reverse_passes_when_ids_align(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/a.py            |
| bar | B                   | src/a.py            |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): import re; return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n'
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n<!-- id: bar -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["reverse"]["status"] == "PASS"
    assert payload["reverse"]["count_detected"] == 2
    assert payload["reverse"]["count_provenance"] == 2


def test_runner_reverse_warns_on_forward_miss(tmp_path):
    """Detected ID with no Provenance row → WARN (FAIL in strict)."""
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/a.py            |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): import re; return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n'
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n<!-- id: orphan -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["reverse"]["status"] == "WARN"
    assert "orphan" in str(payload["reverse"]["forward_misses"])


def test_runner_reverse_warns_on_reverse_miss(tmp_path):
    """Provenance row with no detected ID → WARN."""
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID    | Deliverable element | Producing script(s) |
| ----- | ------------------- | ------------------- |
| foo   | F                   | src/a.py            |
| stale | S                   | src/a.py            |
"""
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": 'VERSION = "1.0.0"\ndef parse(s): import re; return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n'
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["reverse"]["status"] == "WARN"
    assert "stale" in str(payload["reverse"]["reverse_misses"])


def test_runner_fails_when_parser_returns_colon(tmp_path):
    """Spec § Failure modes: parser returning ':' in an ID → FAIL."""
    cfg = """
deliverable_inventory:
  - path: docs/d.md
    parser: narrative_md
    parser_version: "1.0.0"
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | F                   | src/a.py            |
"""
    # Parser stub deliberately returns a colon-containing ID
    bad_parser = 'VERSION = "1.0.0"\ndef parse(s): return ["bad:thing"]\n'
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={
        "narrative_md": bad_parser,
    })
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "d.md").write_text("\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("colon" in d.lower() or ":" in d for d in payload["reverse"]["details"])
```

- [ ] **Step 2: Run tests to verify failure**

```bash
pytest tests/test_run_provenance_check.py -v -k reverse
```

Expected: 4 FAIL — `reverse` field absent.

- [ ] **Step 3: Add reverse-direction (flat mode) logic**

In `hooks/run_provenance_check.py`, replace the section that emits `payload` with a fuller block. Insert before the `print(json.dumps(payload))` line:

```python
    # reverse direction (flat mode only — namespaced mode added in Task 11)
    namespaced = any(e.get("key") for e in inv)
    detected_all: set[str] = set()
    reverse_details: list[str] = []
    counts_detected_per_entry: list[int] = []

    for entry in inv:
        try:
            mod = provenance_io.load_parser(entry["parser"])
        except provenance_io.ParserLoadError as e:
            reverse_details.append(f"parser load failed for {entry['parser']!r}: {e}")
            continue
        if mod.VERSION != entry["parser_version"]:
            reverse_details.append(
                f"parser {entry['parser']!r} VERSION {mod.VERSION!r} != configured {entry['parser_version']!r} (WARN)"
            )
        target_path = Path.cwd() / entry["path"]
        if not target_path.exists():
            reverse_details.append(f"deliverable path {entry['path']!r} does not exist")
            counts_detected_per_entry.append(0)
            continue
        try:
            ids = mod.parse(target_path.read_text())
        except Exception as e:
            reverse_details.append(f"parser {entry['parser']!r} raised: {type(e).__name__}: {e}")
            counts_detected_per_entry.append(0)
            continue
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            reverse_details.append(f"parser {entry['parser']!r} returned non-list-of-str")
            counts_detected_per_entry.append(0)
            continue
        if any(":" in i for i in ids):
            colon_ids = [i for i in ids if ":" in i]
            reverse_details.append(
                f"parser {entry['parser']!r} returned IDs containing colon (forbidden): {colon_ids}"
            )
            counts_detected_per_entry.append(0)
            continue
        if namespaced:
            ids = [f"{entry['key']}:{i}" for i in ids]
        counts_detected_per_entry.append(len(ids))
        detected_all |= set(ids)

    provenance_ids = {row.id for row in rows}

    forward_misses = sorted(detected_all - provenance_ids)
    reverse_misses = sorted(provenance_ids - detected_all)

    if any(d for d in reverse_details if "load failed" in d or "raised" in d
           or "non-list-of-str" in d or "colon" in d.lower()
           or "does not exist" in d):
        reverse_status = "FAIL"
    elif forward_misses or reverse_misses:
        reverse_status = "FAIL" if strict else "WARN"
    else:
        reverse_status = "PASS"

    reverse = {
        "status": reverse_status,
        "details": reverse_details,
        "forward_misses": forward_misses,
        "reverse_misses": reverse_misses,
        "count_detected": sum(counts_detected_per_entry),
        "count_provenance": len(provenance_ids),
    }

    overall_fail = forward["status"] == "FAIL" or reverse["status"] == "FAIL"
    payload = {
        "check": "provenance_integrity",
        "status": "FAIL" if overall_fail else "PASS",
        "forward": forward,
        "reverse": reverse,
        "rows_seen": len(rows),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 12 passed (8 from Tasks 8-9 + 4 new).

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/run_provenance_check.py tests/test_run_provenance_check.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: reverse direction — flat mode + colon-in-ID FAIL

Loads parsers, runs parse(), compares detected IDs to Provenance
rows. Emits forward_misses / reverse_misses / count_detected /
count_provenance on every run. Parser-returns-':' is hard FAIL per
spec § Failure modes. Four tests covering align / forward miss /
reverse miss / colon FAIL."
```

---

## Task 11: TDD `run_provenance_check.py` — reverse direction (namespaced mode)

**Files:**
- Modify: `hooks/run_provenance_check.py` (validate Provenance ID shape in namespaced mode)
- Modify: `tests/test_run_provenance_check.py` (add namespaced tests)

- [ ] **Step 1: Append namespaced tests**

```python
def test_runner_namespaced_passes_when_keys_align(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
  - path: docs/dash.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: dash
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID            | Deliverable element | Producing script(s) |
| ------------- | ------------------- | ------------------- |
| paper:foo     | F in paper          | src/a.py            |
| dash:foo      | F in dash           | src/a.py            |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("<!-- id: foo -->\n")
    (tmp_path / "docs" / "dash.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["reverse"]["count_detected"] == 2
    assert payload["reverse"]["count_provenance"] == 2


def test_runner_namespaced_fails_on_flat_provenance_id(tmp_path):
    """Provenance row with flat ID in namespaced mode → FAIL."""
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID  | Deliverable element | Producing script(s) |
| --- | ------------------- | ------------------- |
| foo | flat ID in namespaced mode | src/a.py     |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("<!-- id: foo -->\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("flat" in d.lower() or "namespaced" in d.lower() for d in payload["reverse"]["details"])


def test_runner_namespaced_fails_on_unknown_key_prefix(tmp_path):
    cfg = """
deliverable_inventory:
  - path: docs/paper.md
    parser: narrative_md
    parser_version: "1.0.0"
    key: paper
compliance_monitor:
  provenance_strict: false
"""
    prov = """\
| ID            | Deliverable element        | Producing script(s) |
| ------------- | -------------------------- | ------------------- |
| ghost:foo     | row with unknown key prefix | src/a.py           |
"""
    parser_src = ('VERSION = "1.0.0"\nimport re\n'
                  'def parse(s): return sorted(set(re.findall(r"<!--\\s*id:\\s*([\\w-]+)\\s*-->", s)))\n')
    _fixture_repo(tmp_path, config_yaml=cfg, provenance_md=prov, parsers={"narrative_md": parser_src})
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("# stub\n")
    (tmp_path / "docs" / "paper.md").write_text("\n")

    rc, payload, _ = _run(tmp_path)
    assert rc != 0
    assert payload["reverse"]["status"] == "FAIL"
    assert any("ghost" in d for d in payload["reverse"]["details"])
```

- [ ] **Step 2: Run tests to verify failure**

```bash
pytest tests/test_run_provenance_check.py -v -k namespaced
```

Expected: 3 FAIL (the namespaced-mode validation logic doesn't exist yet — current implementation accepts any ID shape).

- [ ] **Step 3: Add namespaced-mode validation in `run_provenance_check.py`**

After computing `provenance_ids` and before the set diff, insert:

```python
    if namespaced:
        known_keys = {e["key"] for e in inv}
        for pid in provenance_ids:
            if ":" not in pid:
                reverse_details.append(
                    f"Provenance ID {pid!r} is flat but inventory is namespaced (must be <key>:<id>)"
                )
            else:
                prefix = pid.split(":", 1)[0]
                if prefix not in known_keys:
                    reverse_details.append(
                        f"Provenance ID {pid!r} uses unknown key {prefix!r}; known keys: {sorted(known_keys)}"
                    )
```

And update the `reverse_status` decision to also FAIL when these new details are present (the existing FAIL detection already catches "load failed" / "raised" / etc.; extend to catch `"flat but inventory is namespaced"` and `"unknown key"`):

```python
    fail_substrings = (
        "load failed", "raised", "non-list-of-str", "colon",
        "does not exist", "flat but inventory is namespaced", "unknown key",
    )
    if any(any(sub in d.lower() if sub == "colon" else sub in d for sub in fail_substrings) for d in reverse_details):
        reverse_status = "FAIL"
    elif forward_misses or reverse_misses:
        reverse_status = "FAIL" if strict else "WARN"
    else:
        reverse_status = "PASS"
```

(Replace the prior `if any(d for d in reverse_details if ...)` block.)

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 15 passed (12 from prior tasks + 3 new).

- [ ] **Step 5: Verify file is under 150 lines**

```bash
wc -l hooks/run_provenance_check.py
```

Expected: ≤ 150 (the file has grown across tasks 8-11; if over, refactor extracts before commit).

- [ ] **Step 6: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/run_provenance_check.py tests/test_run_provenance_check.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: namespaced mode — flat-in-namespaced and unknown-key validation

Provenance IDs in namespaced mode must use <key>:<id> form with key
matching a deliverable_inventory entry. Three tests covering pass /
flat-in-namespaced FAIL / unknown-key FAIL."
```

---

## Task 12: Add `--self-check` flag to runner

**Files:**
- Modify: `hooks/run_provenance_check.py`
- Modify: `tests/test_run_provenance_check.py`

`--self-check` runs the audit on a built-in synthetic fixture and exits 0. Used in plan-level verification + as a smoke test in setup.sh.

- [ ] **Step 1: Append self-check test**

```python
def test_runner_self_check_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc, payload, stderr = _run(tmp_path, "--self-check")
    assert rc == 0, f"self-check failed: {payload} / {stderr}"
    assert payload["status"] == "PASS"
    assert payload.get("mode") == "self-check"
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_run_provenance_check.py -v -k self_check
```

Expected: FAIL (flag not implemented).

- [ ] **Step 3: Add `--self-check` to `main()`**

At the top of `main()`, before `_load_config()`:

```python
    if argv and argv[0] == "--self-check":
        # Synthetic in-memory audit: verifies the runner can load a parser,
        # parse a markdown table, and compute set diffs without touching
        # the surrounding repo's config.
        synthetic_md = "<!-- id: alpha -->\n<!-- id: beta -->\n"
        synthetic_prov_text = (
            "| ID    | Deliverable element | Producing script(s) |\n"
            "| ----- | ------------------- | ------------------- |\n"
            "| alpha | A                   | __runner_self__     |\n"
            "| beta  | B                   | __runner_self__     |\n"
        )
        # Use narrative_md from the template's parsers/
        from parsers import narrative_md as _nm
        detected = set(_nm.parse(synthetic_md))
        prov_rows = provenance_io.parse_provenance(synthetic_prov_text)
        prov_ids = {r.id for r in prov_rows}
        ok = detected == prov_ids
        print(json.dumps({
            "check": "provenance_integrity",
            "status": "PASS" if ok else "FAIL",
            "mode": "self-check",
            "detected": sorted(detected),
            "provenance": sorted(prov_ids),
        }))
        return 0 if ok else 1
```

- [ ] **Step 4: Run tests to verify**

```bash
pytest tests/test_run_provenance_check.py -v
```

Expected: 16 passed.

- [ ] **Step 5: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add hooks/run_provenance_check.py tests/test_run_provenance_check.py
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: --self-check flag for runner smoke testing

Synthetic in-memory audit. Used by plan-level verification and as a
smoke test in setup.sh. Exit 0 on PASS."
```

---

## Task 13: Update `compliance_config.yaml` schema

**Files:**
- Modify: `compliance_config.yaml`

- [ ] **Step 1: Append new fields**

Open `compliance_config.yaml` and append to the `compliance_monitor:` block (near the existing `checks:`):

```yaml
  provenance_strict: false  # promote provenance_integrity WARN to FAIL when true
```

Append a new top-level optional block (commented out, since the template itself has no deliverable):

```yaml
# --- Deliverable provenance audit (CHECK 7) ---
# Set this in downstream projects to enable reverse-direction audit.
# See docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md
# deliverable_inventory:
#   - path: output/results_narrative.md
#     parser: narrative_md
#     parser_version: "1.0.0"
#     # key: paper  # required when ≥2 entries (all-or-nothing)
```

In the `compliance_monitor.checks:` list, append:

```yaml
    - id: "provenance_integrity"
      description: "DELIVERABLE_PROVENANCE.md rows align with parser-detected IDs in each deliverable; script paths exist"
```

- [ ] **Step 2: Verify YAML still parses**

```bash
python3 -c "import yaml; yaml.safe_load(open('compliance_config.yaml'))"
```

Expected: no output (success).

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add compliance_config.yaml
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: compliance_config.yaml — provenance_integrity check + schema

Adds deliverable_inventory block (commented; downstream projects
populate), compliance_monitor.provenance_strict flag, new
provenance_integrity check id."
```

---

## Task 14: Update `agents/compliance_monitor.md` with CHECK 7

**Files:**
- Modify: `agents/compliance_monitor.md`

- [ ] **Step 1: Add CHECK 7 spec**

Open `agents/compliance_monitor.md`. In the `## Inputs` section, append after item 5:

```markdown
6. The full content of `docs/DELIVERABLE_PROVENANCE.md` (if it exists)
7. JSON output of `python3 hooks/run_provenance_check.py` invoked from the project root
```

After CHECK 6 (`### CHECK 6: advisory_dismissals_reviewed`), insert:

```markdown
### CHECK 7: provenance_integrity

Run: `python3 hooks/run_provenance_check.py` from the project root. Parse the JSON output (single object on stdout).

The runner handles the entire audit (config validation, parser loading with `local-` prefix enforcement, forward direction, reverse direction with optional namespacing). This check just relays the runner's verdict.

**PASS:** runner exits 0 and emits `"status": "PASS"`.
**FAIL:** runner exits non-zero or emits `"status": "FAIL"`. Surface the `details` and the forward/reverse breakdowns. Always include `count_detected` and `count_provenance` from the `reverse` block in the report — drift between consecutive runs is itself information for the human reviewer.
**SKIP:** runner emits `"status": "SKIP"` (no `deliverable_inventory` configured). Note the SKIP reason in the report.

**What this audit does NOT catch** — print this list verbatim alongside any PASS/FAIL/SKIP result so consumers don't over-extend their trust:

- Wrong linkage (a row that points to the wrong script — both row and script exist, but the linkage is incorrect).
- Semantic drift (the row says "P5 chi-square" but the script now computes Fisher's exact).
- Silently dropped findings (a finding removed from the deliverable but kept in the Provenance map; only caught when reverse direction is enabled).
- Rephrased deliverable elements (text changes with stable IDs are intentionally not flagged).
- Incomplete parser coverage (a typo in an ID tag silently underreports; review `count_detected` against expectations).
```

In the `## Output` section, add a new entry under `checks` in the JSON template:

```json
    "provenance_integrity": {
      "status": "PASS|FAIL|SKIP",
      "details": []
    },
```

Add a corresponding line in the conversation-output ASCII block:

```
✓ PASS  provenance_integrity: {summary}
```

- [ ] **Step 2: Bump version**

Top of file: bump `Version: <prev>` to next minor.

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add agents/compliance_monitor.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: compliance_monitor — CHECK 7 provenance_integrity

Agent shells out to hooks/run_provenance_check.py and relays JSON
verdict. Includes 'What this audit does NOT catch' verbatim in
output per spec § What this audit does NOT catch."
```

---

## Task 15: Create `templates/DELIVERABLE_PROVENANCE.md` and remove `templates/SCRIPT_PURPOSES.md`

**Files:**
- Create: `templates/DELIVERABLE_PROVENANCE.md`
- Delete: `templates/SCRIPT_PURPOSES.md`

- [ ] **Step 1: Write `templates/DELIVERABLE_PROVENANCE.md`**

```markdown
# DELIVERABLE_PROVENANCE.md

Version: 1.0.0

<!--
EMPTY TEMPLATE. setup.sh copies this to `docs/DELIVERABLE_PROVENANCE.md`
in your downstream project. Populate the table as your codebase grows.

Purpose: durable bridge between the project's *reader-facing
deliverable* (a report, web app, API, library, game build, dashboard)
and the source code that produces it. CONTEXT files describe modules;
this file describes outputs and traces them back to scripts.

Maintenance is enforced by:
  - CLAUDE.md Tier 2 "Register every new file" rule
  - CLAUDE.md Pre-Completion Compliance Checklist (advisory)
  - `compliance_monitor` CHECK 7 (provenance_integrity)
  - Every `CONTEXT_<module>.md` Module Change Checklist

See decisions/0001-cut-script-registry.md for why this file replaced
the prior `SCRIPT_PURPOSES.md` (which had a Script Registry section).
-->

---

## What "deliverable" means in this project

[Edit this section before populating the table.] Examples of project deliverables:

- **Analysis report** — a hand-curated DOCX/PDF that quotes numbers from the pipeline
- **Web app** — pages and flows a user sees in production
- **Public API** — endpoints documented in an OpenAPI spec
- **Released library** — public functions in the package's docs
- **Game build** — scenes, mechanics, rules a player experiences
- **Dashboard** — visualisations rendered for an internal team

Deliverable location(s): [path / URL / build target]

If this project ships **multiple deliverables**, namespace IDs via the `key:` field on each `deliverable_inventory` entry in `compliance_config.yaml`. See the spec § Multi-deliverable ID namespacing.

---

## Deliverable → Code Provenance

Each row maps one identifiable element of the deliverable to the script(s) that produce it.

- **`ID` column**: stable identifier matching what the parser extracts from the deliverable. In flat mode (single-deliverable projects with no `key`), IDs are bare strings like `p5-chi`. In namespaced mode, IDs take the form `<key>:<id>` like `paper:p5-chi`. **No colons in flat mode IDs.**
- **`Deliverable element`**: human prose. Not parsed by the audit; can be rewritten without breaking matching.
- **`Producing script(s)`**: comma-separated `path:symbol` entries. The audit verifies `path` exists; `:symbol` is informational.

| ID | Deliverable element | Producing script(s) |
| -- | ------------------- | ------------------- |
|    |                     |                     |

---

## Stale-content policy

If a finding, claim, or screen in the deliverable drifts from current code (someone hand-edited the report, a stale screenshot, an outdated API doc), leave the registry **honest**: mark the row with `⚠` and note both the deliverable's value and the current value. Do NOT silently fix the deliverable from this file — only the deliverable's owner edits it. Spotting drift is part of this file's job.

---

## Maintenance Rules

1. **Every new deliverable element** (a new figure, table, screen, endpoint, scene, public function in the library) registers as a row here pointing at the producing script(s).
2. **Behavior changes** that surface differently in the deliverable update the relevant row AND a Recent Changes bullet in the corresponding `ContextModuleDocumentation/CONTEXT_<module>.md`.
3. **Stale-content tracking** — when the deliverable drifts, mark the affected row with `⚠` and note both values.
4. **Version bumps** — patch for typo / line-count fixes; minor for new entries; major for restructuring.
5. **File location** — keep this file at `docs/DELIVERABLE_PROVENANCE.md`. It is referenced by name from `CLAUDE.md`, every module CONTEXT file, and `compliance_config.yaml`. If you move it, update those references first.

See `decisions/0001-cut-script-registry.md` § "If you find yourself wanting to do X, look at Y" for what to do when this file does not seem to answer your question.
```

- [ ] **Step 2: Delete `templates/SCRIPT_PURPOSES.md`**

```bash
git -C /Users/work/Desktop/ClaudeTemplates rm templates/SCRIPT_PURPOSES.md
```

- [ ] **Step 3: Commit both changes together**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add templates/DELIVERABLE_PROVENANCE.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: replace templates/SCRIPT_PURPOSES.md with DELIVERABLE_PROVENANCE.md

Single section: Deliverable → Code Provenance. Script Registry section
cut per ADR-0001. References the ADR's redirect block for needs the
former Script Registry was serving."
```

---

## Task 16: Update `setup.sh` — copy new artifacts + migration block

**Files:**
- Modify: `setup.sh`

- [ ] **Step 1: Update `setup.sh` to copy new artifacts**

Find the existing block that copies hooks (around line 69-75):

```bash
for hook_file in parse_config.py pre-commit claude_read_gate.py claude_advisory_scan.py claude_subagent_gate.py claude_token_monitor.py; do
```

Add the new hook files to the loop:

```bash
for hook_file in parse_config.py pre-commit claude_read_gate.py claude_advisory_scan.py claude_subagent_gate.py claude_token_monitor.py run_provenance_check.py provenance_io.py; do
```

After the existing `# --- 3. Create directories ---` block (which mkdirs `ContextModuleDocumentation plans docs/superpowers/specs .claude`), append:

```bash
# Copy decisions/ directory (ADR discipline)
mkdir -p decisions
for adr_file in README.md 0001-cut-script-registry.md; do
    if [ -f "${SCRIPT_DIR}/decisions/${adr_file}" ]; then
        copy_if_missing "${SCRIPT_DIR}/decisions/${adr_file}" "decisions/${adr_file}"
    fi
done

# Copy parsers/ directory + CHANGELOG
mkdir -p parsers
for parser_file in __init__.py narrative_md.py CHANGELOG.md; do
    if [ -f "${SCRIPT_DIR}/parsers/${parser_file}" ]; then
        copy_if_missing "${SCRIPT_DIR}/parsers/${parser_file}" "parsers/${parser_file}"
    fi
done
```

Replace the existing block that copies SCRIPT_PURPOSES.md (around line 98-100) with the migration logic + new copy:

```bash
# Seed/migrate the deliverable-to-code provenance file.
DRY_RUN_FLAG=""
for arg in "$@"; do
    [ "$arg" = "--dry-run" ] && DRY_RUN_FLAG="yes"
done

if [ -f "docs/SCRIPT_PURPOSES.md" ] && [ ! -f "docs/DELIVERABLE_PROVENANCE.md" ]; then
    info "Detected legacy docs/SCRIPT_PURPOSES.md — migrating to DELIVERABLE_PROVENANCE.md"

    # Refuse to migrate over a dirty git tree
    if [ -n "$(git status --porcelain docs/SCRIPT_PURPOSES.md 2>/dev/null)" ]; then
        error "docs/SCRIPT_PURPOSES.md has unstaged changes. Stash or commit first."
        exit 1
    fi

    # Detect strip target
    if ! grep -q '^## Script Registry\s*$' docs/SCRIPT_PURPOSES.md; then
        error "docs/SCRIPT_PURPOSES.md present but no '## Script Registry' heading found."
        error "The file may have been customized (e.g., section retitled). Manual review required."
        exit 1
    fi

    # Print the diff that would be applied
    info "Migration would: rename docs/SCRIPT_PURPOSES.md → docs/DELIVERABLE_PROVENANCE.md"
    info "                 strip section from '## Script Registry' to next '---' or EOF"

    if [ -n "$DRY_RUN_FLAG" ]; then
        info "--dry-run set; no changes made"
    else
        echo ""
        read -rp "  Proceed with migration? [y/N]: " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            # Strip Script Registry section
            python3 - <<'PYEOF'
from pathlib import Path
src = Path("docs/SCRIPT_PURPOSES.md")
text = src.read_text()
lines = text.splitlines(keepends=True)
out = []
in_strip = False
for line in lines:
    if line.strip() == "## Script Registry":
        in_strip = True
        continue
    if in_strip and line.strip() == "---":
        in_strip = False
        continue
    if not in_strip:
        out.append(line)
dst = Path("docs/DELIVERABLE_PROVENANCE.md")
dst.write_text("".join(out).replace("SCRIPT_PURPOSES.md", "DELIVERABLE_PROVENANCE.md"))
src.unlink()
PYEOF
            info "Migration complete: docs/DELIVERABLE_PROVENANCE.md"
            warn "Next steps:"
            warn "  1. Add 'ID' column to existing rows in docs/DELIVERABLE_PROVENANCE.md"
            warn "  2. Populate compliance_config.yaml deliverable_inventory section"
            warn "  3. Re-run compliance_monitor to verify CHECK 7 passes"
        else
            warn "Migration skipped"
        fi
    fi
elif [ ! -f "docs/DELIVERABLE_PROVENANCE.md" ]; then
    if [ -f "${SCRIPT_DIR}/templates/DELIVERABLE_PROVENANCE.md" ]; then
        copy_if_missing "${SCRIPT_DIR}/templates/DELIVERABLE_PROVENANCE.md" "docs/DELIVERABLE_PROVENANCE.md"
    fi
fi
```

Update the "Next steps" summary at the end of `setup.sh` to mention `docs/DELIVERABLE_PROVENANCE.md` in place of `docs/SCRIPT_PURPOSES.md`.

- [ ] **Step 2: Verify shell syntax**

```bash
bash -n /Users/work/Desktop/ClaudeTemplates/setup.sh
```

Expected: no output (no syntax errors).

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add setup.sh
git -C /Users/work/Desktop/ClaudeTemplates commit -m "feat: setup.sh — migrate SCRIPT_PURPOSES.md, copy new artifacts

Detects existing docs/SCRIPT_PURPOSES.md, validates clean git tree,
finds '## Script Registry' heading, prompts (or --dry-runs) the
rename + strip. Aborts on customization (no heading found) per spec
§ Migration plan. Also copies decisions/, parsers/, and the new
hooks/run_provenance_check.py + provenance_io.py."
```

---

## Task 17: Manual end-to-end migration verification

**Files:**
- (no files modified; smoke test only)

- [ ] **Step 1: Create a scratch fixture**

```bash
SCRATCH=$(mktemp -d)
cd "$SCRATCH"
git init -q
mkdir docs
cat > docs/SCRIPT_PURPOSES.md <<'EOF'
# SCRIPT_PURPOSES.md

Version: 1.0.0

## Deliverable → Code Provenance

| Deliverable element | Producing script(s) |
| ------------------- | ------------------- |
| Sample finding      | src/foo.py          |

## Script Registry

#### `src/foo.py` (10 lines)

- **Purpose:** sample
- **Backs:** Sample finding

---

## Maintenance Rules

1. Sample
EOF
git add docs/SCRIPT_PURPOSES.md
git commit -q -m "fixture"
```

- [ ] **Step 2: Run setup.sh in `--dry-run`**

```bash
bash /Users/work/Desktop/ClaudeTemplates/setup.sh --dry-run
```

Expected output: includes "Detected legacy docs/SCRIPT_PURPOSES.md — migrating", and "--dry-run set; no changes made". File on disk unchanged.

- [ ] **Step 3: Run setup.sh interactively, answer 'y'**

```bash
bash /Users/work/Desktop/ClaudeTemplates/setup.sh
# answer y at the migration prompt
```

Expected: `docs/DELIVERABLE_PROVENANCE.md` now exists, `docs/SCRIPT_PURPOSES.md` deleted, the Script Registry section stripped, the Deliverable → Code Provenance table preserved.

- [ ] **Step 4: Verify output**

```bash
cat docs/DELIVERABLE_PROVENANCE.md
```

Expected: contains "## Deliverable → Code Provenance", does NOT contain "## Script Registry" or "src/foo.py" line, contains "## Maintenance Rules".

- [ ] **Step 5: Test the abort-on-customization path**

```bash
SCRATCH2=$(mktemp -d)
cd "$SCRATCH2"
git init -q
mkdir docs
echo "# Customized\n\nNo Script Registry heading here." > docs/SCRIPT_PURPOSES.md
git add docs/SCRIPT_PURPOSES.md
git commit -q -m "fixture"
bash /Users/work/Desktop/ClaudeTemplates/setup.sh --dry-run
```

Expected: aborts with "no '## Script Registry' heading found" + "Manual review required".

- [ ] **Step 6: Cleanup**

```bash
rm -rf "$SCRATCH" "$SCRATCH2"
```

- [ ] **Step 7: Commit a verification log**

(no source change; this task is verification only — note the result in the next commit message)

---

## Task 18: Update `CLAUDE.md` Tier 2 "Register every new file" rule

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace the Tier 2 "Register every new file" bullet**

In `CLAUDE.md`, find the bullet starting "**Register every new file** —". Replace its body with:

```markdown
- **Register every new file** — When creating a new source file (including splits/extractions), immediately: add the file header, add it to the module's CONTEXT_*.md and CONTEXT.md file maps with line count, and add it to the Interface Contracts table if it produces or consumes files. If the new file or its output surfaces a new element in the project's reader-facing deliverable (a finding, screen, endpoint, public API function, scene, etc.), add a row under Deliverable → Code Provenance in `docs/DELIVERABLE_PROVENANCE.md`. The script-itself does not need its own row — the per-file inventory was retired (see `decisions/0001-cut-script-registry.md`); CONTEXT files now own the file-level registry.
```

- [ ] **Step 2: Update Pre-Completion Compliance Checklist**

In the Advisory tier of the checklist, replace the SCRIPT_PURPOSES bullet with:

```markdown
- [ ] Every new deliverable-surfacing element (figure, screen, endpoint, etc.) registered as a row in `docs/DELIVERABLE_PROVENANCE.md` Deliverable → Code Provenance
```

- [ ] **Step 3: Bump version**

Top of file: `Version: 2.3.0` → `Version: 2.4.0`.

- [ ] **Step 4: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add CLAUDE.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "docs: CLAUDE.md 2.4.0 — register-new-file rule reflects Script Registry cut

Tier 2 bullet rewritten: per-file Script Registry retired, CONTEXT
files own file-level registry, DELIVERABLE_PROVENANCE.md owns the
deliverable→code map. ADR-0001 referenced. Pre-Completion checklist
Advisory bullet updated to match."
```

---

## Task 19: Update `CONTEXT_MODULE.md` Module Change Checklist

**Files:**
- Modify: `CONTEXT_MODULE.md`

- [ ] **Step 1: Replace the `docs/SCRIPT_PURPOSES.md updated` checklist item**

In `CONTEXT_MODULE.md`, find the bullet `**docs/SCRIPT_PURPOSES.md updated**`. Replace with:

```markdown
- [ ] **`docs/DELIVERABLE_PROVENANCE.md` updated** — If the change surfaces a new figure/screen/endpoint/scene in the project's reader-facing deliverable, add a row under Deliverable → Code Provenance. New source files no longer require a per-file registry entry (see `decisions/0001-cut-script-registry.md`).
```

- [ ] **Step 2: Bump version per the file's own decision table (minor)**

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add CONTEXT_MODULE.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "docs: CONTEXT_MODULE.md — checklist reflects Script Registry cut

Module Change Checklist item rewritten: DELIVERABLE_PROVENANCE.md
deliverable rows only; per-file registry retired."
```

---

## Task 20: Update `README.md` and `templates/PROJECT_README.md`

**Files:**
- Modify: `README.md`
- Modify: `templates/PROJECT_README.md`

- [ ] **Step 1: Add new section to `README.md`**

In `README.md`, after the section that describes hooks, add:

```markdown
### Parser-based provenance audit (CHECK 7)

The compliance monitor's CHECK 7 (`provenance_integrity`) compares parser-detected element IDs in each project's deliverable against rows in `docs/DELIVERABLE_PROVENANCE.md`. Configuration lives in `compliance_config.yaml` under `deliverable_inventory:` (a list of `{path, parser, parser_version, key?}` entries; `key` is required when ≥2 entries, all-or-nothing).

Parsers ship in `parsers/` (canonical) with project-local extensions in `parsers/local/`. The contract is one signature: `parse(file_contents: str) -> list[str]` plus a `VERSION` string. Local parsers use a `local-`-prefixed VERSION; canonical parsers must not. The audit refuses any parser whose VERSION-prefix doesn't match its location, surfacing silent forks in `compliance_config.yaml` itself.

The runner is `hooks/run_provenance_check.py`; the agent shells out to it and relays the JSON verdict. See `docs/superpowers/specs/2026-04-27-deliverable-provenance-audit-design.md` for the full audit logic, failure modes, and limitations.

`docs/DELIVERABLE_PROVENANCE.md` (downstream-installed by `setup.sh`) is the human-curated half. It replaces a prior `docs/SCRIPT_PURPOSES.md` whose two-section design is documented in `decisions/0001-cut-script-registry.md`.
```

Bump `README.md` version (per its own decision table).

- [ ] **Step 2: Update `templates/PROJECT_README.md`**

Search for any reference to `SCRIPT_PURPOSES.md` and replace with `DELIVERABLE_PROVENANCE.md`. Bump version.

```bash
grep -n SCRIPT_PURPOSES templates/PROJECT_README.md
```

If matches found: edit them with the corresponding `DELIVERABLE_PROVENANCE` reference. If none, no change needed; just bump version if any other CLAUDE-system reference changed.

- [ ] **Step 3: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add README.md templates/PROJECT_README.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "docs: README + PROJECT_README — provenance audit section + reference updates

Adds 'Parser-based provenance audit (CHECK 7)' section to top-level
README. Replaces SCRIPT_PURPOSES.md references in PROJECT_README.md."
```

---

## Task 21: Update `CONTEXT.md` and `ContextModuleDocumentation/CONTEXT_hooks.md`

**Files:**
- Modify: `CONTEXT.md`
- Modify: `ContextModuleDocumentation/CONTEXT_hooks.md`

- [ ] **Step 1: Update `CONTEXT.md` Architecture & File Map**

Add new entries for:
- `decisions/README.md`
- `decisions/0001-cut-script-registry.md`
- `parsers/__init__.py`
- `parsers/narrative_md.py`
- `parsers/CHANGELOG.md`
- `hooks/run_provenance_check.py`
- `hooks/provenance_io.py`
- `templates/DELIVERABLE_PROVENANCE.md`

Remove the entry for `templates/SCRIPT_PURPOSES.md`.

Add a Recent Changes block at the top dated 2026-04-27 describing this implementation.

Update `Module Context Files` table if a new module was added (it was not — these are extensions of existing modules).

Bump `CONTEXT.md` version.

- [ ] **Step 2: Update `ContextModuleDocumentation/CONTEXT_hooks.md`**

In the File Map section, add entries for `run_provenance_check.py` and `provenance_io.py` with their actual line counts (`wc -l hooks/run_provenance_check.py` and `wc -l hooks/provenance_io.py`).

Add a Recent Changes bullet dated 2026-04-27.

Bump version.

- [ ] **Step 3: Verify line counts in both CONTEXT files match `wc -l`**

```bash
wc -l hooks/run_provenance_check.py hooks/provenance_io.py parsers/narrative_md.py
# cross-reference these numbers against the file maps just edited
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/work/Desktop/ClaudeTemplates add CONTEXT.md ContextModuleDocumentation/CONTEXT_hooks.md
git -C /Users/work/Desktop/ClaudeTemplates commit -m "docs: CONTEXT files — register provenance audit infrastructure

CONTEXT.md and CONTEXT_hooks.md File Maps updated with new files
(decisions/, parsers/, run_provenance_check.py, provenance_io.py,
DELIVERABLE_PROVENANCE.md template); SCRIPT_PURPOSES.md template
entry removed. Line counts verified via wc -l. Recent Changes blocks
dated 2026-04-27."
```

---

## Task 22: Final integration verification + version cross-check

**Files:**
- (no source changes; verification + version sync)

- [ ] **Step 1: Run full test suite**

```bash
cd /Users/work/Desktop/ClaudeTemplates && pytest tests/ -v
```

Expected: all tests pass — `test_parse_config.py`, `test_narrative_md_parser.py` (8), `test_provenance_io.py` (13), `test_run_provenance_check.py` (16) = 38+ passing.

- [ ] **Step 2: Run runner self-check**

```bash
python3 hooks/run_provenance_check.py --self-check
```

Expected: JSON with `"status": "PASS"`, `"mode": "self-check"`, exit 0.

- [ ] **Step 3: Verify all modified `.md` files have bumped versions**

```bash
git -C /Users/work/Desktop/ClaudeTemplates diff main..HEAD --name-only -- '*.md' | while read -r f; do
    grep -H "^Version:" "$f" 2>/dev/null
done
```

Expected: every modified .md has a Version line; manual check that each is incremented vs the prior commit.

- [ ] **Step 4: Run compliance_monitor manually if Stop hook is wired**

(If running in Claude Code with the Stop hook enabled, this happens automatically. Otherwise, dispatch the agent or skip.)

- [ ] **Step 5: Commit any final version sync if needed**

```bash
# only if Step 3 found a missed version bump
git -C /Users/work/Desktop/ClaudeTemplates add <files>
git -C /Users/work/Desktop/ClaudeTemplates commit -m "chore: version sync for provenance audit implementation"
```

- [ ] **Step 6: Confirm done**

Implementation complete. Backport to EO14173 is its own brainstorm + plan cycle.

---

## Self-Review Notes

**Spec coverage check:** every spec § Components item has a corresponding task — DELIVERABLE_PROVENANCE.md (T15), decisions/README.md (T1), decisions/0001 (T2), parsers/__init__.py (T3), parsers/narrative_md.py (T4), parsers/CHANGELOG.md (T5), compliance_config.yaml (T13), agents/compliance_monitor.md (T14), setup.sh (T16). Doc edits CLAUDE.md (T18), CONTEXT_MODULE.md (T19), README.md (T20). All spec failure modes are tested in T6-T11. Migration verification in T17. Backport explicitly out of scope (per spec).

**Type / signature consistency check:** `parse(file_contents: str) -> list[str]` used identically in `parsers/__init__.py` docstring (T3), `parsers/narrative_md.py` (T4), `tests/test_narrative_md_parser.py` (T4), and `hooks/run_provenance_check.py` (T10). `Row` dataclass fields (`id`, `element`, `script_paths`) used consistently across `provenance_io.py` (T6) and the runner's reverse direction (T10-T11).

**Placeholder scan:** no TODO/TBD/"similar to Task N"/"add appropriate error handling" left in the plan body. All steps include exact commands or complete code.
