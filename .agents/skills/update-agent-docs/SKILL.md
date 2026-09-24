---
name: update-agent-docs
description: >
  Mandatory agent knowledge base update after making code changes in the repo to keep .agents/instructions/ and .agents/memory/ fresh and reliable. Always run at the end of every work session that modifies code, adds files, changes public APIs or diagnostics, or establishes new patterns. DO NOT run after every task if you are working on multiple tasks or delegating work to subagents in a single session. Instead, run after all tasks and/or subagents have completed.
---

# Update Agent Docs

Keep agent documentation small, current, and easy to route.

## Workflow

1. Review the final diff and session history.
2. Derive durable, non-obvious rules from **mistakes, failures, repeated retries, user corrections, steering updates, negative code review results, workarounds discovered, coordination failures, validation reruns, and resolved compiler/linter warnings**.
3. Route each rule using [routing](refs/routing.md).
4. Search related docs before adding content.
5. Update the smallest relevant doc. Create a focused doc only when needed.
6. Remove nearby stale, duplicate, or contradictory guidance.
7. When shortening or splitting a doc, preserve every durable rule in the appropriate focused doc.
8. Apply [document quality](refs/doc-quality.md).
9. Update frontmatter, indexes, and links using [indexes and frontmatter](refs/indexes-frontmatter.md).
10. After semantic changes to canonical documents, invoke `okf-authoring` to apply and verify the OKF representation contract.
11. Report the result.

## Rules

- Edit only `.agents/instructions/` and `.agents/memory/`.
- Do not edit `.agents/skills/` or `.agents/sources/`.
- Describe verified current behavior, not task history.
- Keep one canonical copy of each fact or rule.
- Record diagnostics, linter rules, and framework quirks only when they reveal durable, non-obvious guidance.
- If no durable knowledge changed, make no edits.
- Do not leave broken links.
- Do not document what the codebase already shows.
- Prefer rewriting or pruning existing entries over appending new ones.

## Final Response

Use `None` for empty sections.

```text
Added:
Changed:
Split or moved:
Deduplicated:
Index updates:
Remaining doc quality TODOs:
```
