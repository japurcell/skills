# Phase 7 and Phase 8: Implementation Task Issues for "Add Retry Cap" and "Add Jitter"

## Overview

When the approved plan has two behaviors—"add a retry cap" and "add jitter"—Phase 7 creates **exactly two implementation task issues**, one for each behavior. Phase 8 then executes those tasks using strict TDD red→green→refactor.

---

## Phase 7: TDD Task Graph

### Number of Implementation Task Issues

**Two task issues** are created under the Phase 7 task-graph issue:

1. **Task Issue #1**: "Add retry cap vertical slice" (for the `add-retry-cap` behavior)
2. **Task Issue #2**: "Add jitter vertical slice" (for the `add-jitter` behavior)

Each issue represents one complete **vertical slice**, not a single stage.

### What Each Task Issue Represents

Each implementation task issue owns one full vertical slice from RED → GREEN → REFACTOR:

- **Task Issue #1** owns all work for the "add retry cap" behavior:
  - The failing test (RED stage)
  - The minimal code to pass (GREEN stage)
  - The cleanup and refactoring (REFACTOR stage)
  - All on the same issue

- **Task Issue #2** owns all work for the "add jitter" behavior:
  - The failing test (RED stage)
  - The minimal code to pass (GREEN stage)
  - The cleanup and refactoring (REFACTOR stage)
  - All on the same issue

This is the **vertical slice principle**: each slice is a complete, testable behavior from test to production code to refactored code.

### Initial Task Issue Structure

Each task issue is created with:

```yaml
kind: task
phase: implement
task_id: t1  # or t2
stage: red   # Initial stage
parallelizable: true | false
depends_on: [...]
files: [...]
```

Labels applied: `agent:task`, `phase:implement`, plus `parallel` or `sequential`.

### Progress Recording: RED / GREEN / REFACTOR as Comments

All progress is recorded as **comments on the same task issue**. The issue itself is not replaced; instead:

1. **RED phase comment**: "## Slice Update — t1 / red" + test result
2. **GREEN phase comment**: "## Slice Update — t1 / green" + code result
3. **REFACTOR phase comment**: "## Slice Update — t1 / refactor" + final result

Each comment contains:

```yaml
kind: implementation-log
task_id: t1
stage: red | green | refactor
status: complete | blocked
files_changed: [...]
test_result: pass | fail
```

### The `stage` Field Changes Over Time

The `stage` field in the task issue's Machine Data section evolves as the slice progresses:

1. **Initially**: `stage: red`
   - The issue is created with this value
   - A RED comment is added when the failing test is written

2. **After RED passes**: The issue is **edited** to `stage: green`
   - The issue body's Machine Data `stage` field is updated from `red` to `green`
   - A GREEN comment is added when the minimal implementation is complete

3. **After GREEN passes**: The issue is **edited** to `stage: refactor`
   - The issue body's Machine Data `stage` field is updated from `green` to `refactor`
   - A REFACTOR comment is added when cleanup is done

4. **After REFACTOR passes**: The task issue is **closed**
   - The final Machine Data shows `status: closed`
   - The comments hold the full log of all three stages

### Example Timeline for Task Issue #1 ("Add Retry Cap")

```
Time T0: Issue created
  - stage: red
  - Comment added: RED phase result (failing test)

Time T1: Test passes
  - Issue updated: stage: green
  - Comment added: GREEN phase result (minimal code)

Time T2: Code complete
  - Issue updated: stage: refactor
  - Comment added: REFACTOR phase result (cleanup, tests rerun)

Time T3: Slice done
  - Issue closed
  - status: closed in Machine Data
```

---

## Phase 8: Implementation

### Execution Model

Phase 8 processes the task issues in dependency order:

- **Task #1** ("add retry cap"):
  - Starts at `stage: red`
  - Executes: Write failing test → update to `stage: green` → write code → update to `stage: refactor` → refactor → close

- **Task #2** ("add jitter"):
  - May run in parallel if `parallelizable: true` and files don't overlap, OR
  - Runs after Task #1 if `depends_on: [t1]`
  - Same progression: red → green → refactor → close

### Each Task Is One Issue

Critically, **each task is one issue, not three**. The common mistake is creating three issues per task (one for RED, one for GREEN, one for REFACTOR). Instead:

- **One issue per vertical slice**
- **Three comments per issue** (one for each stage)
- **One `stage` field that is updated in place**

This keeps the GitHub issue tree flat and makes the progress log readable in a single thread.

---

## Key Principles Recap

1. **Two behaviors → Two task issues** (one vertical slice per issue)
2. **Not RED/GREEN/REFACTOR as separate issues**, but as comments on the same issue
3. **`stage` field starts at `red` and is updated in place** to `green`, then to `refactor`
4. **Comments hold the detailed progress log** for each stage
5. **Closing the task issue signals completion** of the entire vertical slice

This design ensures that Phase 7 creates a clear DAG of work, and Phase 8 can execute it with a clean, readable record of progress in GitHub Issues.
