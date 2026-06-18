---
name: self-improve
description: Capture durable session learnings in AGENTS.md files. When requested or clearly warranted, also refactor AGENTS.md structure to reduce duplication, fix scope, and keep linked docs in sync. Use this skill when the user asks to update AGENTS.md, record lessons learned, codify discoveries, or clean up/refactor agent instructions.
---

# Self Improve

Capture durable, reusable session learnings in the correct `AGENTS.md` files. If requested or clearly warranted, also refactor agent instructions. Never remove guidance unless it is low-value or moved to an existing or new linked doc in the same change.

Use `SELF_IMPROVE_REFERENCE.md` for refactor judgment, red flags, and common failure modes.

## Workflow

### Phase 0: Extract durable learnings

Review the session and ask: _what missing context would help future agents?_

Look for:

- Bash commands used or discovered
- Code style or implementation patterns
- Test, validation, build, or typecheck steps
- Environment/configuration quirks
- Warnings, gotchas, or non-obvious constraints
- Human corrections or redirects

Exclude temporary noise and obvious facts.

### Phase 1: Find files and map rules

1. Invoke `subagent-model-router`.
2. Find `AGENTS.md` files using a fast-tier subagent:

   ```bash
   find . -name "AGENTS.md" 2>/dev/null | head -20
   ```

3. Read each `AGENTS.md`.
4. Read any directly linked docs that exist.
5. Build a quick map of where rules live.

If no `AGENTS.md` exists:

- Say so.
- Create `./AGENTS.md` with only the strongest 3-7 learnings.

Placement:

- `./AGENTS.md` - project-wide guidance
- `./**/AGENTS.md` - scoped/module/subdirectory guidance
- Linked docs - detailed topic guidance referenced from `AGENTS.md`

### Phase 2: Apply additions

Add concise, durable guidance to the right file.

Rules:

- One line per concept when possible
- Prefer specific, actionable rules
- Keep `AGENTS.md` brief because it is prompt-loaded
- Use `<command or pattern>` - `<brief description>` when helpful

Prioritize guidance that is recurring, actionable, and specific.

Avoid:

- Verbose explanation
- Obvious facts

### Phase 3: Refactor

Signals:

- Root `AGENTS.md` is over ~120 lines
- Duplicated rules
- Contradictory rules
- Mixed global and scoped guidance
- Missing, stale, or orphaned linked docs
- User asked for cleanup or reorganization

If not warranted, skip to Phase 4.

Refactor steps:

1. **Resolve contradictions** - if two rules cannot both be followed, keep one and explain why.
2. **Trim root** - keep only near-universal guidance:
   - One-sentence project description
   - Package manager if non-default or easy to confuse
   - Non-standard build, typecheck, or test commands
   - One or two universal workflow constraints
3. **Group by scope/topic** - move specialized guidance into scoped `AGENTS.md` files or linked docs.
4. **Keep docs in sync** - add moved guidance to the destination doc in the same change before deleting the source text.
5. **Delete only true low-value content**:
   - Redundant
   - Non-actionable
   - Obvious boilerplate
   - Superseded by a resolved contradiction
6. **Finalize structure**:
   - Minimal root `AGENTS.md` with links
   - Updated scoped `AGENTS.md` files
   - New or updated linked docs as needed
   - Fixed or removed orphan links

### Phase 4: Report changes

In the final response include:

**Always**

1. **Learnings** - concise list, or say none qualified
2. **Applied updates** - grouped by file path, with diff blocks
3. **Assumptions** - only if needed

**If refactor was performed**:

4. **Contradictions** - summary, sources, chosen rule, reason
5. **Deletions** - deleted text, reason, original location
6. **Moved guidance** - source location -> destination file for every moved rule
7. **Grouped files** - each scoped/topic file and what it owns
8. **Folder structure** - tree view if new folders were created

## Quality Bar

- Root `AGENTS.md` stays under ~120 lines and safe to always load
- Scope stays clean across root, scoped `AGENTS.md`, and linked docs
- No orphan links
- No duplicated guidance unless explicitly justified
- Prefer linking over repeating
- New learnings are concise, actionable, and likely to recur
- Guidance removed from one file must appear in its new destination or be reported as deleted
- If nothing meets the bar, say so and make no changes

## Verification

Before concluding, confirm:

**Always**

- [ ] All relevant `AGENTS.md` files were found
- [ ] Directly linked docs were reviewed
- [ ] Durable learnings were placed in the right files
- [ ] One-off and low-value items were excluded
- [ ] Assumptions were stated when needed

**If refactor was performed**

- [ ] Root `AGENTS.md` remains minimal
- [ ] Scoped guidance is in the right file
- [ ] Every moved rule was added to its destination doc in the same change
- [ ] Deletions were applied only where appropriate
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced and resolved
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
