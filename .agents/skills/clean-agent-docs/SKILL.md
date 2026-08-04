---
name: clean-agent-docs
description: Cleans up and formats agent documentation to keep context loading efficient and cost-effective.
---

# /clean-agent-docs

Improve quality of repo agent docs/instructions/memory for lower token cost and cleaner context loading.

## Workflow

1. Read and audit all relevant docs surfaces:
   - `**/AGENTS.md`
   - `.agents/instructions/**/*.md`
   - `.agents/memory/**/*.md`
2. Find and fix:
   - duplicate guidance
   - stale or contradictory rules
   - broken or missing references/links
   - indexing gaps in `.agents/memory/INDEX.md`
   - over-broad always-load guidance that increases context pollution
3. Keep edits minimal, precise, and future-facing; avoid session-history chatter.
4. Activate the `update-agent-docs` skill and complete its checklist.
5. Validate doc changes with smallest appropriate checks (at least formatting check on changed docs).

## Constraints

- Do not change product/source code unrelated to docs quality work.
- Preserve repo conventions and frontmatter requirements.
- Prioritize making it easier for future agents to load only exact needed context.

## Return

- summary of key improvements
- files changed
- validation commands/results
