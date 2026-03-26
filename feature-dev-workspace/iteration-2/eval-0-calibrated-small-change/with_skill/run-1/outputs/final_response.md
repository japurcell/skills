I inspected [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md). The main issue is that the skill already says “medium-to-large,” but its trigger text and Light Track still invite smaller, well-bounded feature work. I would tighten the trigger at the frontmatter first, then make the process language match it.

I would make these changes:

1. Replace the frontmatter `description` with something narrower and more explicit about thresholds. I would use:

```md
description: Structured feature development for medium-to-large feature work that spans multiple files, subsystems, or decisions. Use this when the task requires meaningful codebase exploration, non-trivial implementation planning, architecture trade-offs, or coordination across multiple moving parts. Do not use it for small scoped changes, isolated edits, or fully specified work that can be implemented directly.
```

2. Tighten the Light Track so it covers only the smallest work that is still in scope for this skill. Right now it says “well-bounded medium-sized changes,” which is exactly the kind of phrasing that will still trigger on calibrated small-change requests. I would change that paragraph to something like:

```md
Use for the smallest requests that still justify this skill: bounded multi-file feature work where the scope is clear, but understanding local patterns and integration points still matters.
```

3. Update the Phase 1 track-selection bullets so they reinforce the same boundary. I would change:
   - `Light for well-bounded medium-sized feature work`
   - `Standard for medium feature work`

   to:
   - `Light for bounded multi-file feature work that still needs discovery`
   - `Standard for broader medium-to-large feature work with real design choices`

4. Keep the existing `## When Not To Use This Skill` section, but shorten and sharpen it instead of adding a second one. The repo already has that section near the end of the file, so the right change is a rewrite, not an insertion. I would replace it with:

```md
## When Not To Use This Skill

Do not use this skill for:

1. Small or local changes that can be implemented directly
2. One-file edits or tightly scoped bug fixes
3. Fully specified tasks with no real design or discovery work
4. Pure review, brainstorming, or documentation-only requests
```

I would not make broader structural changes. The current skill already has the right overall shape; it just has a boundary problem. The frontmatter description is the highest-leverage fix because that is the primary trigger surface, and the Light Track wording is the second fix because it currently legitimizes smaller work. The “When Not To Use” section should stay short and act as a backstop, not carry the whole burden of trigger control.
