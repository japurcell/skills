---
name: update-agent-docs
description: >
  Update the agent knowledge base after making code changes in the repo. Run at the end of
  every task that modifies code, adds files, changes public APIs or diagnostics, or establishes new
  patterns. Keeps .agents/instructions/ and .agents/memory/ fresh and reliable.
---

# Update Agent Docs

Keep `.agents/` small, current, and easy to navigate.

## Run When

Run at the end of every task that changes code. This is not optional.

## Workflow

1. Identify durable changes.
2. Route each change to the right doc. See `refs/routing.md`.
3. Search related docs for existing guidance before adding text.
4. Update the most focused doc, or create one if needed.
5. Remove stale, duplicated, or contradicted nearby content.
6. Update indexes/frontmatter when needed. See `refs/indexes-frontmatter.md`.
7. Check links.
8. Report updates using the format below.

## Rules

- Edit only `.agents/instructions/` and `.agents/memory/`.
- Do not edit `.agents/skills/` or `.agents/sources/`.
- Document current repo state, not this task's story.
- Keep one canonical copy of each fact or rule.
- Prefer short, focused docs over grab bags.
- Use simple bullets and direct language.
- Do not store one-off notes, raw logs, speculation, or obvious facts from nearby code.
- If a cleanup is too large, make one useful improvement and add a short TODO in the most relevant doc.
- If no durable knowledge changed, make no doc edits and report that no update was needed.

More quality rules: `refs/doc-quality.md`.

## Final Response Format

Use this short summary:

```text
Added:
Changed:
Split or moved:
Deduplicated:
Index updates:
Remaining doc quality TODOs:
```
