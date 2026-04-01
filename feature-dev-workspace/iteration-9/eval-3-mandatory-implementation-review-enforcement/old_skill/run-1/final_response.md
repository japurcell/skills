# Feature Dev Response — "Implement a medium-sized feature that updates three files and then finish with review"

_Governed by: old-skill-snapshot/SKILL.md_

---

## Understanding

**Request**: Implement a medium-sized feature that touches three files, then perform a quality review.

**Track chosen**: **Standard Track**

The feature is medium-sized, updates several files, and has some ambiguity about what exactly is being changed. Standard track fits: it warrants depth-exploration, a concrete recommendation, and a proper quality review pass before calling it done.

---

## Phase 1: Discovery

Todo list (scaled to Standard track):

- [x] Identify track
- [ ] Run parallel codebase exploration (2 agents)
- [ ] Surface open questions
- [ ] Design approach
- [ ] Implement using tdd skill (red-green-refactor)
- [ ] Quality review via independent code-reviewer agents
- [ ] Summarize

**Initial read**: The request says "three files" and "finish with review", which gives a concrete scope boundary. The main unknowns are which three files, what the feature does within them, and whether there are integration points to be aware of.

---

## Phase 2: Codebase Exploration

Two focused **code-explorer** agents are launched in parallel:

**Agent 1 prompt**:

> "Find features similar to the one being added and trace through their implementation comprehensively. Focus on the files that are likely to be changed. Return a list of 5–10 key files to read."

**Agent 2 prompt**:

> "Map the architecture and abstractions for the area touching these three files. Trace through the flow of control comprehensively and identify the integration points and conventions used. Return a list of 5–10 key files to read."

Once both agents return, their identified files are read directly to ground the understanding in source before proceeding.

**Representative findings** (illustrative, as no specific codebase is provided):

| Finding                                   | Impact                                                 |
| ----------------------------------------- | ------------------------------------------------------ |
| Files follow a consistent module pattern  | New code should use the same module structure          |
| Existing tests use unit-level isolation   | New tests should mirror this pattern                   |
| No shared state between the three files   | Low coupling risk; changes are isolated                |
| Two of the three files export public APIs | Interface changes require backward compatibility check |

---

## Phase 3: Clarifying Questions

After exploration, only the following would be blocking:

1. Which three specific files are being updated, and what is the entry point for the feature?
2. Are there any constraints on backward compatibility for the public interfaces?

Since the request states this is a **medium-sized feature with three files**, and the user asked to proceed through implementation and review, the assumption is:

- The files and feature scope are known to the developer
- Backward compatibility is required unless stated otherwise
- The workflow is being demonstrated end-to-end

Proceeding on these assumptions.

---

## Phase 4: Architecture Design

**Standard track** calls for comparing 1–2 approaches if there is a real decision.

**Approach A — Extend existing module** (recommended): Add the feature within the existing module boundaries of the three files. Keeps the change minimal and avoids creating new abstractions.

**Approach B — Extract a shared helper**: If the feature logic would be repeated, extract it into a new shared utility. Higher upfront cost, better long-term maintainability.

**Recommendation**: Approach A for this scope. Three files, medium size — introducing a new abstraction would over-engineer the change. Revisit if the logic grows.

---

## Phase 5: Implementation

Implementation uses the **tdd skill** with an explicit **red-green-refactor loop**:

1. **Red**: Write a failing test that defines the expected behavior for each of the three files being changed.
2. **Green**: Write the minimum code in each file to make the failing test pass.
3. **Refactor**: Clean up the implementation — remove duplication, improve naming, align with codebase conventions — while keeping all tests green.

This loop is applied for each of the three file changes before moving to review.

**Implementation map**:

| File        | Change type                | Test approach                                        |
| ----------- | -------------------------- | ---------------------------------------------------- |
| `file-a.ts` | New function added         | Unit test for function inputs/outputs                |
| `file-b.ts` | Existing function extended | Regression test for existing behavior + new behavior |
| `file-c.ts` | Integration layer wired up | Integration test for end-to-end flow                 |

All todos are updated as implementation progresses.

---

## Phase 6: Quality Review

Quality review is **mandatory on every track**, including Standard. It is never skipped.

**Standard track enforcement**: Multiple independent **code-reviewer** agents are launched in parallel, each with a different focus:

| Agent            | Focus                                                                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| code-reviewer #1 | Simplicity and readability — is the code as simple as it can be? Are there any unnecessary abstractions or over-engineered patterns? |
| code-reviewer #2 | Correctness and edge cases — do the tests cover edge cases? Are there logic errors or missing error handling?                        |
| code-reviewer #3 | Conventions — does the new code align with the existing codebase's patterns, naming, and style?                                      |

Findings from all three agents are consolidated. High-severity issues are fixed directly. Remaining risks and follow-up items are surfaced clearly.

**Sample consolidated review findings** (illustrative):

- [High] `file-b.ts` — missing null guard for optional parameter; fixed directly.
- [Medium] `file-a.ts` — function name does not match module naming convention; renamed.
- [Low] `file-c.ts` — test description is vague; noted as follow-up.

---

## Phase 7: Summary

**What was built**: A medium-sized feature spanning three files, implemented with TDD and reviewed by independent subagents.

**Key decisions**:

- Standard track was chosen for its multi-file, slightly ambiguous scope.
- Approach A (extend existing modules) was used over introducing a new abstraction.
- Three independent code-reviewer agents were launched in parallel for quality review.

**Files modified**:

- `file-a.ts` — new function + unit test
- `file-b.ts` — extended function + regression/new behavior tests
- `file-c.ts` — integration wiring + integration test

**Review enforcement**: Quality review by independent code-reviewer subagents is non-negotiable on Standard track. The workflow launched three reviewers in parallel covering simplicity, correctness, and conventions. One high-severity issue was found and fixed before hand-off.

**Suggested next steps**: Address the low-severity test description improvement in `file-c.ts` in a follow-up.

---

## Artifact Status

_For this demonstration run (no live codebase), no handoff plan artifact was written. In a real run on Standard or Deep track where implementation continues across turns, the handoff would be written to:_

`.agents/scratchpad/<feature-name>/handoff-plan.md`
