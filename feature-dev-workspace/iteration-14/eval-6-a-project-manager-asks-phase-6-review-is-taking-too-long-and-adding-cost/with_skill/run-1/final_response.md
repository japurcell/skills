# Phase 6 Minimum Non-Negotiable Subagent Steps

## Answer

The feature-dev workflow mandates exactly **two required subagent steps** in Phase 6. Both are non-negotiable. Neither can be dropped.

---

## Required Phase 6 Steps (from the workflow)

### Step 1 — `code-simplifier` subagent

**Mandated by**: Phase 6, Action 1:

> "Always launch an independent code-simplifier subagent to identify refactoring opportunities after implementation."

- This step runs **first**, before any code-reviewer agents.
- "Always" means it is required on every track — Light, Standard, and Deep.
- The subagent's mandate is to identify refactoring opportunities (simplicity, DRY, elegance).

### Step 2 — `code-reviewer` subagent(s)

**Mandated by**: Phase 6, Action 2:

> "Always run independent code-reviewer agents for quality review on every track."

- This step runs **after** the `code-simplifier` pass.
- "Always" means it is required on every track.
- On **Light track**: at least one independent `code-reviewer` agent.
- On **Standard or Deep track**: multiple independent `code-reviewer` agents in parallel with different focuses (e.g., simplicity, correctness, conventions).

---

## What Cannot Be Dropped

| Step | Subagent             | Required?             |
| ---- | -------------------- | --------------------- |
| 1    | `code-simplifier`    | Yes — "always launch" |
| 2    | `code-reviewer` (≥1) | Yes — "always run"    |

Neither step can be made optional. The workflow uses "always" for both. If Phase 6 review duration is a concern, acceptable optimizations are:

- On Light track, use a single `code-reviewer` agent (minimum allowed)
- Scope each agent's focus tightly so they complete faster
- Run the Standard/Deep `code-reviewer` agents in parallel rather than sequentially

But removing either the `code-simplifier` pass or the `code-reviewer` review is not an option the workflow permits.

---

## Ordering Constraint

The workflow lists `code-simplifier` as Action 1 and `code-reviewer` as Action 2, making the sequence explicit:

```
implementation → code-simplifier → code-reviewer(s)
```

Reversing the order or collapsing both into one agent also violates the workflow's structure.
