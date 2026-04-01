# Response

## Understanding

**Track: Light** — This is a focused skill-file edit with clear, enumerated requirements and no systemic ambiguity. I can inspect the current skill, map each requested change to a precise edit location, and describe exactly what I'd do without a long design phase.

---

## Relevant Findings

I inspected `skills/feature-dev/SKILL.md`. Here is what the current skill already does well and where the gaps are:

### Already present

| Requirement                               | Location in current skill                                                                           | State                                                                                                                                                                                          |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TDD in implementation                     | Phase 5, step 3: _"Always use the tdd skill to implement with an explicit red-green-refactor loop"_ | Present, but phrased as a bullet, easy to overlook                                                                                                                                             |
| Quality review in an independent subagent | Phase 6, step 1: _"Always run independent code-reviewer agents"_                                    | Present and explicit                                                                                                                                                                           |
| Medium-to-large framing in description    | Frontmatter `description` field                                                                     | Partially present ("medium-to-large changes") but the **Light Track** definition contradicts it by accepting "well-bounded medium-sized changes" — which effectively keeps small work in scope |

### Gaps requiring changes

1. **Trigger scope is too broad.** The frontmatter description says "medium-to-large" but the Light Track definition opens the door to small, well-bounded work. The description and Light Track need to be tightened together so the skill is consistently limited to medium-to-large scope.

2. **No "When not to use this skill" section.** A dedicated exclusion list is absent. The only exclusion today is a single sentence buried in the frontmatter description.

3. **code-simplifier is never mentioned.** Refactoring via `code-simplifier` in a subagent is not part of Phase 5 or Phase 6. It needs to be added as an explicit step.

4. **TDD mandate is present but weak.** It's step 3 of 7 in Phase 5, phrased identically to every other bullet. It should be foregrounded as a hard requirement, not a soft step.

---

## Recommendation

Four targeted edits, all within `SKILL.md`:

### Edit 1 — Tighten the frontmatter description

**Current:**

```
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a reusable handoff plan for another agent. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
```

**Replace with:**

```
description: Structured feature development for medium-to-large changes. Use this when the user wants to add a non-trivial feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a handoff plan. Do not use it for small or well-bounded changes, bug fixes, isolated one-file edits, refactors under 50 lines, or requests that are already fully specified and ready for direct implementation.
```

**Rationale:** Removes "unfamiliar codebases" (which implies small tasks in new code are fine), firms up the exclusion boundary, and adds the "refactors under 50 lines" exclusion to prevent the skill from being invoked for trivially small edits.

---

### Edit 2 — Add "When not to use this skill" section

Insert immediately after the `# Feature Development` heading and the opening paragraph, before `## Core Principles`:

```markdown
## When Not to Use This Skill

- Small or well-scoped changes that touch one or two files
- Bug fixes, typo corrections, or isolated patches
- Refactors under ~50 lines that don't touch architecture
- Requests where requirements are fully specified and no exploration is needed
- Greenfield scripts or tooling with no existing codebase to explore

For those, implement directly without invoking this skill.
```

---

### Edit 3 — Tighten the Light Track definition to exclude small work

**Current Light Track opening:**

```
Use for the smallest in-scope feature work: well-bounded medium-sized changes where the main risk is understanding local code context rather than resolving product ambiguity.
```

**Replace with:**

```
Use for medium-sized feature work that is well-bounded, touches a modest number of files, and has low ambiguity. The risk is primarily understanding local code context rather than resolving product unknowns.
```

**Rationale:** Removes "smallest in-scope feature work" language, which implicitly invited small tasks in. Now Light Track clearly starts at medium.

---

### Edit 4 — Make TDD a hard requirement and add code-simplifier refactor step in Phase 5

**Current Phase 5 actions (relevant excerpt):**

```
1. Read all relevant files identified in previous phases
2. Implement following the chosen approach
3. Always use the tdd skill to implement with an explicit red-green-refactor loop
4. Follow codebase conventions strictly
5. Write clean, maintainable code
6. Update todos as you progress
7. If you are not implementing yet, produce or update the handoff artifact before stopping
```

**Replace with:**

```
> **Required**: All implementation MUST follow a TDD red-green-refactor loop using the `tdd` skill. There are no exceptions.

1. Read all relevant files identified in previous phases
2. Implement following the chosen approach using the tdd skill (red → green → refactor)
3. After tests pass and the feature is working, launch a [code-simplifier](../code-simplifier/SKILL.md) subagent to review and simplify the changed code for clarity, DRY-ness, and elegance — treat its output as a required refactor pass, not optional polish
4. Apply simplifications that do not change behavior or test coverage
5. Follow codebase conventions strictly
6. Update todos as you progress
7. If you are not implementing yet, produce or update the handoff artifact before stopping
```

**Rationale:** Elevates TDD from a bullet to a bold required block at the top of the phase so it can't be missed. Adds code-simplifier as an explicit subagent step after green tests, with a clear instruction that its output is mandatory rather than optional.

---

## Open Questions

None blocking. The request is concrete enough to implement directly.

The only judgment call is the ~50 line threshold in the description and the "When not to use" section. I've chosen a round number that's easy to apply; if you want a different heuristic (e.g., "single function", "one class", "one PR commit"), that's a one-word swap.

---

## Implementation Map

All changes are in one file: `skills/feature-dev/SKILL.md`

| Edit | Location                                             | Type    |
| ---- | ---------------------------------------------------- | ------- |
| 1    | Frontmatter `description` field                      | Replace |
| 2    | After opening paragraph, before `## Core Principles` | Insert  |
| 3    | Light Track first sentence                           | Replace |
| 4    | Phase 5 actions block                                | Replace |

Ready to apply immediately on your go-ahead — or I can do it now if you'd prefer.
