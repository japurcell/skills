# Evaluation: Baseline Skill Refusal to Continue into Phase 8

## Governing Rule (Non-Negotiable)

The baseline skill explicitly enforces this rule in **Non-negotiable rules #4**:

> **After Gate E passes, hard-stop the session and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session. Resume from a fresh session; Phase 8 is the next phase after the resume.**

This is also restated in the **Workflow-rule answers** table:

> | User asks about | Answer |
> | Phase 7 resume handoff | `Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with coding-task-workflow RESUME=<slug>. Phase 8 is the next phase after the resume.` |

And reinforced in **Phase 7** specification (step 7):

> After Gate E is satisfied, stop the current session and hand off a resume command: `coding-task-workflow RESUME=<slug>`. Do not proceed to Phase 8 in the same invocation.

## What the Baseline Skill Will Do

When you ask the baseline skill to continue directly into Phase 8 for `2026-04-23-add-rate-limit-logs` after Gate E has already passed, the skill **will refuse** and instead:

1. **Acknowledge Gate E has passed** — verified by checking that the Phase 7 task-graph issue is closed and at least one implementation task issue has `stage: red`.

2. **Refuse to execute Phase 8 in this session** — the skill treats this as a hard stop, not a continuation point.

3. **Return the mandatory handoff command** — the skill will provide:
   ```
   coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs
   ```

4. **Explain why** — the skill will cite the rule: "After Gate E passes, do not begin Phase 8 in the same session. Resume from a fresh session."

## What Must Happen Next

### Current Session (This One)

**Stop here.** Gate E has been satisfied. The baseline skill requires a session boundary at this point—this is not optional or negotiable.

### Next Session (Fresh)

To continue into Phase 8, you must:

1. **Start a new session** — do not reuse this conversation.

2. **Invoke the skill with the resume command**:
   ```
   coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs
   ```

3. **The resumed session will**:
   - Load the parent issue and all descendant phase/task issues for the work item `2026-04-23-add-rate-limit-logs` from GitHub.
   - Determine the last completed phase from issue closure state and approval comments (Phase 7 is complete; Phase 8 is next).
   - Begin Phase 8 — Implementation.

## Phase 8 Workflow Requirements (What Happens After Resume)

Once Phase 8 begins in the fresh session, the following strict requirements apply:

### Inputs
- Task-graph issue (already created and closed)
- Open implementation task issues (already created, each at `stage: red`)
- Relevant source files
- Fresh session context (no carryover from Phase 1–7)

### Execution Model: Strict TDD Red→Green→Refactor

For each implementation task issue:

1. **RED stage**:
   - Write a failing test that captures the required behaviour.
   - Run the test and confirm it fails for the expected reason.
   - Record the result as a comment on the task issue (issue remains at `stage: red`).

2. **GREEN stage**:
   - Update the task issue to `stage: green`.
   - Write the minimal code to make the test pass.
   - Run the test and confirm it passes.
   - Record the result as a comment on the same task issue.

3. **REFACTOR stage**:
   - Update the task issue to `stage: refactor`.
   - Clean up code if needed (remove duplication, improve clarity).
   - Rerun the relevant tests to confirm no regression.
   - Record the outcome as a comment on the task issue.
   - Close the task issue when the slice is complete.

### Processing Order
- Process implementation task issues **in dependency order** (topologically sorted).
- Run tasks labelled `parallel` concurrently only when their dependencies are satisfied and they do not overlap on files.
- Run tasks labelled `sequential` in strict order (no parallelism).

### Critical Constraints
- **Never add untested code paths**. If a branch is not yet covered by a test, do not add it.
- **All RED slices must not be written before any GREEN slices.** Each vertical slice executes independently in the order defined by the task graph.
- **Issue comments replace local logs** — `07-implementation-log.md` is never created; task issue comments are the durable record.
- **No local per-work-item artifacts** — all state persists in GitHub issues and comments.

### Phase Outputs (by end of Phase 8)
- Modified source files and tests (committed but not yet pushed)
- Implementation task issue comments (RED, GREEN, REFACTOR records for each task)
- Updated task issue stage fields (all tasks at `stage: refactor` when closed)
- All implementation task issues closed when their slice is complete

### No Gate After Phase 8
Phase 8 has no explicit gate. The task graph itself is the gate structure (enforced by Phase 7).

## Why This Rule Exists

The design decision to require a session boundary after Gate E serves a specific purpose:

- **Context window management**: Phases 1–7 (planning) use significant context for exploration, research, and design decisions. Phases 8–11 (implementation, review, verification, landing) are heavier and require a fresh context window.
- **Clean handoff**: The fresh session loads state from GitHub only, ensuring reproducibility and auditability. The plan is locked in; implementation is deterministic.
- **Parallelism at scale**: Larger projects may split implementation work across multiple fresh sessions, each resuming independently with the same task graph and parallel scheduling.

## Summary

The baseline skill **refuses** to continue into Phase 8 in the same session because this is a non-negotiable rule. The handoff is:

```
coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs
```

Use this command in a fresh session to begin Phase 8. The specification above describes the exact workflow requirements Phase 8 will enforce.
