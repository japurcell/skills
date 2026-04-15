# Phase 6 Quality Review: Code-Simplifier Comparison

## Short Answer

Per the feature-dev skill, **the code-simplifier step does not differ between Scenario A (3 files) and Scenario B (12 files across two packages)**. The skill prescribes the same action in both cases. What *does* scale is the code-reviewer step.

---

## What the Skill Says

Phase 6 of the feature-dev skill contains two distinct sub-steps:

**Step 1 — code-simplifier (no scaling language):**
> "Always launch an independent code-simplifier subagent to identify refactoring opportunities after implementation."

The word *always* is unqualified. There is no conditional, no track-based variation, and no mention of launching multiple code-simplifier agents for larger changes. It is a single independent subagent launch every time, regardless of scope.

**Step 2 — code-reviewer (explicit scaling language):**
> "Always run independent code-reviewer agents for quality review on every track:
> - Light: launch at least one independent code-reviewer agent
> - Standard or Deep: launch multiple independent code-reviewer agents in parallel with different focuses such as simplicity, correctness, and conventions"

This step explicitly scales based on the chosen process track.

---

## Applying This to Each Scenario

### Scenario A — 3 files modified

- **Likely track**: Light. Three files is a well-bounded change where the main risk is local code context, not broad architectural ambiguity.
- **code-simplifier**: Launch one independent code-simplifier subagent. Identical to any other track.
- **code-reviewer**: Launch at least one independent code-reviewer agent (Light track minimum).

### Scenario B — 12 files across two packages

- **Likely track**: Standard or Deep. Touching 12 files spread across two packages suggests cross-cutting concerns, non-trivial design surface, and higher risk of inconsistency between packages.
- **code-simplifier**: Launch one independent code-simplifier subagent. **Same as Scenario A.**
- **code-reviewer**: Launch multiple independent code-reviewer agents in parallel (e.g., one for simplicity, one for correctness, one for cross-package conventions). This is where the meaningful difference lies.

---

## Why the code-simplifier Doesn't Scale Here

The skill treats code-simplification as a pass that any codebase change benefits from equally — it is a baseline quality gate, not a proportional one. Doubling the number of simplifier agents would not improve its effectiveness; a single focused pass over the changed files is sufficient to surface redundancy and readability issues.

The code-reviewer step is where scaling adds value: larger, cross-package changes benefit from reviewers focused on different concerns in parallel because the failure modes (correctness vs. simplicity vs. convention adherence) are independent and harder to catch in one pass.

---

## Summary Table

| | Scenario A (3 files, Light) | Scenario B (12 files, Standard/Deep) |
|---|---|---|
| **code-simplifier** | 1 independent subagent | 1 independent subagent (**same**) |
| **code-reviewer** | ≥ 1 agent | Multiple agents in parallel, different focuses |

The code-simplifier step is **invariant** across scenarios. The code-reviewer step is where the skill's scaling logic applies.
