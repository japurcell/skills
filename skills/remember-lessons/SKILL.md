---
name: remember-lessons
description: Capture session learnings into AGENTS.md and reorganize all AGENTS.md files for clarity. Use this skill whenever the user asks to update AGENTS.md with lessons learned, capture session discoveries, clean up or reorganize AGENTS.md files, do a retrospective update, or refresh agent instructions. Also use it when the user mentions "revise agents", "refactor agents.md", "codify learnings", "remember lessons learned", or wants to improve future-agent context in any way — even if they don't explicitly say "remember lessons".
---

# Remember Lessons Learned

## Overview

Capture durable session learnings into AGENTS.md, then reorganize all AGENTS.md files into a clean, minimal structure — all in one pass.

## When to Use

Use this skill when the goal is to improve future-agent context by recording durable learnings and/or cleaning up agent instruction files.

Use it when:

- The user asks to update `AGENTS.md`
- The user asks to capture lessons learned or codify discoveries
- The user asks to clean up, refactor, or reorganize `AGENTS.md`
- The session reveals reusable guidance, such as:
  - non-obvious commands
  - project conventions
  - recurring pitfalls
  - validation steps
  - important user corrections

## The Workflow

### Phase 0: Discover

Before drafting anything, build a picture of the current state.

1. Find all AGENTS.md files and any linked instruction docs:
   ```bash
   find . -name "AGENTS.md" 2>/dev/null | head -20
   ```
2. Read each file and all linked files. Map which rules live where, what's linked, and the current structure.
3. Detect contradictions — places where two rules conflict and can't both be followed.
4. Assess whether a structural refactor is warranted. Signals that it is:
   - Root AGENTS.md exceeds ~120 lines
   - Duplicated rules across files
   - Mixed scopes (domain-specific guidance sitting in root)
   - Orphan links or missing linked docs
   - User explicitly asked for cleanup or reorganization

If no AGENTS.md files exist, say so and propose creating `./AGENTS.md` with only the strongest learnings.

### Phase 1: Draft Learnings

Review the session for durable, reusable guidance. Ask: _what context was missing that would have helped me work more effectively?_

Look for:

- Bash commands that were used or discovered
- Code style patterns followed
- Testing approaches that worked
- Environment or configuration quirks
- Warnings or gotchas encountered
- Human interventions, re-directions or corrections

Filter out one-off incidents, temporary noise, and obvious facts.

**Keep each learning to one line** — AGENTS.md is part of the prompt, so brevity matters.

Format: `<command or pattern>` — `<brief description>`

Avoid:

- Verbose explanations
- Obvious information
- One-off fixes unlikely to recur

### Phase 2: Refactor

1. **Extract root essentials** — keep only guidance relevant to nearly every task:
   - One-sentence project description
   - Package manager (only if non-default or easily confused)
   - Non-standard build/typecheck/test commands
   - One or two universal workflow constraints

2. **Group and split** — move specialized content into topic files. Typical groups:
   - Workflow
   - Frontend conventions
   - Backend conventions
   - Validation/testing
   - Environment/secrets
   - Git/release process

   Use concise filenames. Keep each file focused on one topic.

3. **Flag deletion candidates** — call out instructions that are:
   - Redundant (covered elsewhere)
   - Non-actionable (too vague to change behavior)
   - Obvious boilerplate

### Phase 3: Produce final structure

Generate:

- Minimal root AGENTS.md with links
- Updated scoped AGENTS.md files where needed
- New/updated topic docs
- Suggested docs tree if folders do not exist yet

### Operating Principles

1. Keep root AGENTS.md short and always-load safe.
2. Prefer actionable rules over vague advice.
3. Preserve scope boundaries (root vs subdirectory AGENTS files).
4. Avoid duplicate guidance across files; link instead.
5. Do not silently resolve conflicts between instructions.

## Final response contract

In the final response, include:

1. `Findings`: list concise learnings or a statement that none qualified
2. `Applied updates`: grouped by AGENTS.md path with diff blocks
3. `Assumptions` (only when needed): explicit assumptions used to produce best-effort proposals despite partial context

## Quality Bar

- Root AGENTS.md should stay under ~120 lines
- Every linked file should have a clear purpose and no mixed scopes
- No orphan links
- No duplicated rule text unless duplication is explicitly justified
- New learnings are concise, actionable, and likely to recur
- If no changes meet the quality bar, say so explicitly — don't force updates

## Common Rationalizations

| Rationalization                                        | Reality                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------- |
| "The user only asked for a small edit."                | Small edits can still reinforce duplication, contradictions, or bad scope. |
| "I'll just add it to the root AGENTS.md."              | Root should stay minimal; scoped guidance belongs in focused files.        |
| "This is too minor to record."                         | Small corrections often reveal durable, reusable rules.                    |
| "I'll clean up the structure later."                   | Deferring cleanup compounds clutter and duplication.                       |
| "I can merge conflicting rules into one."              | Do not silently resolve conflicts; surface them explicitly.                |
| "The root file is enough for this change."             | Linked docs may contain scope-defining guidance.                           |
| "That command is obvious."                             | Non-default commands are often exactly what future agents need.            |
| "The user didn't explicitly ask me to remember this."  | Capture durable guidance even when the request is implicit.                |
| "Broader wording is safer."                            | Vague rules are less useful than specific, actionable ones.                |
| "Leaving redundant rules is harmless."                 | Redundancy creates drift and inconsistency.                                |
| "I should make some update even if nothing qualifies." | Do not force low-value changes.                                            |

## Red Flags

- Root `AGENTS.md` is missing, empty, or overly long
- Files mix global and scoped guidance
- Rules are duplicated across files
- Linked docs are missing, stale, or orphaned
- Rules are vague or non-actionable
- Durable learnings from the session were not captured
- Non-standard commands or validation steps are undocumented
- User corrections were not preserved
- One-off incidents were added as standing instructions
- Conflicting rules exist and were not called out
- An AGENTS.md file was edited without checking related files
- Redundant or obsolete guidance was added but not pruned

## Verification

Before concluding, confirm:

- [ ] All relevant `AGENTS.md` files were found
- [ ] Linked instruction files were reviewed
- [ ] Durable learnings were identified
- [ ] One-off and low-value items were excluded
- [ ] Root `AGENTS.md` stays minimal
- [ ] Scoped guidance was placed in the right file
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced explicitly
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
- [ ] Final response includes findings, applied updates, and assumptions when needed
