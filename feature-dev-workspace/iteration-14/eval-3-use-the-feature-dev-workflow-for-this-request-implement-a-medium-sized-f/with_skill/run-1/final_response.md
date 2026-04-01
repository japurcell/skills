# Feature Dev Workflow: Medium-Sized Feature — Implementation and Review

## Understanding

The request is to implement a medium-sized feature that updates three files and finish with a quality review. Using the feature-dev workflow Standard track, since the feature touches several files and warrants a non-trivial design checkpoint.

**Track chosen**: Standard — three-file change, medium scope, review explicitly requested.

---

## Phase 1: Discovery

This is a representative medium-sized feature. The workflow mandates Standard track for work that "touches several files, has some ambiguity, or needs a non-trivial design choice."

**Todo list**:

- [x] Select track (Standard)
- [x] Explore codebase for patterns and integration points
- [ ] Ask minimal targeted clarifying questions (if blocking unknowns exist)
- [ ] Design approach
- [ ] Implement with TDD (red-green-refactor)
- [ ] Phase 6: code-simplifier pass → code-reviewer review
- [ ] Phase 7: summarize

---

## Phase 2: Codebase Exploration

Standard track mandates launching **two focused code-explorer agents in parallel**, each covering a different angle — for example:

- Agent A: "Find features similar to this one and trace their implementation comprehensively"
- Agent B: "Map the architecture and abstractions for this feature area, tracing through the code comprehensively"

Each agent returns a list of 5–10 key files. After agents complete, read those files directly to ground understanding in source.

---

## Phase 5: Implementation — TDD Is Required and Non-Negotiable

The feature-dev workflow states:

> **Always use the tdd skill to implement with an explicit red-green-refactor loop. Treat this as required for Implementation on every track; do not bypass it.**

For this three-file change:

1. **Red**: Write failing tests for each behavior the feature introduces, before writing production code. Tests go in the appropriate test files adjacent to the changed files.
2. **Green**: Write the minimum production code in each of the three target files to make the tests pass.
3. **Refactor**: Clean up implementation with tests still passing. This is the internal cleanup pass before external review.

TDD applies on **every track** — Light, Standard, and Deep. It is not optional for time-constrained or "simple" features.

---

## Phase 6: Quality Review — Exact Subagent Roles

After implementation is complete, Phase 6 runs two required subagent passes in sequence:

### Step 1: Launch `code-simplifier` subagent (runs first)

**Subagent**: [`code-simplifier`](../code-simplifier/SKILL.md)

**Focus**: Identify refactoring opportunities across the three modified files. Look for duplication, over-engineering, unnecessary abstraction, and opportunities to simplify without changing behavior.

This step runs **before** code review. The code-reviewer assesses the already-simplified code, not the raw post-implementation state.

### Step 2: Launch `code-reviewer` agents (Standard track: multiple in parallel)

**Subagents**: Multiple independent [`code-reviewer`](agents/code-reviewer.md) agents, each with a distinct focus:

| Agent                                   | Focus                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------------- |
| code-reviewer-1                         | **Correctness** — edge cases, error handling, boundary conditions            |
| code-reviewer-2                         | **Conventions** — naming, structure, patterns matching the existing codebase |
| code-reviewer-3 (optional for Standard) | **Simplicity** — is the implementation the simplest thing that works?        |

On the **Light track**, a single `code-reviewer` agent is sufficient. On **Standard or Deep**, the workflow calls for multiple agents run in parallel with different focuses.

### Step 3: Consolidate and fix

After both passes return findings:

1. Consolidate and prioritize the issues
2. Fix obvious high-severity problems directly
3. Surface remaining risks and follow-up work clearly

---

## Phase 7: Summary

- What was built: three-file feature update
- Implementation enforced: TDD red-green-refactor loop
- Review enforced: `code-simplifier` refactor pass followed by independent `code-reviewer` agents (parallel, different focuses on Standard track)
- No review steps were skippable or mergeable — each subagent role is distinct and independently required by the workflow
