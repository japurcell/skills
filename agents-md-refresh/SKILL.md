---
name: agents-md-refresh
description: Capture session learnings into AGENTS.md and reorganize all AGENTS.md files for clarity. Use this skill whenever the user asks to update AGENTS.md with lessons learned, capture session discoveries, clean up or reorganize AGENTS.md files, do a retrospective update, or refresh agent instructions. Also use it when the user mentions "revise agents", "refactor agents.md", "codify learnings", or wants to improve future-agent context in any way — even if they don't explicitly say "refresh".
---

# AGENTS.md Refresh

Capture durable session learnings into AGENTS.md, then conditionally reorganize all AGENTS.md files into a clean, minimal structure — all in one pass.

## How It Works

Three phases, but only the first two always run. The refactor phase activates only when the files actually need structural cleanup.

### Phase 0: Discover

Before drafting anything, build a picture of the current state.

1. Find all AGENTS.md files and any linked instruction docs:
   ```bash
   find . -name "AGENTS.md" 2>/dev/null | head -20
   ```
2. Read each file. Map which rules live where, what's linked, and the current structure.
3. Detect contradictions — places where two rules conflict and can't both be followed.
4. Assess whether a structural refactor is warranted. Signals that it is:
   - Root AGENTS.md exceeds ~120 lines
   - Duplicated rules across files
   - Mixed scopes (domain-specific guidance sitting in root)
   - Orphan links or missing linked docs
   - User explicitly asked for cleanup or reorganization

If no AGENTS.md files exist, say so and propose creating `./AGENTS.md` with only the strongest learnings.

### Phase 1: Draft Learnings

Review the session for durable, reusable guidance. Ask: *what context was missing that would have helped me work more effectively?*

Look for:
- Bash commands that were used or discovered
- Code style patterns followed
- Testing approaches that worked
- Environment or configuration quirks
- Warnings or gotchas encountered

Filter out one-off incidents, temporary noise, and obvious facts.

**Keep each learning to one line** — AGENTS.md is part of the prompt, so brevity matters.

Format: `<command or pattern>` — `<brief description>`

Prioritize additions that are:
- **Recurring**: likely to matter in future tasks
- **Actionable**: directly changes what an agent should do
- **Specific**: concrete command, file pattern, or decision rule

If the refactor phase will run, draft learnings into their likely post-refactor locations (e.g., a testing learning targets the testing topic file, not root). If no refactor is needed, target existing files directly.

If session context is partial, use best-effort assumptions and label them clearly.

### Phase 2: Refactor (conditional)

Only run this phase when discovery found structural problems or the user explicitly asked for reorganization. Skip it when the files are already clean and new learnings fit neatly.

When it runs:

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

### Operating Principles

1. Keep root AGENTS.md short and always-load safe.
2. Prefer actionable rules over vague advice.
3. Preserve scope boundaries (root vs subdirectory AGENTS files).
4. Avoid duplicate guidance across files; link instead.
5. Do not silently resolve conflicts between instructions.

## Presenting Results

Structure the output so the user can clearly distinguish new content from reorganization.

### A. Contradictions (only if found)

For each conflict:
1. Conflict summary
2. Source A (file + short quote)
3. Source B (file + short quote)
4. Question: "Which version should I keep?"

If contradictions exist, pause and resolve them before showing the rest.

### B. New Learnings

List each proposed learning with its target file:

````markdown
### Target: <path-to-file>

```diff
+ <concise addition>
```
````

### C. Structural Changes (only if refactoring)

- Proposed root AGENTS.md content
- List of topic files and what rules each now owns
- Suggested folder structure (tree layout)
- Deletion candidates with reasons

### D. Combined Preview

Show the final state — what the files will look like after both learnings and structural changes are applied together. This is what the user is actually approving.

## Approval Gate

One clear question: apply these changes?

- If approved: apply all edits and summarize what changed
- If declined: ask what to adjust

Do not apply edits beyond the approved set.

## Quality Bar

- Root AGENTS.md should stay under ~120 lines
- Every linked file should have a clear purpose and no mixed scopes
- No orphan links
- No duplicated rule text unless duplication is explicitly justified
- New learnings are concise, actionable, and likely to recur
- If no changes meet the quality bar, say so explicitly — don't force updates
