# Deliverable Provenance Audit — Design Spec

Version: 1.0.0
Date: 2026-04-27
Status: proposed

---

## Summary

Replace the template's `templates/SCRIPT_PURPOSES.md` (two sections: Deliverable→Code Provenance + Script Registry) with a single-section `templates/DELIVERABLE_PROVENANCE.md` audited mechanically by `compliance_monitor` against parser-detected elements in each project's reader-facing deliverable. The Script Registry section is cut because it duplicates information already in CONTEXT files; the surviving Deliverable→Code Provenance map is the unique value (reverse index from a finding/screen/endpoint/function to the producing script). A first-class ADR records why the cut happened so future-you doesn't reintroduce it. Configuration is generic across project shapes (analysis report, web app, API, library, game build) via a pluggable parser interface and a list-valued `deliverable_inventory:` config block.

This spec covers template-level changes plus the migration logic. Backport to the EO14173 project is described under § Backport but is its own implementation task with its own plan.

---

## Problem

The template's enforcement machinery — pre-commit hooks, Claude Code PreToolUse/PostToolUse hooks, the session-end compliance monitor — does not touch `SCRIPT_PURPOSES.md`. Maintenance is policy-only via manual checklists in `CLAUDE.md` and per-module `CONTEXT_*.md` files. The compliance monitor's six existing checks audit `CONTEXT.md` and `CONTEXT_*.md` but explicitly not `SCRIPT_PURPOSES.md`. Failure modes:

- New source files land in CONTEXT but not in `SCRIPT_PURPOSES.md` → silent rot.
- Line counts in `SCRIPT_PURPOSES.md` drift from `wc -l` reality with no audit.
- Deleted source files leave stale Script Registry entries forever.
- New findings appear in the deliverable with no Provenance row → reader can't trace numbers back to code.
- Provenance rows survive after the deliverable's findings are dropped → reader trusts a row that points to dead code.

The Script Registry section duplicates information already authoritative elsewhere: line counts (CONTEXT.md and module CONTEXT files), public symbols (source code), one-line purposes (CONTEXT files and module docstrings). This duplication is the *structural cause* of the enforcement gap — triple-bookkeeping invites either skipped updates or pressure to simplify the docs. Adding mechanical audit on top of three duplicated stores enforces a duplication that should be eliminated, not stabilized.

---

## Decision: ElementID matching by explicit IDs

The audit compares two sets of IDs: those detected by a parser in the deliverable, and those listed in the Provenance map. Three matching strategies were considered; only one is viable.

| Strategy | Rejected because |
|---|---|
| Exact-string match | The deliverable for analysis projects is *auto-generated* (`output/results_narrative.md` from `src/reporting/formatters.py` in James). Any prose change in the formatter breaks every Provenance row simultaneously; the audit punishes formatter improvements rather than catching real drift. |
| Normalized match (lowercase, strip punctuation, collapse whitespace) | Handles formatting drift but cannot bridge wording rewrites. "Chi-square test = 22.63" vs "P5 χ² = 22.63" normalize to different strings. The realistic rot mode is paper revision rephrasing, which normalization cannot accommodate. |
| **Explicit IDs** *(chosen)* | Each deliverable element carries a stable identifier; the Provenance row references it in a dedicated column; the parser extracts IDs, not finding text. Audit is a pure set comparison on IDs. Matching is decoupled from text. |

**Cost of explicit IDs.** Each project's deliverable must carry IDs. For most project shapes this is free — web routes are IDed by path, OpenAPI operations by `operationId`, library functions by name, game scenes by scene name. Only the analysis-report shape requires a new convention: an HTML comment marker (`<!-- id: <stable-id> -->`) emitted alongside each numeric finding. For James, this is a one-time edit to `src/reporting/formatters.py`.

Picking explicit IDs is therefore a *standardization* on what most deliverable shapes already do natively, not a new burden.

---

## Components

Eight artifacts in `templates/`:

1. **`templates/DELIVERABLE_PROVENANCE.md`** — replaces `templates/SCRIPT_PURPOSES.md`. Single section with a three-column table: `| ID | Deliverable element | Producing script(s) |`. Header preserves deliverable-shape-agnostic framing.
2. **`decisions/README.md`** — ADR discipline: numbering scheme (zero-padded sequential: `0001`, `0002`, …), status field (`proposed` / `accepted` / `superseded`), supersede protocol (don't edit accepted ADRs; write a new ADR that supersedes them and update the old one's status field with a back-reference).
3. **`decisions/0001-cut-script-registry.md`** — first ADR. Includes a *redirect block* answering each need that Script Registry was answering: "If you want to know what scripts exist → CONTEXT.md file map. If you want to know what a script does → CONTEXT_*.md or module docstring. If you want to know what report content depends on a script → grep the ID column of `docs/DELIVERABLE_PROVENANCE.md`."
4. **`parsers/__init__.py`** — declares the parser interface contract in a docstring. No parser registry; discovery is by file presence in `parsers/` and `parsers/local/`.
5. **`parsers/narrative_md.py`** — first parser. Detects `<!--\s*id:\s*([\w-]+)\s*-->` markers in markdown. Carries a `VERSION` constant.
6. **`compliance_config.yaml`** — schema additions:
   - `deliverable_inventory: [{path, parser, parser_version}, ...]` (list, optional; empty/missing → reverse direction skipped)
   - `compliance_monitor.provenance_strict: false` (default; promotes WARN to FAIL when true)
   - `compliance_monitor.checks` adds `provenance_integrity` (CHECK 7)
7. **`agents/compliance_monitor.md`** — adds CHECK 7 spec; adds `docs/DELIVERABLE_PROVENANCE.md` to Inputs; adds parser-loading from `parsers/` and `parsers/local/`.
8. **`setup.sh`** — adds migration block: detects `docs/SCRIPT_PURPOSES.md`, supports `--dry-run` and refuses to migrate over a dirty git tree.

Three documentation edits:

- **`CLAUDE.md`** — Tier 2 "Register every new file" rewrite to drop Script Registry mention; references `docs/DELIVERABLE_PROVENANCE.md` only. Pre-Completion Checklist Advisory tier updated. Version bump 2.3.0 → 2.4.0.
- **`CONTEXT_MODULE.md`** — Module Change Checklist item rewritten to drop Script Registry bullet. Version bump per its own decision table.
- **`README.md`** — section explaining the parser-based audit, the `deliverable_inventory` schema, and how to add a project-local parser.

---

## DELIVERABLE_PROVENANCE.md schema

Single section. Three-column markdown table:

```markdown
| ID         | Deliverable element                            | Producing script(s)                                                  |
| ---------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| p5-chi     | P5 chi-square test of Configuration A vs B     | src/propositions/p5_oliver.py:_chi_square                            |
| fig2       | Figure 2 — sector × ban CIs                    | src/descriptives/figures.py:fig2_sector_by_ban → output/figures/fig2.png |
| p1-ame     | P1 AME (sector × ban) = 0.1802                 | src/propositions/p1_coercive.py:run, src/propositions/utils.py:compute_ames |
```

**Rules:**

- ID column values must be unique within the file.
- ID format: `[A-Za-z0-9_-]+`, ≤ 32 chars. Recommended convention `<group>-<finding-shorthand>` (e.g. `p5-chi`, `fig2`, `endpoint-create-user`). Convention is recommended in ADR-0001's redirect block, not enforced.
- Deliverable element column is human prose. Not parsed by the audit.
- Producing script(s) column is comma-separated `path:symbol` entries. The audit verifies `path` exists; `:symbol` is informational and not currently checked.

---

## Parser interface

Each parser is a Python module under `parsers/` (or `parsers/local/`) that exports two names:

```python
VERSION = "1.0.0"

def parse(file_contents: str) -> list[str]:
    """Return list of stable ElementIDs found in the file."""
```

That is the entire contract. Parsers must not return positions, contexts, types, or counts — only IDs. If a parser's job seems to need richer output, that is a signal the abstraction is wrong; split into multiple parsers or extend the audit's logic, do not extend the interface.

**`narrative_md` reference implementation:**

```python
import re
VERSION = "1.0.0"
_ID_PATTERN = re.compile(r"<!--\s*id:\s*([A-Za-z0-9_-]+)\s*-->")

def parse(file_contents: str) -> list[str]:
    return sorted(set(_ID_PATTERN.findall(file_contents)))
```

---

## Audit data flow (CHECK 7: `provenance_integrity`)

**Inputs added to the agent's input list:**

- Full content of `docs/DELIVERABLE_PROVENANCE.md`
- Listing of `parsers/` and `parsers/local/` directories
- `compliance_config.yaml.deliverable_inventory` list
- `compliance_config.yaml.compliance_monitor.provenance_strict` boolean

**Logic:**

```
forward_direction (always runs when DELIVERABLE_PROVENANCE.md exists):
    For each row in DELIVERABLE_PROVENANCE.md:
        For each `path:symbol` in the "Producing script(s)" cell:
            Verify path exists on disk.
        If any path missing → WARN (FAIL if provenance_strict).

reverse_direction (runs only when deliverable_inventory is non-empty):
    For each {path, parser, parser_version} entry in deliverable_inventory:
        Resolve parser:
            Search parsers/local/<parser>.py first, then parsers/<parser>.py.
            If neither exists → FAIL the entry.
        Import parser module.
        Compare parser.VERSION to entry.parser_version.
            On mismatch → WARN with both versions.
        Read file at entry.path.
            If missing → FAIL the entry.
        Try parser.parse(contents).
            On exception → FAIL the entry with traceback.
        detected_ids = result of parse()
        provenance_ids = IDs from DELIVERABLE_PROVENANCE.md ID column

        forward_misses = detected_ids - provenance_ids
        reverse_misses = provenance_ids - detected_ids

        Always log (PASS or FAIL):
            count_detected = len(detected_ids)
            count_provenance = len(provenance_ids)
            entry.path, entry.parser, entry.parser_version

        If forward_misses non-empty → WARN per element (FAIL if provenance_strict)
        If reverse_misses non-empty → WARN per element (FAIL if provenance_strict)
```

The count-logging on every run (PASS or FAIL) surfaces silent shifts: "47 → 47" passes, "31 → 31" passes, but a delta from 47 to 31 over time is information the human reviewer wants. Logging on PASS is the cheap fix.

---

## Failure modes (specified, not ad-hoc)

| Condition | Behavior |
|---|---|
| `deliverable_inventory` unset or empty list | Reverse direction SKIPPED with informational log; forward direction still runs. |
| `path` field of an entry doesn't exist on disk | FAIL the entry (config error, regardless of `provenance_strict`). |
| `parser` name doesn't resolve to a file in `parsers/` or `parsers/local/` | FAIL the entry with `"unknown parser: <name>. Available: [...]"`. |
| Parser module imports but raises during `parse()` | FAIL the entry with traceback; do not silently skip. |
| Parser returns non-list, or list containing non-strings | FAIL with type error. Parser bug. |
| Two `deliverable_inventory` entries detect overlapping IDs | Union the IDs (no error). A finding can be cited by multiple deliverables. |
| `DELIVERABLE_PROVENANCE.md` missing | FAIL if `deliverable_inventory` is set; SKIP whole check otherwise. |
| `DELIVERABLE_PROVENANCE.md` present but contains no rows | WARN — no IDs to compare; reverse direction passes vacuously. |
| Provenance row missing ID column or with empty ID | FAIL (malformed row; list the row's deliverable element for the human). |
| Duplicate IDs within `DELIVERABLE_PROVENANCE.md` | FAIL with the list of duplicates. |
| Parser `VERSION` mismatch with `entry.parser_version` | WARN with both versions; do not block. |
| Project-local parser shadows a template parser of the same name | Use the local one; log informationally. |

---

## What this audit does NOT catch

The audit is a *structural integrity* check. Honest limitations:

- **Wrong linkage.** A Provenance row that says `p5-chi → src/propositions/p3_resource.py` will pass if both the row and the script exist. The audit does not verify that the named script actually computes the named finding.
- **Semantic drift.** A row says "P5 chi-square test" but the script now computes Fisher's exact. The audit cannot detect this; only a human reading the row can.
- **Silently dropped findings.** A finding removed from the deliverable but kept in the Provenance map shows up as a reverse-miss WARN — but only if `deliverable_inventory` is configured. With it unset, the reverse direction does not run and this rot is invisible.
- **Rephrased deliverable elements.** If a finding's prose changes but its ID stays stable, the audit (correctly) does not flag it. The audit does not enforce that deliverable text matches Provenance text — that's why we picked explicit IDs over exact-string matching.
- **Incomplete parser coverage.** If a parser regex misses some valid findings (e.g., a finding's ID tag has a typo), the parser silently underreports. Detection requires the count-logging feature; reading "found 31 IDs" when the deliverable obviously has more flags it. The audit does not auto-detect this — a human reviews the count.

These are spec'd intentionally so that the audit is not trusted beyond its scope. The compliance monitor's report should print the limitations list verbatim alongside any PASS or FAIL on this check, so consumers of the report don't over-extend their trust.

---

## Parser versioning protocol

Each parser exports `VERSION` (semver). Each `deliverable_inventory` entry records `parser_version`. Behavior changes:

| Parser change | Bump |
|---|---|
| Bug fix that *adds* detection (parser previously missed valid findings) | MAJOR |
| Bug fix that *removes* detection (parser previously matched invalid things) | MAJOR |
| New optional behavior gated behind a config field | MINOR |
| Refactor, comment changes, performance with no detection change | PATCH |

Parser authors document the change in `parsers/CHANGELOG.md`. Projects do **not** auto-upgrade — `parser_version` in `compliance_config.yaml` pins the version a project tested with. To upgrade, the project owner manually bumps the config field and re-runs the compliance monitor; mismatches WARN until the bump.

The single shared `parsers/CHANGELOG.md` file (rather than per-parser CHANGELOGs) is chosen for discoverability. Every parser change appears in one place.

---

## Parser location: template-shipped with project-local extension

Template ships parsers in `parsers/`. `setup.sh` copies them to the project. Projects may add custom parsers in `parsers/local/` (gitignored is recommended; the `.gitignore` template seed picks this up). The audit looks in both directories; `parsers/local/<name>.py` shadows `parsers/<name>.py` on collision.

This is a deliberate hybrid:

- **Bug fixes propagate** when the user re-runs `setup.sh` (which prompts before overwriting any parser file).
- **Projects extend the vocabulary locally** without modifying the template (and without a coordination bottleneck).

The "single source of truth" property is preserved at the *interface contract* level (one signature, one return type, in `parsers/__init__.py`), not at the implementation level — the template owns the canonical implementations, projects own their extensions.

---

## Migration plan (`setup.sh`)

`setup.sh` gains a migration block, idempotent and safe:

```
if [ -f "docs/SCRIPT_PURPOSES.md" ] && [ ! -f "docs/DELIVERABLE_PROVENANCE.md" ]; then
    1. Verify clean git tree under docs/. If dirty: abort with
       "docs/SCRIPT_PURPOSES.md has unstaged changes. Stash or commit first,
        or pass --force-migrate to override."
    2. Print the diff that would be applied: lines preserved (Deliverable →
       Code Provenance section + maintenance rules) vs lines stripped
       (Script Registry section, delimited by `## Script Registry` heading
       to next `---` or EOF).
    3. If --dry-run: exit 0.
    4. Else: prompt "Migrate? [y/N]". On y:
         - Rename docs/SCRIPT_PURPOSES.md → docs/DELIVERABLE_PROVENANCE.md
         - Strip the Script Registry section using the delimiter rule above
         - Update internal references in the file (`Script Registry` →
           document removal; `SCRIPT_PURPOSES.md` → `DELIVERABLE_PROVENANCE.md`)
    5. Print: "Migration complete. Next: add `ID` column to existing rows
       in docs/DELIVERABLE_PROVENANCE.md, populate compliance_config.yaml's
       deliverable_inventory section, and re-run compliance_monitor."
fi
```

The migration is *conservative* — it strips one section but does not modify rows in the surviving section. Adding the ID column is a manual step; the migration prints the instruction. Setting `deliverable_inventory` is a manual step. This is intentional: the migration is not meant to leave a project in an audit-passing state, only in a structurally migrated state.

---

## Backport to EO14173 (separate implementation task)

After template changes are committed, the EO14173 project is migrated as its own task with its own implementation plan. Steps:

1. Run new `setup.sh` in `/Users/work/Desktop/Folders/James/`. Migration prompt → rename + strip.
2. Manually merge new `CLAUDE.md` Tier 2 text with James's project-specific Tier 1 rules. Bump version.
3. Manually merge new `CONTEXT_MODULE.md` checklist with James's domain-specific checklists.
4. Add to `compliance_config.yaml`:
   ```yaml
   deliverable_inventory:
     - path: output/results_narrative.md
       parser: narrative_md
       parser_version: "1.0.0"
   compliance_monitor:
     provenance_strict: false  # promote to true after first clean audit
     checks:
       # ... existing checks ...
       - id: provenance_integrity
         description: "Deliverable elements match Provenance rows by ID"
   ```
5. Edit `src/reporting/formatters.py` to emit `<!-- id: <stable-id> -->` markers alongside each numeric finding. Convention: `p<N>-<shorthand>` (e.g. `p5-chi`, `p1-ame`, `p6-mixedlm-coef`, `p6-paired-t`).
6. Add `ID` column to existing rows in the migrated `docs/DELIVERABLE_PROVENANCE.md`.
7. Re-run `python3 main.py --collapse-binary` to regenerate `output/results_narrative.md` with IDs.
8. Run `compliance_monitor`. Resolve any drift surfaced.
9. Once clean, set `provenance_strict: true` so future drift becomes blocking.

---

## Out of scope (deferred)

- **Template self-test** (`tests/test_template_meta.py`): own spec. Catches cross-doc skew between `CLAUDE.md`, `compliance_config.yaml`, `agents/compliance_monitor.md`, and `CONTEXT_MODULE.md`. The failure mode that originally caused this gap (SCRIPT_PURPOSES landing in CLAUDE.md but not compliance machinery on 2026-04-27) is exactly what this would have caught.
- **Auto-generation of CONTEXT.md line counts via AST**: revisit only if line-count drift becomes the dominant pain point post-migration.
- **Additional parsers** (`openapi_yaml.py`, `routes_json.py`, etc.): demand-driven. Add when the next project shape shows up; the parser interface is intentionally tight to keep this cheap.
- **Per-finding semantic verification** (verify the named script actually computes the named finding): out of scope. Semantic verification is not what an audit does; it is what code review and tests do.

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Migration disrupts in-flight work in `docs/SCRIPT_PURPOSES.md` | `setup.sh` checks `git status` for the file and refuses to migrate without `--force-migrate`. |
| ID convention drifts inconsistently across projects | ADR-0001's redirect block names a recommended convention (`<group>-<shorthand>`). Not enforced — convention, not contract. |
| Parsers become load-bearing infrastructure | Interface stays one sentence; parsers stay under ~50 lines; behavior changes require MAJOR bump and CHANGELOG entry. |
| Project-local parsers fragment the vocabulary | Acceptable trade-off for extension flexibility; the canonical parsers in `parsers/` remain the reference. The compliance report logs which parser variant was used (template vs local). |
| ADRs accumulate inconsistently and lose discipline | `decisions/README.md` defines numbering, status field, supersede protocol up front. ADR template included. |

---

## Open questions (non-blocking)

- **ID column heading text**: `ID` vs `Element ID` vs `Provenance ID`. Lean: `ID` (short, table-friendly). Decide at implementation time.
- **`parser_version` field default behavior**: if omitted, accept any parser version (silent), or require pin (block)? Lean: require pin. A missing field is a config error, not a flexibility feature.
- **Does the migration script also copy the EO14173 project's existing `Recent Changes` notes into `decisions/0002-eo14173-script-registry-cut.md` automatically?** Lean: no, manual. The backport task is small enough that hand-writing the ADR is reasonable, and auto-extraction adds setup.sh complexity for one-time benefit.

These are decisions that fall out of implementation, not architecture. None block writing the implementation plan.
