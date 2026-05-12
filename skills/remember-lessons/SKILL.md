---
name: remember-lessons
description: Capture durable session learnings into AGENTS.md and reorganize AGENTS.md files. Use this skill whenever the user asks to update AGENTS.md with lessons learned, capture session discoveries, clean up or reorganize AGENTS.md files, do a retrospective update, or refresh agent instructions. Also use it when the user mentions "revise agents", "refactor agents.md", "codify learnings", or "remember lessons learned".
---

# Remember Lessons Learned

Capture durable session learnings into AGENTS.md, then reorganize all AGENTS.md files into a clean, minimal structure — all in one pass.

## The Workflow

### Phase 0: Extract durable learnings

Review the session for durable, reusable guidance. Ask: _what context was missing that would have helped me work more effectively?_

Look for:

- Bash commands that were used or discovered
- Code style patterns followed
- Testing approaches that worked
- Environment or configuration quirks
- Warnings or gotchas encountered
- Human interventions, re-directions or corrections

Filter out one-off incidents, temporary noise, and obvious facts.

If session context is partial or missing, do not stop at questions. Use best-effort assumptions based on available context and produce candidate updates anyway, clearly labeling assumptions.

### Phase 1: Find AGENTS.md Files

1. Find all AGENTS.md files:
   ```bash
   find . -name "AGENTS.md" 2>/dev/null | head -20
   ```
2. Read each file and any linked topic docs.
3. Read currently linked instruction docs if they exist.
4. Build a quick map of where each rule currently lives.

If no AGENTS.md files exist:

- Say so clearly
- Propose creating `./AGENTS.md` with only the strongest 3-7 learnings

Decide where each addition belongs:

| Type             | Location            | Purpose                                                      |
| ---------------- | ------------------- | ------------------------------------------------------------ |
| Project root     | `./AGENTS.md`       | Primary project context (checked into git, shared with team) |
| Package-specific | `./**/AGENTS.md`    | Module-level context in monorepos                            |
| Subdirectory     | Any nested location | Feature/domain-specific context                              |

### Phase 2: Apply Additions

Apply durable learnings as concise additions to identified file(s).

**Keep it concise** - one line per concept. AGENTS.md is part of the prompt, so brevity matters.

Format: `<command or pattern>` - `<brief description>`

Prioritize additions that are:

- Recurring: likely to matter again in future tasks
- Actionable: directly changes what an agent should do
- Specific: concrete command, file pattern, or decision rule

Avoid:

- Verbose explanations
- Obvious information
- One-off fixes unlikely to recur

### Phase 3: Refactor

Produce a minimal root AGENTS.md that contains only globally essential guidance, then move all specialized guidance into linked, topic-specific files.

1. **Detect contradictions** — places where two rules conflict and can't both be followed. Use your best judgment to pick one to keep, then flag the other for deletion.

2. **Assess whether a structural refactor is warranted**. Signals that it is:
   - Root AGENTS.md exceeds ~120 lines
   - Duplicated rules across files
   - Contradictory rules across files
   - Mixed scopes (domain-specific guidance sitting in root)
   - Orphan links or missing linked docs
   - User explicitly asked for cleanup or reorganization

3. **Extract root essentials** — keep only guidance relevant to nearly every task:
   - One-sentence project description
   - Package manager (only if non-default or easily confused)
   - Non-standard build/typecheck/test commands
   - One or two universal workflow constraints

4. **Group and split** — move specialized content into topic files. Typical groups:
   - Workflow
   - Frontend conventions
   - Backend conventions
   - Validation/testing
   - Environment/secrets
   - Git/release process

   Use concise filenames. Keep each file focused on one topic.

5. **Extract deletion candidates** — call out instructions that are:
   - Redundant (covered elsewhere)
   - Non-actionable (too vague to change behavior)
   - Obvious boilerplate
   - Contradictory flagged for deletion

6. **Produce final structure**:
   - Minimal root AGENTS.md with links
   - Updated scoped AGENTS.md files where needed
   - New/updated topic docs
   - Docs tree if folders do not exist yet

### Phase 4: Report final changes and assumptions

In the final response, include:

1. **Learnings**: list concise learnings or a statement that none qualified
2. **Applied updates**: grouped by AGENTS.md or topic docs path with diff blocks
3. **Contradictions**: For each contradiction:
   - Conflict summary
   - Source A (file + short quote)
   - Source B (file + short quote)
   - Version chosen and reason
4. **Deletions**: List deleted text, reason, and original location
5. **Grouped files**: List each topic file and what rules it now owns
6. **Folder structure**: If new folders were created, show the new structure in a tree-style layout
7. **Assumptions** (only when needed): explicit assumptions used to produce best-effort proposals despite partial context

### Operating Principles

1. Keep root AGENTS.md short and always-load safe.
2. Prefer actionable rules over vague advice.
3. Preserve scope boundaries (root vs subdirectory AGENTS files).
4. Avoid duplicate guidance across files; link instead.

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
| "I can't decided which conflicting rule to keep."      | Use your best judgment to pick one. The human can review later.            |
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
- Conflicting rules exist and were not resolved
- An AGENTS.md file was edited without checking related files
- Redundant or obsolete guidance was added but not pruned

## Verification

Before concluding, confirm:

- [ ] All relevant `AGENTS.md` files were found
- [ ] Linked instruction files were reviewed
- [ ] Durable learnings were applied to the right files
- [ ] Deletion candidates were applied where appropriate
- [ ] One-off and low-value items were excluded
- [ ] Root `AGENTS.md` stays minimal
- [ ] Scoped guidance was placed in the right file
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced explicitly and resolved
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
- [ ] Final response includes all required sections (learnings, updates, contradictions, deletions, grouped files, folder structure, assumptions)
