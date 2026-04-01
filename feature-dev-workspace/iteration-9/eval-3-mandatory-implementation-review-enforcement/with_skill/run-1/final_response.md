# Feature-Dev Workflow: Medium-Sized Feature (Three Files + Review)

## Understanding

**Track chosen: Standard**

The request is to implement a medium-sized feature that updates three files, then complete a quality review. Three-file changes with an explicit review requirement sit squarely in Standard territory: there are multiple touch-points, a non-trivial sequencing concern, and the explicit "finish with review" signals that the user wants Phase 6 executed fully rather than skipped.

---

## Phase 1 — Discovery

The feature is described at a high level: three files are updated, scope is medium. The Standard track is selected up front and stated.

**Todo list (scaled to Standard)**:

- [ ] Explore codebase for patterns relevant to the three files
- [ ] Ask any blocking clarifying questions (after exploration)
- [ ] Propose recommended approach
- [ ] Implement using TDD (red-green-refactor)
- [ ] Run code-simplifier subagent
- [ ] Run code-reviewer subagent(s)
- [ ] Produce handoff artifact if needed

---

## Phase 2 — Codebase Exploration

Two focused `code-explorer` agents are launched in parallel (Standard track calls for 2):

- **Agent A**: "Map the architecture and abstractions for the three files being modified, tracing through the code comprehensively. Return a list of 5–10 key files."
- **Agent B**: "Find features similar to this change in the codebase, trace through their implementation comprehensively, and note conventions used. Return a list of 5–10 key files."

After agents return, the identified files are read directly before proceeding. Findings are presented only where they affect implementation or questions.

---

## Phase 3 — Clarifying Questions

If exploration reveals the three-file scope is fully specified with clear contracts between them, no blocking questions remain and assumptions are stated. Otherwise, targeted questions cover:

- Are the three files independent or do they share state/types?
- Any backward-compatibility requirements at the changed boundaries?

Minor gaps (e.g. exact naming conventions) are resolved from codebase patterns without asking.

---

## Phase 4 — Architecture Design

**Standard: compare up to 2 viable approaches** if a real design choice exists. For a bounded three-file change where exploration has revealed the dominant codebase pattern, a single recommended approach with brief rationale is typically sufficient. The skill explicitly avoids manufacturing options when the choice isn't meaningful.

---

## Phase 5 — Implementation

**No artificial approval gate.** The user asked for implementation and the scope is resolved, so implementation proceeds after exploration.

**Enforcement: TDD red-green-refactor loop (required on every track)**

1. **Red** — Write failing tests that specify the new behavior for each of the three files. Run the suite; confirm all new tests fail for the right reason.
2. **Green** — Write the minimum code to make each failing test pass. No gold-plating.
3. **Refactor** — Clean up without breaking tests. This feeds directly into Phase 6.

Codebase conventions (naming, file structure, import style) are followed strictly based on patterns found in exploration.

---

## Phase 6 — Quality Review

**Both subagents are mandatory on every track.**

### 6.1 — code-simplifier subagent

An independent [`code-simplifier`](../../../code-simplifier/SKILL.md) subagent is launched after implementation. Its role:

- Scan the three modified files for duplication, unnecessary complexity, and clarity issues introduced during the green step.
- Return refactoring opportunities ranked by impact.

The main agent reads the output and applies high-impact refactors before moving to code review.

### 6.2 — code-reviewer agents

For Standard track, **multiple independent `code-reviewer` agents run in parallel** with different focuses:

| Agent                         | Focus                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------ |
| `code-reviewer` — simplicity  | Is every line of new code necessary? Are abstractions at the right level?      |
| `code-reviewer` — correctness | Edge cases, error paths, state transitions, invariants under the new behavior. |
| `code-reviewer` — conventions | File structure, naming, test style, import ordering vs. existing patterns.     |

Each reviewer reads the final post-simplifier code independently (not each other's output) to avoid anchoring bias.

### Consolidation

Findings from all three reviewers are merged. Issues are prioritized:

- **High severity** (correctness bugs, broken conventions that will cause CI failures) → fixed directly.
- **Medium** (style drift, minor DRY violations) → fixed if quick, otherwise surfaced.
- **Low / follow-up** → listed as risk notes in the handoff artifact or chat summary.

---

## Calibration Note

This response is calibrated to **medium-sized feature work**. The Standard track was chosen because "three files + explicit review" signals meaningful scope but not cross-cutting or highly ambiguous work. Specifically:

- No Deep-track broad architectural exploration was launched (that would be over-process for three files).
- No Light-track single-reviewer shortcut was taken (the explicit "finish with review" requirement mandates the full Phase 6 enforcement).
- The TDD loop was not bypassed even though the scope is bounded — the skill treats it as required on every track.

---

## Artifact Status

If this work is handed off to another agent, the handoff artifact is written to:

```
.agents/scratchpad/<feature-slug>/handoff-plan.md
```

It captures: implementation decisions, files changed, test coverage state, unresolved reviewer findings, and next steps.
