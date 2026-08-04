# Doc Quality

Agent docs should give future agents the smallest useful context.

## Core Rules

- Update existing focused docs before creating new ones.
- Put guidance where future agents will look for it.
- Keep indexes short; link instead of repeating content.
- Keep one canonical copy of each fact or rule.
- Use short headings, short bullets, and simple words.
- Do not mix instructions and memory.

## Progressive Disclosure

Agents should be able to start at an index and open only relevant docs.

Prefer:

- Small overview docs
- Focused docs for areas, tools, providers, or variants
- Links from indexes to focused docs

Avoid:

- Large mixed-topic files
- Rare details in shared docs
- Provider/platform/tool details in shared docs unless usually needed together

## Split When

Split a doc if it:

- Covers unrelated topics
- Has rare or narrow sections
- Forces agents to scan a large file for one detail
- Mixes instructions and memory
- Became a grab bag
- Covers variants agents usually need separately

Example split:

- `.agents/memory/hooks/INDEX.md`
- `.agents/memory/hooks/shared-hook-architecture.md`
- `.agents/memory/hooks/gemini-hooks.md`
- `.agents/memory/hooks/copilot-hooks.md`

If variants are tightly coupled, one focused combined doc is fine:

- `.agents/memory/hooks/gemini-copilot-hooks.md`

## Deduplicate

When duplicate guidance exists:

1. Pick the canonical location.
2. Merge useful content there.
3. Delete duplicate text elsewhere.
4. Add a short link only if useful.
5. Update indexes and links.

## Required Cleanup Check

Before finishing, check touched and closely related docs for:

- Duplicate content
- Stale or contradicted claims
- Broad sections that should be split
- Missing or vague index entries
- Broken links
- Instructions stored as memory
- Memory stored as instructions
- Long task narratives
- Raw logs or debug transcripts

Fix small issues immediately.

## Do Not Store

Do not add:

- One-off task notes
- Raw command output
- Temporary debugging details
- Obvious facts from nearby code
- Speculation
- Long summaries of what the last agent did
