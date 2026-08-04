# Indexes and Frontmatter

## Frontmatter

For new or existing `.agents/instructions/` or `.agents/memory/` docs, use only `coverage` frontmatter:

```yaml
---
coverage: Brief description of what this doc covers
---
```

Do not add:

- `last_updated`
- `updated_by`
- `confidence`
- Date fields

Git history tracks those details.

## New Docs

Create a new focused doc when durable information does not fit an existing focused doc.

Rules:

- Use a descriptive name, not `misc.md`.
- Add only `coverage` frontmatter.
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
