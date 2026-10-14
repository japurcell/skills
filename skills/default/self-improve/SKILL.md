---
name: self-improve
description: Use to update or refactor AGENTS.md and linked instruction docs by preserving durable repo-specific guidance, removing duplicate/conflicting/stale instructions, and mining reusable lessons from session notes, handoffs, corrections, commands, failures, mistakes, validation steps, and execution friction so that future agents don't make the same mistakes.
---

# Self Improve

Keep future-agent instructions useful, scoped, and lightweight. Preserve durable guidance only; do not record one-off noise.

Do not use for temporary blockers, obvious facts, generic advice, speculation, or one-time failures.

## Workflow

1. **Find instruction files**
   - Find relevant files with: `find . -path './.git' -prune -o -name AGENTS.md -print`
   - Read applicable `AGENTS.md` files and directly linked instruction docs.
   - If none exist, create `./AGENTS.md` only when the user asked or strong durable guidance exists.

2. **Extract candidate lessons**
   - Review the user request, conversation, work artifacts, and validation history.
   - Include execution friction only when it reveals a reusable rule: stale paths, repeated patch retries, coordination failures, validation reruns, or user corrections.
   - For keep/skip criteria, see `DURABLE_LEARNINGS.md`.

3. **Place guidance correctly**
   - Root `./AGENTS.md`: repo-wide rules that should always load.
   - Scoped `./**/AGENTS.md`: directory/module/package rules.
   - Linked docs: long, rare, procedural, example-heavy, or branch-specific guidance.
   - For refactor/scoping rules, see `INSTRUCTION_STRUCTURE.md`.

4. **Edit minimally**
   - Use short, specific, actionable bullets.
   - Prefer exact commands, paths, flags, ordering, and constraints.
   - Remove duplicates only after preserving the rule in the right place.
   - Resolve contradictions; do not keep both sides.
   - Make no change if nothing clears the durable-learning bar.

5. **Report**
   - State what durable guidance was found.
   - List files changed and why.
   - If no changes were made, say why candidates did not qualify.
   - If refactored, note moved guidance, deleted duplicates, resolved conflicts, and assumptions.

## Final Check

- Relevant `AGENTS.md` files and linked docs reviewed.
- Durable items kept; low-value items skipped.
- Guidance placed at the right scope.
- Root remains short.
- Duplicates and conflicts removed.
- No orphan links remain.
