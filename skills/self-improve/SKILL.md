---
name: self-improve
description: Captures durable session learnings in the right `AGENTS.md` files and refactors instruction structure when needed to remove duplication, fix scope, and keep linked docs in sync. Use when the user asks to update `AGENTS.md`, record lessons learned, codify repo-specific commands or gotchas, preserve human corrections, clean up agent instructions, or says things like "remember this", "document this workflow", or "make future agents know this."
---

# Self Improve

## Overview

Capture only durable guidance future agents will reuse. Update the smallest correct `AGENTS.md` surface first; refactor structure only when the current layout would cause drift, duplication, or bad scoping.

Use `SELF_IMPROVE_REFERENCE.md` for refactor judgment, placement examples, rationalizations, and failure modes.

## When to Use

- The user asks to update or refactor `AGENTS.md`, record lessons learned, or preserve a workflow/discovery.
- The session surfaced non-default commands, validation steps, code patterns, environment quirks, warnings, or human corrections worth reusing.
- Current `AGENTS.md` structure is duplicated, conflicting, stale, or poorly scoped.
- Not for one-off notes, obvious facts, speculative advice, or transient debugging noise.

## Workflow

1. **Qualify learnings**
   - Ask: _what missing context would help future agents?_
   - Keep only items likely to recur, actionable, repo/user-specific, and not already documented.
   - Look for non-default commands, code patterns, validation/build/typecheck steps, environment quirks, warnings, and human corrections.
   - Never turn excluded noise into an inverse standing rule.
   - Exclude temporary noise and obvious facts.

2. **Map the instruction surface**
   - Find every relevant `AGENTS.md`, then read each one plus any directly linked docs.
   - If the search is large, invoke `subagent-model-router` and use a cheap finder subagent.
   - If no `AGENTS.md` exists, say so and create `./AGENTS.md` with only the strongest 3-7 learnings.

3. **Apply the smallest correct update**
   - Put project-wide rules in `./AGENTS.md`, scoped rules in the nearest `./**/AGENTS.md`, and long topic detail in linked docs.
   - Keep prompt-loaded files brief. Prefer one line per concept and specific, actionable wording.
   - Use `<command or pattern>` - `<brief description>` when that makes the rule easier to scan.

4. **Refactor only when warranted**
   - Do it when root `AGENTS.md` is over ~120 lines, scope is mixed, rules duplicate or conflict, linked docs are stale/orphaned, or the user asked for cleanup.
   - Resolve contradictions first.
   - Keep root limited to near-universal guidance: short project description, non-default package manager, non-standard build/test/typecheck commands, and one or two universal workflow constraints.
   - Move specialized guidance into scoped `AGENTS.md` files or linked docs, and update the destination in the same change before deleting the source text.
   - Delete only content that is redundant, non-actionable, obvious boilerplate, or superseded by a resolved contradiction.

5. **Report the outcome**
   - If nothing clears the durable-learning bar, say so and make no changes.
   - Always report learnings, applied updates, and assumptions when needed.
   - If refactoring happened, also report contradictions resolved, deletions, moved guidance, grouped files, and any new folder structure.

## Specific Techniques

### Durable-learning filter

Keep:

- Non-default commands
- Build, test, validation, or typecheck steps
- Repo-specific patterns or constraints
- Environment/configuration quirks
- Warnings and gotchas
- Repeated human corrections

Skip:

- Temporary debugging notes
- Facts obvious from the tree or README
- Navigation/process heuristics inferred from one run unless the user wants them as standing policy
- Generic reminders like "be careful"

### Placement

- `./AGENTS.md` - near-universal project rules
- `./**/AGENTS.md` - directory/module rules
- Linked docs - longer topic detail referenced from `AGENTS.md`

### Refactor floor

Keep root `AGENTS.md` minimal and safe to always load. Prefer linking over repeating. Never remove guidance unless it is low-value or moved to its new destination in the same change.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The root file is enough." | Scoped files or linked docs may own the rule better. |
| "That command is obvious." | Non-default commands are often high-value. |
| "The user didn't ask me to remember this." | Capture durable guidance when warranted. |
| "Leaving redundant rules is harmless." | Redundancy causes drift. |
| "I moved it, so deleting the old text is enough." | Verify the destination was updated in the same change. |
| "I should update something anyway." | Do not force low-value changes. |

## Red Flags

- Missing, empty, or overly long root `AGENTS.md`
- Mixed global and scoped guidance
- Duplicate or conflicting rules
- Missing, stale, or orphaned linked docs
- Vague or non-actionable rules
- Durable learnings not captured
- One-offs added as standing instructions
- Guidance removed from one file without appearing in its destination

## Verification

- [ ] All relevant `AGENTS.md` files were found
- [ ] Directly linked docs were reviewed
- [ ] Durable learnings were placed in the right files
- [ ] One-off and low-value items were excluded
- [ ] Assumptions were stated when needed
- [ ] Root `AGENTS.md` remains minimal
- [ ] Scoped guidance is in the right file
- [ ] Every moved rule was added to its destination doc in the same change
- [ ] Deletions were applied only where appropriate
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced and resolved
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
