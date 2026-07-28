# Feature Development: Medium-Sized Feature (Three Files, With Review)

## Understanding

**Request**: Implement a medium-sized feature that updates three files, then complete quality review.

**Track selected: Standard**

Rationale: Three files is solidly medium-sized with likely design choices across their interactions. The Standard track fits: it explores in depth, surfaces any ambiguity, proposes a recommendation, implements via TDD, then runs a full quality review pass.

---

## Phase 1: Discovery

**Todos created (scaled to actual work):**

1. Explore codebase — understand patterns in the three files' area
2. Ask targeted clarifying questions if any gaps remain
3. Propose recommended implementation approach
4. Implement via TDD (red → green → refactor)
5. Quality review: run code-simplifier + code-reviewer subagents
6. Fix high-severity findings; surface remaining risks
7. Write handoff artifact (Standard track with multi-turn potential)

---

## Phase 2: Codebase Exploration

**Action**: Launch **2 focused `code-explorer` agents in parallel** (Standard track calls for 2):

- **Agent A** — "Find features similar to [the target feature] and trace through their implementation comprehensively, focusing on abstractions and flow of control. Return a list of 5–10 key files to read."
- **Agent B** — "Map the architecture and abstractions for [the affected area], covering how the three files relate to each other. Return a list of 5–10 key files to read."

Once both agents return, I read every file they identify so my understanding is grounded in source, not only agent summaries.

**Relevant Findings** (representative of what would emerge):

- File A exports a data model; Files B and C consume it via a shared interface.
- Existing patterns use a factory function rather than direct instantiation.
- Tests live alongside source using `*.test.ts` naming.
- No integration-level tests yet for the three-file surface.

---

## Phase 3: Clarifying Questions

Only questions that would materially change the design are raised. For a three-file feature with a clear interface boundary, typical blockers might be:

1. Should the new behavior be opt-in (feature flag) or always-on?
2. Are there backward-compatibility constraints on the shared interface in File A?

If the user answers or says "your call," I state my assumptions (opt-in via config; existing interface extended, not replaced) and proceed without waiting for a second confirmation.

---

## Phase 4: Architecture Design

**Standard track: compare 1–2 approaches if a real decision exists.**

| | Option 1 — Extend existing interface | Option 2 — New side-car module |
|---|---|---|
| Files changed | A, B, C (as requested) | A, B, C + new D |
| Risk | Lower — stays in-scope | Slightly higher scope |
| Maintainability | Good if interface stays cohesive | Better separation but adds indirection |

**Recommendation**: Option 1. The three-file boundary is already appropriate; adding a fourth module would be gold-plating for a medium-sized change.

---

## Phase 5: Implementation

**Required on every track: use the `tdd` skill with an explicit red-green-refactor loop.**

1. **Red** — Write failing tests for the new behaviour in all three files' test suites before touching production code.
2. **Green** — Make the smallest changes to File A (model), File B (consumer), File C (consumer) that turn the tests green.
3. **Refactor** — Deduplicate, clarify naming, enforce conventions without breaking tests.

All todos are updated in real time as each slice completes.

---

## Phase 6: Quality Review

This is where the skill is most explicit. Because the change touches **three files (≤5)**, the rule is:

### code-simplifier subagent

> **Small (≤5 changed files): launch 1 `code-simplifier` agent covering all changed files.**

- **Role**: `code-simplifier` (skill at `../code-simplifier/SKILL.md`)
- **Scope**: File A, File B, File C — all three in a single agent (no overlapping scopes, because each agent applies edits directly).
- **Goal**: Identify and apply refactoring opportunities — DRY violations, unclear naming, unnecessary complexity — without changing external behaviour.

### code-reviewer subagents

> **Standard track: launch multiple independent `code-reviewer` agents in parallel with different focuses.**

- **Agent 1** — `code-reviewer` focused on **correctness**: edge cases, error paths, data integrity between File A's model and Files B/C's consumption.
- **Agent 2** — `code-reviewer` focused on **simplicity & conventions**: naming, formatting, adherence to codebase patterns found in Phase 2.

Both agents run in parallel; they are independent (read-only reviewers, no write conflicts).

### Consolidation

- Findings from both reviewers are merged and prioritized by severity.
- High-severity issues (e.g., unhandled null on File B's consumer path) are fixed directly.
- Remaining risks and follow-up suggestions are surfaced clearly rather than silently dropped.

---

## Exact Subagent Roles in Quality Review (Summary)

| Subagent | Role Reference | Count | Scope |
|---|---|---|---|
| `code-simplifier` | `../code-simplifier/SKILL.md` | 1 (≤5 files rule) | All 3 changed files, non-overlapping |
| `code-reviewer` (correctness) | `code-reviewer` | 1 of 2 parallel | Correctness, edge cases, data integrity |
| `code-reviewer` (conventions) | `code-reviewer` | 2 of 2 parallel | Simplicity, naming, codebase conventions |

---

## Handoff Artifact

Because this is Standard track and may continue in another turn, a handoff artifact is written to:

```
.agents/scratchpad/medium-three-file-feature/handoff-plan.md
```

The artifact captures: goal & non-goals, relevant findings, technical constraints, assumptions, recommended design, ordered implementation slices, file-by-file map, and a Validation Plan that explicitly names:

1. TDD red-green-refactor loop ✓
2. `code-simplifier` refactor pass ✓
3. Independent `code-reviewer` review ✓

---

## Phase 7: Summary

**What was built**: A medium-sized feature extending three files (File A: model, Files B & C: consumers) using the factory pattern already present in the codebase.

**Key decisions**:
- Standard track chosen for 3-file scope with moderate ambiguity.
- Option 1 (extend interface, not add module) to stay in scope.
- TDD enforced at every phase — not bypassed.

**Files modified**: File A, File B, File C (+ their test files).

**Quality review enforced**:
- 1 `code-simplifier` agent across all 3 files.
- 2 parallel `code-reviewer` agents (correctness; conventions).
- High-severity findings fixed inline; remainder surfaced.

**Next steps**: Address any open questions from review; add integration tests if the interface is consumed by a fourth caller.
