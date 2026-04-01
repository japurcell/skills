# Feature Development Workflow — Eval 3 Response

## Understanding

**Track chosen: Standard**

The request is a medium-sized feature that touches three files. This fits the Standard Track because:

- Well-defined scope (three files) but not trivially bounded
- Requires non-trivial coordination across multiple files
- The explicit "finish with review" instruction aligns with Standard-track expectations

---

## Phase 1: Discovery

**Todo list (Standard Track):**

- [ ] Explore codebase (2 parallel agents)
- [ ] Ask targeted clarifying questions if needed after exploration
- [ ] Design approach
- [ ] Implement with TDD (red-green-refactor)
- [ ] Run quality review agents
- [ ] Fix high-severity issues; surface remaining risks

**Initial request:** "Implement a medium-sized feature that updates three files and then finish with review."

The feature description is intentionally abstract for this demonstration. No blocking ambiguities prevent proceeding — the token "update three files" indicates bounded scope and the "finish with review" instruction is explicit.

---

## Phase 2: Codebase Exploration

Per Standard Track rules, **two focused `code-explorer` agents** are launched in parallel:

- **Agent A:** "Find features similar to [feature] and trace through their implementation comprehensively — include a list of 5–10 key files to read."
- **Agent B:** "Map the architecture and abstractions for [feature area], tracing through the code comprehensively — include a list of 5–10 key files to read."

After both complete, their returned file lists are read directly to ground implementation decisions in source, not only agent summaries.

---

## Phase 3: Clarifying Questions

No blocking questions remain after exploration. The scope is clear: three files, implement, then review. Assumptions are stated:

- The three files are co-located in a single subsystem
- No new public APIs are introduced
- Existing conventions and test patterns apply

---

## Phase 4: Architecture Design (Standard Track)

One recommended approach is presented (no meaningful architectural fork exists for this bounded change). The approach is:

- Identify the three target files from exploration findings
- Apply minimal-diff changes aligned with existing patterns
- Co-locate any new logic with existing similar logic

---

## Phase 5: Implementation — Enforcement Explained

The skill includes an **explicit anti-gate directive**:

> "Do not create artificial approval gates. If the user already asked for implementation and the important unknowns are resolved, proceed."

The user's request included "Implement a medium-sized feature" — this is an unambiguous implementation request. The skill **mandates proceeding** once blockers are resolved, not asking for redundant confirmation.

**Additional mandatory requirement:** the skill states:

> "Always use the tdd skill to implement with an explicit red-green-refactor loop"

Implementation proceeds in red-green-refactor cycles across the three files:

1. **Red:** Write a failing test capturing the required behavior in each changed file
2. **Green:** Implement the minimum code to make each test pass
3. **Refactor:** Clean up to meet simplicity and conventions standards
4. Update todos as each file completes

This applies on **all tracks** — there is no escape hatch that allows skipping TDD.

---

## Phase 6: Quality Review — Enforcement and Subagent Roles

The skill states:

> "Always run independent `code-reviewer` agents for quality review on every track"

The word **always** and **every track** means this phase is non-optional. There is no path through the skill that skips quality review.

**Scaling by track:**

| Track    | Reviewer Agents Required                                        |
| -------- | --------------------------------------------------------------- |
| Light    | At least one `code-reviewer` agent                              |
| Standard | Multiple parallel `code-reviewer` agents with different focuses |
| Deep     | Multiple parallel `code-reviewer` agents with different focuses |

**For this Standard Track feature, the following `code-reviewer` subagents are launched in parallel:**

1. **`code-reviewer` (simplicity focus)** — enforces DRY, readable, minimal code; flags over-engineering
2. **`code-reviewer` (correctness focus)** — verifies logic, edge cases, and test coverage
3. **`code-reviewer` (conventions focus)** — checks naming, formatting, file structure, and architectural alignment with existing patterns

These are all instances of the same `agents/code-reviewer.md` agent role, launched with different scoped instructions. The agents are **independent** (they do not share state and are run in parallel), preventing confirmation bias.

**Post-review actions:**

- Consolidate findings from all three reviewers
- Fix obvious high-severity issues directly
- Surface remaining risks and follow-up work clearly
- Do not stop after review unless the user requested it — the default is to fix high-severity findings

---

## Summary of Enforcement Mechanisms in the Old Skill

| Requirement                                      | Enforcement Method                                                                                    |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Implementation must happen (no artificial gates) | Explicit directive in Phase 5: "Do not create artificial approval gates"                              |
| TDD on every track                               | "Always use the tdd skill" — unconditional                                                            |
| Quality review on every track                    | "Always run independent code-reviewer agents… on every track" — unconditional                         |
| Standard track gets multiple reviewers           | Track scaling table: "Standard or Deep: launch multiple independent code-reviewer agents in parallel" |
| Reviewers are independent                        | Agents launched independently and in parallel, not sequentially                                       |

The exact subagent roles used in quality review for Standard Track:

- `agents/code-reviewer.md` × 3 (simplicity, correctness, conventions)

---

## Artifact Status

No file-backed handoff artifact is required for this bounded three-file feature. The workflow terminates after quality review issues are addressed.
