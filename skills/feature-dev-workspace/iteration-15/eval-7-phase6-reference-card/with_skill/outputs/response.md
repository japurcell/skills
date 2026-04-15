# Phase 6 Reference Card: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct.

---

## Exact Sequence of Subagent Steps

### Step 1 — Launch `code-simplifier` subagent(s)

Run **after implementation completes**. Scale by number of changed files:

| Change Size | Action |
|---|---|
| **Small** (≤ 5 changed files) | Launch **1** `code-simplifier` agent covering **all** changed files |
| **Large** (> 5 changed files) | Partition files into non-overlapping groups (by module, directory, or logical area); launch **one agent per group in parallel** |

> **Critical constraint**: Each file must be assigned to **exactly one** agent. No file may appear in more than one agent's scope — agents apply edits directly and overlapping scopes produce conflicting writes.

---

### Step 2 — Launch independent `code-reviewer` agent(s)

Run **always**, on **every track**:

| Track | Action |
|---|---|
| **Light** | Launch **at least 1** independent `code-reviewer` agent |
| **Standard or Deep** | Launch **multiple** independent `code-reviewer` agents in parallel, each with a different focus (e.g., simplicity, correctness, conventions) |

These agents run **independently** — do not share scope between them.

---

### Step 3 — Consolidate findings

Gather all outputs from the `code-simplifier` and `code-reviewer` agents. **Prioritize** the issues that matter most.

---

### Step 4 — Fix high-severity issues

**Fix obvious high-severity issues directly**, unless the user has explicitly asked to stop after review.

---

### Step 5 — Surface remaining items

**Surface** remaining risks, trade-offs, and follow-up work clearly to the user.

---

## Notes

- Steps 1 and 2 may run concurrently (code-simplifier agents and code-reviewer agents are independent of each other, subject to the no-overlapping-scope constraint within code-simplifier).
- The `code-simplifier` partitioning rule applies only across multiple code-simplifier agents — it does not restrict code-reviewer agents.
- This phase applies on **all tracks** (Light, Standard, Deep). The only track-variable element is the number of `code-reviewer` agents in Step 2.
