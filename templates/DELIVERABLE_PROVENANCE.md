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
