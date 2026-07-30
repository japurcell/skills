---
name: self-improve
description: Update or refactor repo instruction files to preserve durable, repo-specific guidance. Use when the user asks to update AGENTS.md, remember lessons, self-improve, preserve corrections, mine session/handoff/progress notes, preserve reusable review findings, document non-default commands, or fix duplicated, conflicting, stale, oversized, or poorly scoped agent instructions.
---

# Self Improve

Preserve reusable guidance for future agents. Make the smallest correct edit. Do not record one-off noise.

## Use When

- The user asks to update/refactor `AGENTS.md` or linked instruction docs.
- The user asks to remember lessons, corrections, workflows, commands, validation steps, gotchas, or repo quirks.
- Conversation context, session notes, handoffs, progress files, or similar artifacts may contain reusable guidance.
- Instruction files are duplicated, conflicting, stale, poorly scoped, or too large.

Do **not** use for temporary debugging notes, obvious facts, generic advice, or speculative rules.

## Workflow

1. **Find the instruction surface**
   - Activate or load the `subagent-model-router` skill and spawn a fast-tier subagent to find every `AGENTS.md` file:
     ```bash
     find . -name AGENTS.md -not -path './.git/*' -print
     ```
   - Read relevant `AGENTS.md` files and their directly linked instruction docs.
   - If none exist, create `./AGENTS.md` only when there is strong durable guidance or the user asked for it.

2. **Decide what to keep**
   - Keep guidance only if it is likely to recur, actionable, repo/workflow/user-specific, and not already documented.
   - Prefer exact commands, paths, validation steps, constraints, gotchas, reusable review findings, and human corrections.
   - For examples and artifact-mining rules, see `DURABLE_LEARNINGS.md`.

3. **Place it correctly**
   - Root `./AGENTS.md`: project-wide rules that should always load.
   - Scoped `./**/AGENTS.md`: directory/module-specific rules.
   - Linked docs: longer topic detail, procedures, examples, or rare branches.
   - If root already links a topic doc, update that doc instead of repeating the same guidance in root.
   - For refactor and placement rules, see `INSTRUCTION_STRUCTURE.md`.

4. **Edit minimally**
   - Use short, specific, actionable bullets.
   - Prefer one rule per line.
   - Remove duplication only after the destination has the rule.
   - Resolve contradictions instead of preserving both sides.
   - Do not add inverse rules from excluded noise.

5. **Report**
   - Say what durable guidance was found.
   - Say what files changed and why.
   - If no item clears the durable-learning bar, say so and make no changes.
   - If refactoring happened, mention moved guidance, deleted duplicates, resolved conflicts, and assumptions.
