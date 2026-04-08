# Phase 6: Quality Review — Reference Card

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct.

---

## Exact Subagent Step Sequence

### Step 1 — Launch `code-simplifier` subagent (always required)

Launch an independent **code-simplifier** subagent (`../code-simplifier/SKILL.md`) to identify refactoring opportunities after implementation.

- This step is unconditional — it runs on every track (Light, Standard, Deep).

---

### Step 2 — Launch `code-reviewer` subagent(s) (always required)

Launch independent **code-reviewer** subagents (`agents/code-reviewer.md`) for quality review. The number of agents depends on track:

| Track | Requirement |
|---|---|
| **Light** | Launch **at least one** independent code-reviewer agent |
| **Standard** | Launch **multiple** independent code-reviewer agents in parallel with different focuses (e.g. simplicity, correctness, conventions) |
| **Deep** | Launch **multiple** independent code-reviewer agents in parallel with different focuses (e.g. simplicity, correctness, conventions) |

---

### Step 3 — Consolidate findings

Consolidate all findings from the code-simplifier and code-reviewer agents. Prioritize the issues that matter most.

---

### Step 4 — Fix high-severity issues

Fix obvious high-severity issues directly, **unless** the user has asked to stop after review.

---

### Step 5 — Surface remaining work

Surface remaining risks, trade-offs, and follow-up work clearly.

---

## Notes for Literal Execution

- Steps 1 and 2 are mandatory on **every track** — there are no exceptions.
- The code-simplifier (Step 1) and code-reviewer agents (Step 2) are **independent** subagents — do not conflate them or skip either.
- For Standard and Deep tracks, code-reviewer agents must be launched **in parallel**, not sequentially.
- Step 4 (fixing issues) is conditional only on whether the user asked to stop after review; it is otherwise expected.
