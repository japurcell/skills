---
name: clean-agent-docs
description: Audit and simplify repository agent instructions, memory, and routing docs. Use when agent context is duplicated, stale, contradictory, overly broad, poorly indexed, or expensive to load.
---

# Clean Agent Docs

Reduce agent-doc context cost while preserving durable guidance.

## Workflow

1. Inventory relevant files:
   - `**/AGENTS.md`
   - `.agents/instructions/**/*.md`
   - `.agents/memory/**/*.md`
2. Map the load path:
   - Identify default-loaded docs, indexes, pointers, and task-specific docs.
   - Note where broad docs force unrelated context to load.
3. Audit each relevant file using [references/audit-checklist.md](references/audit-checklist.md).
4. Make the smallest coherent edits:
   - Keep one canonical location for each rule.
   - Replace duplicates with links.
   - Resolve contradictions in favor of the narrowest authoritative source.
   - Make indexes and pointers state what to read and when.
   - Keep default-loaded docs short and broadly applicable.
5. If a default or mixed-topic doc needs restructuring, use [references/splitting-guide.md](references/splitting-guide.md).
6. Activate the `update-agent-docs` skill and complete its checklist.
7. Validate:
   - Run the repository's doc-formatting or lint command on changed files.
   - Check changed links and index entries.
   - Review the diff for lost guidance and unrelated changes.

## Constraints

- Do not change unrelated product or source code.
- Preserve repository conventions and required frontmatter.
- Prefer links to repeated text.
- Do not invent policy or silently discard unique durable guidance.
- Keep session history, one-off task state, secrets, and raw work logs out of durable docs.
- Do not broaden default-load scope unless necessary.
- Purge content that the codebase already shows.
- Prefer rewriting or pruning existing entries over appending new ones.

## Return

Report:

- Key improvements
- Files changed
- Content moved or dropped
- Validation commands and results
- Unresolved conflicts or broken references
