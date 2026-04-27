# Phase 7 and Phase 8: Implementation Task Issues for Retry Cap and Jitter

## Overview

Based on the approved plan with two behaviors (add a retry cap and add jitter), **Phase 7 creates exactly TWO implementation task issues**, one for each behavior. Each task issue owns one complete vertical TDD slice (RED → GREEN → REFACTOR) and persists as the durable record across Phase 8.

---

## Phase 7: TDD Task Graph

### What Gets Created

**Deliverable 1: Task-Graph Issue** (labeled `agent:phase`, `phase:task-graph`)
- Contains a YAML block (in the issue body) that defines the task graph structure
- Lists both tasks with their dependencies, parallelizability, and affected files
- Closed once the YAML and implementation task issues are complete

**Deliverable 2a: Implementation Task Issue #1** (labeled `agent:task`, `phase:implement`, `sequential` or `parallel`)
- **Title**: Retry mechanism: add retry cap
- **Task ID**: (e.g., `t1-retry-cap`)
- **Behavior**: Implement a maximum retry limit so requests don't retry indefinitely
- **Initial stage**: `red`
- **Depends on**: (likely empty or depends on prerequisite infrastructure)
- **Files affected**: (e.g., `src/retry/retry.test.ts`, `src/retry/retry.ts`)
- **Status**: Open (stays open through Phase 8 until the slice is complete)

**Deliverable 2b: Implementation Task Issue #2** (labeled `agent:task`, `phase:implement`, `sequential` or `parallel`)
- **Title**: Retry mechanism: add jitter
- **Task ID**: (e.g., `t2-jitter`)
- **Behavior**: Implement exponential backoff with jitter to avoid thundering-herd problems
- **Initial stage**: `red`
- **Depends on**: (possibly depends on t1 if jitter builds on the cap, or independent if it's a sibling)
- **Files affected**: (e.g., `src/retry/retry.test.ts`, `src/retry/retry.ts`)
- **Status**: Open (stays open through Phase 8 until the slice is complete)

---

## Recording Progress: RED / GREEN / REFACTOR

### Where Progress is Recorded

**All RED/GREEN/REFACTOR progress is recorded as comments on the same task issue**, never as separate stage-specific issues. The issue body remains the durable record of metadata; comments hold the execution log.

### How the `stage` Field Changes Over Time

The task issue body contains a `Machine Data` YAML block with a `stage` field. This field tracks the current progress state:

```yaml
work_id: <slug>
kind: task
phase: implement
task_id: t1-retry-cap
stage: red | green | refactor  # <-- This field changes
parallelizable: false
depends_on: []
files: [src/retry/retry.test.ts, src/retry/retry.ts]
status: open
```

### Timeline: Task Issue #1 (Retry Cap)

**Phase 8 / RED stage** (after Phase 7 handoff and session resume):
1. Update the task issue body to set `stage: red`
2. Write a failing test that captures the expected behavior (e.g., verify that retries stop after the cap)
3. Run the test and confirm it fails for the expected reason
4. Post a RED comment on the task issue:
   ```markdown
   ## Slice Update — t1-retry-cap / red
   
   - **status**: complete
   - **files_changed**: src/retry/retry.test.ts
   - **test_result**: fail (expected: retry cap not yet implemented)
   - **notes**: Test verifies that a request with maxRetries=3 stops after 3 attempts
   
   ## Machine Data
   
   ```yaml
   work_id: <slug>
   kind: implementation-log
   task_id: t1-retry-cap
   stage: red
   status: complete
   updated_at: <ISO8601>
   ```
   ```

**Phase 8 / GREEN stage**:
1. Update the task issue body to set `stage: green`
2. Write minimal code to make the test pass
3. Run the test suite and confirm the test now passes
4. Post a GREEN comment on the task issue:
   ```markdown
   ## Slice Update — t1-retry-cap / green
   
   - **status**: complete
   - **files_changed**: src/retry/retry.ts
   - **test_result**: pass
   - **notes**: Implemented maxRetries limit; added counter to retry loop
   
   ## Machine Data
   
   ```yaml
   work_id: <slug>
   kind: implementation-log
   task_id: t1-retry-cap
   stage: green
   status: complete
   updated_at: <ISO8601>
   ```
   ```

**Phase 8 / REFACTOR stage**:
1. Update the task issue body to set `stage: refactor`
2. Clean up code if needed (extract constants, simplify logic, improve naming)
3. Rerun the full test suite to ensure no regressions
4. Post a REFACTOR comment on the task issue:
   ```markdown
   ## Slice Update — t1-retry-cap / refactor
   
   - **status**: complete
   - **files_changed**: src/retry/retry.ts
   - **test_result**: pass (all tests)
   - **notes**: Extracted MAX_RETRIES constant; added inline documentation
   
   ## Machine Data
   
   ```yaml
   work_id: <slug>
   kind: implementation-log
   task_id: t1-retry-cap
   stage: refactor
   status: complete
   updated_at: <ISO8601>
   ```
   ```

5. Close the task issue once the slice is complete

### Timeline: Task Issue #2 (Jitter)

**Phase 8 / RED stage** (depends on t1 completion or runs in parallel):
1. Update the task issue body to set `stage: red`
2. Write a failing test that captures jitter behavior (e.g., verify that retry delays vary by random amount)
3. Post a RED comment (same format as t1-retry-cap)

**Phase 8 / GREEN stage**:
1. Update the task issue body to set `stage: green`
2. Implement minimal jitter logic (add random variance to backoff delay)
3. Post a GREEN comment

**Phase 8 / REFACTOR stage**:
1. Update the task issue body to set `stage: refactor`
2. Clean up jitter implementation (verify distribution, test edge cases)
3. Post a REFACTOR comment
4. Close the task issue

---

## Summary Table

| Aspect | Task Issue #1 (Retry Cap) | Task Issue #2 (Jitter) |
|--------|---------------------------|------------------------|
| **Count** | 1 of 2 | 1 of 2 |
| **ID** | t1-retry-cap | t2-jitter |
| **Behavior** | Implement maximum retry limit | Implement exponential backoff with jitter |
| **Labels** | `agent:task`, `phase:implement`, `sequential`/`parallel` | `agent:task`, `phase:implement`, `sequential`/`parallel` |
| **Initial Stage** | red | red |
| **Progress Recording** | Comments on this same issue (RED comment, GREEN comment, REFACTOR comment) | Comments on this same issue (RED comment, GREEN comment, REFACTOR comment) |
| **Stage Field Changes** | red → green → refactor (issue body `stage` field updated before each phase) | red → green → refactor (issue body `stage` field updated before each phase) |
| **Closure** | Closed after REFACTOR and all tests pass | Closed after REFACTOR and all tests pass |
| **Durable Record** | Issue body + comments | Issue body + comments |

---

## Key Rules Enforced

1. **Exactly two task issues**: One per behavior, created in Phase 7
2. **One vertical slice per issue**: Each issue owns a complete RED → GREEN → REFACTOR flow
3. **Comments are the log**: RED/GREEN/REFACTOR results appear as comments on the same task issue, never as separate stage issues
4. **Stage field tracks state**: The `stage` field in Machine Data (issue body) is updated in place as work progresses
5. **Hard stop after Phase 7**: After Phase 7 gate (Gate E) passes, the session ends. Phase 8 resumes in a fresh session with `RESUME=<slug>`
6. **No early closure**: Task issues remain open until their slice is complete (REFACTOR done, tests passing)
7. **Phase issue also closed**: The parent task-graph issue is closed only after both task issues exist and the YAML is finalized

---

## Dependency Ordering (Example)

The task graph YAML in the task-graph issue might look like:

```yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "2026-04-27T14:00:00Z"

tasks:
  - id: t1-retry-cap
    name: "Retry mechanism: add retry cap vertical slice"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/retry/retry.test.ts
      - src/retry/retry.ts

  - id: t2-jitter
    name: "Retry mechanism: add jitter vertical slice"
    stage: red
    depends_on: [t1-retry-cap]  # or [] if they can run in parallel
    parallelizable: false
    files:
      - src/retry/retry.test.ts
      - src/retry/retry.ts
```

---

## Phase 8 Execution Model

In Phase 8, the workflow:
1. Loads the task graph YAML from the task-graph issue
2. Processes task issues in dependency order
3. For each task issue in sequence (or parallel, if `parallelizable: true` and dependencies are satisfied):
   - Executes RED: write test, run, confirm fail
   - Executes GREEN: write code, run, confirm pass
   - Executes REFACTOR: clean up, run, confirm pass
   - Closes the task issue
4. Updates the `stage` field on the task issue body as it transitions between red/green/refactor
5. Records every step as a comment on the task issue

This design ensures that:
- The task issue is the single source of truth for that slice's state
- All progress is durable and persists across session boundaries
- Phases 7 and 8 are clearly separated (Phase 7 creates issues; Phase 8 executes them)
- The workflow can resume without re-reading local files
