# Indexes and Frontmatter

## Frontmatter

Created or touched agent docs must have parseable OKF frontmatter:

```yaml
---
type: Agent Memory
description: What this document covers and when to read it
---
```

Use the first matching type:

| Path | `type` |
| --- | --- |
| `.agents/instructions/**` | `Agent Instruction` |
| `.agents/memory/**/INDEX.md` | `Knowledge Index` |
| `.agents/memory/**/LOG.md` | `Source Ingestion Log` |
| `.agents/memory/KNOWN_ISSUES.md` or `.agents/memory/known-issues/**` | `Known Issue` |
| `.agents/memory/TESTING_STRATEGY.md` or `.agents/memory/testing/**` | `Testing Guidance` |
| `.agents/memory/adrs/**` | `Architecture Decision` |
| `.agents/memory/sources/**/*.summary.md` | `Source Summary` |
| Other `.agents/memory/**` | `Agent Memory` |

Rules:

- Make `description` useful for routing.
- Omit `status` for stable docs.
- Use `status: draft` only for an actual draft.
- Keep repository-local links file-relative.
- Preserve paths and unrelated content during metadata-only edits.
- Use `okf-authoring` for the complete profile and lint checks.

## New Docs

Create a doc only when durable content does not fit an existing focused doc.

- Use a descriptive filename, not `misc.md`.
- Add frontmatter.
- Update the relevant index, if present.
- No permission is needed within `.agents/instructions/` or `.agents/memory/`.

## Index Entries

Indexes route agents; they do not repeat document content.

Each entry should state:

1. What the doc covers
2. When to read it
3. When not to read it, if confusion is likely

Example:

```markdown
- `hooks/gemini-hooks.md`
  - Gemini hook behavior and known constraints.
  - Read when changing Gemini hooks or their tests.
  - Do not read for unrelated CI or package-management work.
```

Update the relevant index when a doc is added, moved, renamed, removed, split, or repurposed.
