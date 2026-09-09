# Indexes and Frontmatter

## Frontmatter

For new or existing `.agents/instructions/` or `.agents/memory/` docs, use parseable OKF frontmatter with non-empty path-derived `type` and routing-oriented `description`:

```yaml
---
type: Agent Memory
description: Brief description of what this doc covers
---
```

Use `Agent Instruction` below `.agents/instructions/`; `Knowledge Index` for uppercase `INDEX.md`; `Source Ingestion Log` for uppercase `LOG.md`; `Known Issue` for root `KNOWN_ISSUES.md` and `known-issues/**`; `Testing Guidance` for root `TESTING_STRATEGY.md` and `testing/**`; `Architecture Decision` for `adrs/**`; `Source Summary` for recursive `sources/**/*.summary.md`; and `Agent Memory` otherwise. Stable documents omit lifecycle `status`; use `status: draft` only for an actual draft. Keep repository-local links file-relative and preserve paths and unrelated bodies during metadata-only work. `okf-authoring` owns the full profile and lint verification.

## New Docs

Create a new focused doc when durable information does not fit an existing focused doc.

Rules:

- Use a descriptive name, not `misc.md`.
- Add non-empty path-derived `type` and routing-oriented `description` frontmatter.
- Add or update index entries when an index exists.
- No permission is needed to create focused docs in `.agents/instructions/` or `.agents/memory/`.

## Memory Index Entries

Indexes should route agents, not explain the whole topic.

Each `.agents/memory/INDEX.md` entry should say:

- What the doc covers
- When to read it
- When not to read it, if confusion is likely

Good:

- `hooks/gemini-copilot-hooks.md`
  - Covers shared Gemini/Copilot hook orchestration and provider-specific hook behavior.
  - Read when modifying Gemini or Copilot git hooks or hook tests.
  - Do not read for unrelated tooling, package manager, linting, or CI changes.

Bad:

- `tooling.md` - tooling notes.

## Instruction Indexes

If instruction docs are added, moved, renamed, split, or removed, update the matching instruction index if one exists.
