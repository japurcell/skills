# Response: Tighten the feature-dev skill

## Inspection summary

After reading `/skills/feature-dev/SKILL.md`, here is the status of each requested change:

| Requested change                              | Current state                                                                                                                                                                             |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Only trigger for medium-to-large feature work | Partially done. The frontmatter description says "medium-to-large changes" but the exclusion list doesn't call out "small features" explicitly.                                           |
| Add "When not to use this skill" section      | **Missing** — no such section exists.                                                                                                                                                     |
| Implementation always requires TDD            | Already done — Phase 5 says "Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it." |
| code-simplifier as subagent for refactoring   | Already done — Phase 6 says "Always launch an independent code-simplifier subagent to identify refactoring opportunities after implementation."                                           |
| Quality review in independent subagent        | Already done — Phase 6 says "Always run independent code-reviewer agents for quality review on every track."                                                                              |

**Two changes are needed.** The rest already matches what was requested.

---

## Change 1 — Tighten the frontmatter description

**File**: `skills/feature-dev/SKILL.md`, `description:` field.

Current exclusion clause:

> Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.

Replace with:

> Do not use it for small features, tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.

Adding "small features" closes the gap: someone describing a small feature addition today would find nothing in the exclusion list that covers them, so the extension hint and VS Code description matching would still pull this skill in. The single added phrase gates that case out.

---

## Change 2 — Add a "When Not to Use This Skill" section

Insert the following section immediately after the `## Core Principles` block and before `## Process Selection`:

```markdown
## When Not to Use This Skill

- **Small or single-file changes** — a one-file edit, a minor tweak, or a small self-contained addition does not need discovery, design, or review phases.
- **Pure bug fixes** — debugging and patching a known defect is better handled directly or with the tdd skill alone.
- **Fully specified, no-ambiguity tasks** — if every implementation detail is already decided and no codebase exploration is needed, skip this workflow and implement directly.
- **Tasks that don't require exploration or design** — if you already know the exact files to change and the changes to make, this skill adds overhead without value.
```

This makes the scope visible at a glance without burying it in the description frontmatter. Readers land here before reaching the process tracks and can bail out early.

---

## No questions

The request is concrete. Nothing here is blocking. Both changes are small and local; the rest of the skill already satisfies the TDD, code-simplifier, and independent-reviewer requirements.
