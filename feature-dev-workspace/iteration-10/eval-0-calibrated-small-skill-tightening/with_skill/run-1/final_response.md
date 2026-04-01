# Response

**Track**: Light — the request is well-bounded, the skill is already read, and the changes are small edits to a single markdown file. No blocking questions.

---

## Understanding

You want four concrete improvements to the feature-dev skill:

1. Tighten trigger / scope so the skill only activates for medium-to-large work
2. Add an explicit "When not to use this skill" section
3. Guarantee TDD is non-optional for every implementation
4. Lock in code-simplifier-as-subagent and independent quality-review-subagent

After reading the current skill end-to-end, here is what I found and exactly what I'd change.

---

## Relevant Findings

| Concern                                | Current state                                                                                                                                                |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Trigger tightness                      | Description says "medium-to-large" but also says "Use this whenever the user wants to add a feature" — that phrase is too broad and could capture small work |
| "When not to use" section              | Not present as a named section; exclusions live only in one line of the frontmatter description                                                              |
| TDD                                    | Present in Phase 5, step 3, with strong language ("required … do not bypass it") — but **not** in Core Principles, so it is easy to miss on a first skim     |
| code-simplifier as subagent            | Phase 6 step 1 already reads "Always launch an independent [code-simplifier] subagent" — wording is correct                                                  |
| Quality review as independent subagent | Phase 6 step 2 already reads "Always run independent [code-reviewer] agents" — wording is correct                                                            |

**Net**: two real gaps (trigger language, missing "When not to use" section) and one placement issue (TDD belongs in Core Principles, not only buried in Phase 5). Items 4 and 5 are already correct; no changes needed there beyond the confirmation above.

---

## Recommendation — Exact Changes

### Change 1 — Tighten the frontmatter `description`

**Old text (frontmatter):**

```
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a reusable handoff plan for another agent. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
```

**New text:**

```
description: Structured feature development for medium-to-large changes. Use when the feature touches multiple files or components, requires codebase exploration, involves real design decisions, or needs a coordinated implementation and review process. Do not use for small or well-understood changes — isolated one-file edits, tiny bug fixes, simple configuration changes, copy changes, or any request that is fully specified and ready for direct implementation with no exploration or design work needed.
```

Rationale: removes "Use this whenever the user wants to add a feature" (too broad), keeps "medium-to-large" as the explicit gate, and moves the exclusion list to the description so trigger-matching logic disfavours small tasks.

---

### Change 2 — Add "When Not to Use This Skill" section

**Insert as a new section immediately after the `---` that closes Core Principles (before "## Process Selection"):**

```markdown
## When Not to Use This Skill

Skip this skill and implement directly when:

- The change is confined to a single file with no design ambiguity
- The task is a bug fix with a clear, isolated root cause
- The request is a simple configuration, dependency, or copy change
- The user supplies a complete spec with no unknowns and says "just do it"
- Net-new logic is trivially small (roughly fewer than ~30 lines)

For these, prefer the default agent workflow. The overhead of phased exploration, agents, and a handoff artifact is not justified.
```

---

### Change 3 — Elevate TDD to Core Principles

TDD is already required in Phase 5 but is easy to miss there. Add it to Core Principles so it is visible on first read.

**Old Core Principles list (last bullet):**

```markdown
- **Leave reusable artifacts**: When the work spans multiple phases or may be handed to another agent, write a concrete handoff artifact rather than leaving only prose in chat.
- **Use TodoWrite**: Track all progress throughout
```

**New (append one bullet after "Use TodoWrite"):**

```markdown
- **TDD is non-optional**: Every implementation phase — on every track — must follow the tdd skill's red-green-refactor loop. Do not bypass this for any reason.
```

The existing Phase 5, step 3 text is already correct and stays unchanged. The Core Principles addition makes the requirement discoverable without reading every phase.

---

## What I Would Leave Alone

- **code-simplifier subagent** (Phase 6, step 1) — wording is already "Always launch an independent … subagent". No change needed.
- **Quality review subagent** (Phase 6, step 2) — wording is already "Always run independent … agents". No change needed.
- **Process tracks, phases, and agent references** — all remain intact; the changes above are purely additive or limited to the two identified gaps.

---

## Implementation Map

All three changes are edits to a single file: `skills/feature-dev/SKILL.md`.

| #   | Location                                                              | Type                 |
| --- | --------------------------------------------------------------------- | -------------------- |
| 1   | Frontmatter `description:` line                                       | Replace entire value |
| 2   | Between `## Core Principles` closing `---` and `## Process Selection` | Insert new section   |
| 3   | End of `## Core Principles` bullet list                               | Append one bullet    |

No other files need to change. Ready to apply whenever you confirm or say "just do it".
