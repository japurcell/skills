---
name: revise-agents-md
description: Update AGENTS.md files using concrete lessons from the just-completed session. Use this whenever a user asks to capture learnings, codify workflow discoveries, add recurring gotchas, or improve future-agent context in AGENTS.md (even if they do not explicitly mention this skill).
---

Review this session for durable learnings about working in the codebase. Propose concise AGENTS.md updates that improve future sessions, then apply only with user approval.

## Outcome

Produce a short, high-signal AGENTS.md update with:

- Only reusable guidance that likely helps future sessions
- Exact file target(s) for each addition
- Minimal, reviewable diffs before editing
- Explicit approval gate before applying changes

## Step 1: Extract durable learnings

What context was missing that would have helped me work more effectively?

- Bash commands that were used or discovered
- Code style patterns followed
- Testing approaches that worked
- Environment/configuration quirks
- Warnings or gotchas encountered

Filter out one-off incidents, temporary noise, and obvious facts.

If session context is partial or missing, do not stop at questions. Use best-effort assumptions based on available context and produce candidate updates anyway, clearly labeling assumptions.

## Step 2: Find AGENTS.md Files

```bash
find . -name "AGENTS.md" 2>/dev/null | head -20
```

If no AGENTS.md files exist:

- Say so clearly
- Propose creating `./AGENTS.md` with only the strongest 3-7 learnings
- Ask for approval before creating the file

Decide where each addition belongs:

| Type             | Location            | Purpose                                                      |
| ---------------- | ------------------- | ------------------------------------------------------------ |
| Project root     | `./AGENTS.md`       | Primary project context (checked into git, shared with team) |
| Package-specific | `./**/AGENTS.md`    | Module-level context in monorepos                            |
| Subdirectory     | Any nested location | Feature/domain-specific context                              |

## Step 3: Draft Additions

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

## Step 4: Present proposed edits

Show proposed changes grouped by file, with one-line rationale for each group.

Use this structure:

````markdown
### Update: <path-to-AGENTS.md>

Why this file: <one-line placement rationale>

```diff
+ <concise addition>
```
````

```

If no changes meet the quality bar, say that explicitly and do not force updates.

If context was incomplete, still provide grouped proposed edits using assumptions. Add a brief `Assumptions` subsection before diffs so the user can quickly correct them.

## Step 5: Approval gate

Ask whether to apply exactly the proposed edits.

- If approved: apply edits and summarize what changed
- If not approved: stop and ask what to adjust

Do not apply extra edits beyond the approved diff.

## Final response contract

In the final response, include:

1. `Findings`: 3-7 concise candidate learnings or a statement that none qualified
2. `Proposed updates`: grouped by AGENTS.md path with diff blocks
3. `Approval request`: one direct question asking whether to apply
4. `Assumptions` (only when needed): explicit assumptions used to produce best-effort proposals despite partial context
```
