---
name: remember-lessons
description: Capture session learnings into AGENTS.md and reorganize all AGENTS.md files for clarity. Use this skill whenever the user asks to update AGENTS.md with lessons learned, capture session discoveries, clean up or reorganize AGENTS.md files, do a retrospective update, or refresh agent instructions. Also use it when the user mentions "revise agents", "refactor agents.md", "codify learnings", "remember lessons learned", or wants to improve future-agent context in any way — even if they don't explicitly say "remember lessons".
---

# Remember Lessons Learned

Capture durable session learnings into AGENTS.md, then reorganize all AGENTS.md files into a clean, minimal structure — all in one pass.

## Core Workflow

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

| Rationalization                 | Reality                 |
| ------------------------------- | ----------------------- |
| Excuse agents use to skip steps | Why the excuse is wrong |

## Red Flags

- Root AGENTS.md does not exist or is empty
- Any AGENTS.md file exceeds ~120 lines
- Duplicated rules across files
- Orphan links or missing linked docs
- Undocumented or new command was not captured as a learning
- Human interventions, corrections or re-directions were not captured as learnings

## Verification

After completing the skill's process, confirm:

- [ ] Checklist of exit criteria
- [ ] Evidence requirements
