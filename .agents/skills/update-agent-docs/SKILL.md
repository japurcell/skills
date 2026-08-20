---
name: update-agent-docs
description: >
  Mandatory agent knowledge base update after making code changes in the repo. Always run at the end of
  every task that modifies code, adds files, changes public APIs or diagnostics, or establishes new
  patterns. Keeps .agents/instructions/ and .agents/memory/ fresh and reliable.
---

# Update Agent Docs

Keep `.agents/` small, current, and easy to navigate.

## Run When

Run at the end of every task that changes code. This is not optional.

## Workflow

1. Identify durable changes.
2. Review the session history specifically for **mistakes, failures, repeated retries, user corrections, steering updates, negative code review results, workarounds discovered, coordination failures, validation reruns, and resolved compiler/linter warnings**.
3. Extract any durable language, framework, or tooling rules learned from these mistakes.
4. Route each change to the right doc. See `refs/routing.md`.
5. Search related docs for existing guidance before adding text.
6. Update the most focused doc, or create one if needed.
7. Remove stale, duplicated, or contradicted nearby content.
8. Update indexes/frontmatter when needed. See `refs/indexes-frontmatter.md`.
9. Check links.
10. Report updates using the format below.

## Rules

- Edit only `.agents/instructions/` and `.agents/memory/`.
- Do not edit `.agents/skills/`.
- Document current repo state, not this task's story.
- Keep one canonical copy of each fact or rule.
- Prefer short, focused docs over grab bags.
- Use simple bullets and direct language.
- Do not store one-off notes, raw logs, speculation, or obvious facts from nearby code.
- If a cleanup is too large:
  - activate the `exec-plans` skill
  - orchestrate the updates with subagents
  - make file ownership explicit for each subagent to avoid conflicts
  - choose the smallest subagent model type that can effectively handle the task to avoid unnecessary cost and latency
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
