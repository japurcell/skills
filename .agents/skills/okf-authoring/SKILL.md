---
name: okf-authoring
description: Apply the in-place OKF representation contract when creating, modifying, migrating, or reviewing Markdown under .agents/instructions/ or .agents/memory/. Use after update-agent-docs semantic changes and for its ingest-source path; ordinary reads, immutable .agents/sources/, and Markdown outside these roots are out of scope.
---

# OKF Authoring

Keep canonical knowledge discoverable at its stable path while making its representation conform to the repository OKF profile. This skill owns representation, not knowledge selection.

## Workflow

1. Confirm that each target is Markdown under `.agents/instructions/` or `.agents/memory/`. For a question or review without change authorization, inspect and report only. Treat `.agents/sources/` as immutable input.

2. Identify each affected bundle and its path-derived type. Load [the shared profile](references/profile.md). Load [the source-summary branch](references/source-summaries.md) only for `.agents/memory/sources/**/*.summary.md`.

3. Keep semantic ownership with `update-agent-docs`: it decides durable content, placement, routing, deduplication, and index work. When it changed canonical documents, apply this representation pass afterwards. `okf-authoring` does not invoke `update-agent-docs`.

4. Apply only the required metadata, link, provenance, and lifecycle changes. Preserve stable paths, unrelated body text, and every out-of-scope file. Metadata-only conformance preserves the body byte-for-byte: when inserting frontmatter above a supplied body, place the body's first byte immediately after the closing delimiter newline unless that body already begins with a blank line.

5. Confirm that `update-agent-docs` handled applicable routing and index implications. Run `./scripts/lint-okf.py` from the repository root across both bundles, then inspect the scoped diff and record exactly the authorized changed paths. Exit `0` makes the change verified; exit `1` is authoritative nonconformance and leaves it incomplete; an unavailable linter, exit `2`, or `OKF900` leaves it unverified.

6. Report affected canonical paths and derived types; the exact branch references loaded (`profile`, plus `source-summaries` when applicable); routing/index implications; the exact lint command and result; and whether the scoped diff contains exactly the authorized paths. Claim completion or success only after clean lint and a clean scoped diff. Otherwise use `incomplete`, `unverified`, or `not applicable` without a success claim.
