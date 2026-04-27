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
