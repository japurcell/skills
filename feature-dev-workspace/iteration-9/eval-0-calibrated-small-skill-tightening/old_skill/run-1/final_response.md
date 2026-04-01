# Response: Tighten the feature-dev Skill

## Understanding

This is a well-bounded skill-file update. I'll use the **Light Track** — the scope is clear, it touches one primary file, and the required changes are specific enough to execute without ambiguity.

---

## Relevant Findings

After reading `SKILL.md`:

1. **Description already says "medium-to-large"** — The frontmatter ends with: "Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation." The intent is there but the exclusions are buried in the `description` field — not visible as a scannable section.

2. **No "When not to use" section in the body** — There is no dedicated heading for negative guidance. Readers skimming the skill body will miss the exclusion criteria entirely.

3. **TDD is already required in Phase 5** — Step 3 already reads: "Always use the tdd skill to implement with an explicit red-green-refactor loop." ✓ No change needed.

4. **`code-simplifier` is missing** — The refactor leg of TDD has no instruction to invoke `code-simplifier` as a subagent. Phase 5 goes straight from implementation to quality review with no dedicated simplification step.

5. **Quality review already uses an independent subagent** — Phase 6, Step 1 reads: "Always run independent `code-reviewer` agents for quality review on every track." ✓ No change needed.

**Gaps requiring action:**

- No scannable "When not to use" section
- `code-simplifier` subagent missing from the refactor step

---

## Open Questions

None blocking. The request is fully specified.

---

## Recommendation

Three targeted edits — no structural rework:

### Edit 1 — Sharpen the frontmatter `description`

Make the medium-to-large scope and the anti-cases explicit and direct:

```
description: Structured feature development for medium-to-large changes. Use when the task needs codebase exploration, architecture decisions, multi-file implementation, or a reusable handoff plan for another agent. Skip it for small or single-file edits, straightforward well-specified tasks, or bug fixes with no design work.
```

### Edit 2 — Add "When not to use this skill" section

Insert immediately after the opening paragraph (before `## Core Principles`) so readers hit it early:

```markdown
## When not to use this skill

- Small or single-file edits that need no exploration
- Bug fixes where the cause and fix are already identified
- Requests that are fully specified and can go directly to implementation with no design work
- Greenfield scaffolding tasks better handled by a dedicated workspace-creation workflow
```

### Edit 3 — Add `code-simplifier` subagent to Phase 5

After the existing TDD step (step 3), insert a new step 4 and renumber the rest:

```markdown
4. After tests pass, launch a [code-simplifier](../code-simplifier/SKILL.md) subagent on the impacted files to surface refactoring opportunities before closing the implementation turn
```

This makes the red-green-refactor loop concrete: red (failing tests) → green (passing tests) → refactor (code-simplifier subagent results reviewed and applied) → Phase 6 quality review.

---

## Implementation Map

**File:** `skills/feature-dev/SKILL.md`

| #   | Location                                           | Change                                                                   |
| --- | -------------------------------------------------- | ------------------------------------------------------------------------ |
| 1   | Frontmatter `description` field                    | Sharpen to call out medium-to-large scope explicitly and name anti-cases |
| 2   | After intro paragraph, before `## Core Principles` | Add `## When not to use this skill` (4 bullets)                          |
| 3   | Phase 5, after step 3                              | Add step 4: launch `code-simplifier` subagent post-green for refactoring |

Phase 6's independent `code-reviewer` subagent requirement is already in place — no change needed there.
