# Evaluation: Phase 7–8 Task Decomposition for Two Behaviors

## Summary

**Scenario**: The approved plan has two behaviors: **add a retry cap** and **add jitter** (extending retry mechanism).

**Question**: In Phase 7 and Phase 8, describe exactly what implementation task issues to create for those two behaviors, where progress is recorded, and how the `stage` field evolves.

**Answer**: 

- **Phase 7 creates exactly 2 implementation task issues** (one per behavior, each a vertical slice)
- **Each task issue** starts with `stage: red` and progresses through `green` then `refactor`
- **RED/GREEN/REFACTOR progress is recorded as three separate comments** on each task issue
- **The `stage` field in Machine Data** is updated on the task issue body as work progresses
- **All progress is durable** in GitHub; no local files

---

## Understanding Vertical Slices

From `workflow.md` Phase 7 step 1:

> Identify distinct behaviours to implement. Each behaviour becomes one vertical slice: RED → GREEN → REFACTOR.

A **vertical slice** is:
- One independent behavior
- Starts with a failing test (RED)
- Moves to working code (GREEN)
- Polished and refactored (REFACTOR)
- Recorded as comments on a single task issue

From the README example (retry mechanism with cap and jitter):

> builds a TDD task graph (write test for single retry → write test for max retries → implement → add jitter → refactor), implements with three red→green→refactor slices

This tells us that **behaviors can be further decomposed into testable slices**. For our example with two behaviors (retry cap and jitter), the decomposition might be:

### Option A: Two Behaviors → Two Tasks (Simple)

If the behaviors are truly independent:
- Task 1: Add retry cap (one test, one implementation, one refactor)
- Task 2: Add jitter (one test, one implementation, one refactor)

### Option B: Two Behaviors → Multiple Tasks (Complex)

If behaviors have dependencies or need intermediate tests:
- Task 1: Add retry cap (test cap logic independently)
- Task 2: Add jitter (test jitter independently, depends on cap)

For this evaluation, I'll use **Option A** (two behaviors = two tasks) as the clearest case, but I'll note that the skill allows for further decomposition based on dependencies.

---

## Phase 7: Creating Implementation Task Issues

### Step 1: Create the task-graph issue with YAML

The Phase 7 task-graph issue contains the YAML that defines the two tasks:

```bash
gh issue create \
  --title "Task Graph — retry-with-cap-and-jitter" \
  --body-file taskgraph_body.md \
  --label "agent:phase" \
  --label "phase:task-graph"
```

**taskgraph_body.md**:

```markdown
## Summary

Task graph for retry mechanism: add cap on retries, then add jitter to backoff delays.

## Inputs

- Approved plan: #N+6

## Deliverable

```yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "2026-04-27T15:00:00Z"

tasks:
  - id: t1
    name: "Add retry cap — max 5 attempts"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts

  - id: t2
    name: "Add jitter to exponential backoff"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts
```

## Exit Criteria

- At least one task has `stage: red`
- Every task has an explicit `depends_on` list
- No circular dependencies

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: task-graph
status: open
depends_on:
  - plan
```
```

**Result**: Task-graph issue created, e.g., `#N+7`.

### Step 2: Create one implementation task issue per vertical slice

**Task 1: Add retry cap**

```bash
gh issue create \
  --title "Task: t1 — Add retry cap — max 5 attempts" \
  --body-file task_t1_body.md \
  --label "agent:task" \
  --label "phase:implement" \
  --label "sequential"
```

**task_t1_body.md**:

```markdown
## Summary

Write failing test for retry cap at 5 attempts, then implement minimal code to pass test, then refactor for clarity.

## Task Details

- **Current stage**: red
- **Task ID**: t1
- **Depends on tasks**: (none)

## Files

- src/http/retry.ts
- src/http/retry.test.ts

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t1
stage: red
parallelizable: false
depends_on: []
files:
  - src/http/retry.ts
  - src/http/retry.test.ts
status: open
```
```

**Result**: Task t1 issue created, e.g., `#N+7a`.

**Task 2: Add jitter**

```bash
gh issue create \
  --title "Task: t2 — Add jitter to exponential backoff" \
  --body-file task_t2_body.md \
  --label "agent:task" \
  --label "phase:implement" \
  --label "sequential"
```

**task_t2_body.md**:

```markdown
## Summary

Write failing test for jitter (randomness) in backoff delays, then implement, then refactor.

## Task Details

- **Current stage**: red
- **Task ID**: t2
- **Depends on tasks**: t1

## Files

- src/http/retry.ts
- src/http/retry.test.ts

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t2
stage: red
parallelizable: false
depends_on: [t1]
files:
  - src/http/retry.ts
  - src/http/retry.test.ts
status: open
```
```

**Result**: Task t2 issue created, e.g., `#N+7b`.

### Step 3: Attach task issues to task-graph

```bash
TASKGRAPH_NODE=$(gh issue view <taskgraph-issue> --json id --jq .id)

for TASK_ISSUE in <t1-issue> <t2-issue>; do
  TASK_NODE=$(gh issue view $TASK_ISSUE --json id --jq .id)
  
  gh api graphql -f query='
    mutation($parentId: ID!, $subIssueId: ID!) {
      addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
        issue { number }
      }
    }' \
    -f parentId="$TASKGRAPH_NODE" \
    -f subIssueId="$TASK_NODE"
done
```

### Step 4: Close task-graph issue

```bash
gh issue close <taskgraph-issue>
```

**Result**: Task-graph issue is closed. Gate E is satisfied. Phase 8 begins in a fresh session.

---

## Phase 7 Summary: What Was Created

| Artifact | ID | Type | Status | Role |
|----------|----|----|--------|------|
| Task-graph | #N+7 | `phase:task-graph` | Closed | Container for YAML + task issues |
| Task 1 | #N+7a | `agent:task, phase:implement` | Open, `stage: red` | Retry cap behavior |
| Task 2 | #N+7b | `agent:task, phase:implement` | Open, `stage: red` | Jitter behavior |

---

## Phase 8: Execution and Progress Recording

Phase 8 resumes in a fresh session with `RESUME=2026-04-27-add-retry-mechanism`.

### Step 1: Load state from GitHub

```bash
# Fetch task-graph to read YAML
gh issue view <taskgraph-issue> --json number,title,body

# For each task, fetch current state
gh issue view <t1-issue> --json number,title,body,labels
gh issue view <t2-issue> --json number,title,body,labels

# Parse Machine Data blocks to determine current stage
```

### Step 2: Process tasks in dependency order

From the task-graph YAML:
- Task t1: `depends_on: []` — no dependencies, ready immediately
- Task t2: `depends_on: [t1]` — waits for t1 to complete

Execute t1, then t2 (sequential, as marked in YAML).

---

## Task t1 Execution: Add Retry Cap

### RED Stage

The implementation subagent is launched for task #N+7a with stage `red`.

**Subagent action**:
1. Read the task issue to understand the slice
2. Write a failing test for retry cap logic
3. Run the test and confirm it fails for the expected reason
4. **Record RED result as a comment** on the task issue

```bash
gh issue comment <t1-issue> --body '
## Slice Update — t1 / red

- **status**: complete
- **files_changed**: src/http/retry.test.ts
- **test_result**: fail (expected)
- **notes**: Test written: "should return error when retries exceed cap of 5". Test fails: "cap not yet implemented"

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: red
status: complete
updated_at: 2026-04-27T16:00:00Z
```
'
```

**Update task issue body** to reflect new stage:

The issue body is updated to change `stage: red` in the Machine Data to `stage: green`:

```bash
# Body now has Machine Data with:
# stage: green
```

**Result**: 
- Comment #1 recorded on #N+7a (RED result)
- Task issue stage changed to green in body

### GREEN Stage

The same implementation subagent continues (or a new one resumes at green stage).

**Subagent action**:
1. Read the task issue; see `stage: green` in Machine Data
2. Write minimal code to make the failing test pass
3. Run the test and confirm it passes
4. **Record GREEN result as a second comment** on the task issue

```bash
gh issue comment <t1-issue> --body '
## Slice Update — t1 / green

- **status**: complete
- **files_changed**: src/http/retry.ts
- **test_result**: pass
- **notes**: Implemented retry cap at 5 attempts. Test now passes. No cleanup needed yet.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: green
status: complete
updated_at: 2026-04-27T16:05:00Z
```
'
```

**Update task issue body** to reflect new stage:

```bash
# Body Machine Data now has:
# stage: refactor
```

**Result**:
- Comment #2 recorded on #N+7a (GREEN result)
- Task issue stage changed to refactor in body

### REFACTOR Stage

The subagent continues.

**Subagent action**:
1. Read the task issue; see `stage: refactor` in Machine Data
2. Clean up code, add clarity, improve test coverage if needed
3. Rerun the test and confirm it still passes
4. **Record REFACTOR result as a third comment** on the task issue

```bash
gh issue comment <t1-issue> --body '
## Slice Update — t1 / refactor

- **status**: complete
- **files_changed**: src/http/retry.ts, src/http/retry.test.ts
- **test_result**: pass
- **notes**: Added JSDoc comments and extracted magic number 5 to constant MAX_RETRIES. All tests still pass.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: refactor
status: complete
updated_at: 2026-04-27T16:10:00Z
```
'
```

**Update task issue body** to mark task complete:

```bash
# Body Machine Data now has:
# stage: refactor
# status: closed (or left for explicit close command)
```

### Close Task t1

```bash
gh issue close <t1-issue>
```

**Result**: 
- Comment #3 recorded on #N+7a (REFACTOR result)
- Task issue #N+7a closed
- Task t1 complete; t2 can now begin (since it depends_on t1)

---

## Task t1 Issue Lifecycle (Complete)

```
#N+7a [agent:task, phase:implement] Task: t1 — Add retry cap
  status: open
  
  • [BODY]
    - Summary: Add retry cap vertical slice
    - Task Details: t1, depends_on: []
    - Files: src/http/retry.ts, src/http/retry.test.ts
    - Progress Log: (placeholder)
    - Machine Data: stage: red, status: open
  
  • [COMMENT 1] RED Stage Update
    - Failing test written
    - Test result: fail (expected)
    - Machine Data: stage: red, status: complete, updated_at: T16:00:00Z
  
  • [BODY UPDATED]
    - Machine Data stage: green
  
  • [COMMENT 2] GREEN Stage Update
    - Minimal code implementation
    - Test result: pass
    - Machine Data: stage: green, status: complete, updated_at: T16:05:00Z
  
  • [BODY UPDATED]
    - Machine Data stage: refactor
  
  • [COMMENT 3] REFACTOR Stage Update
    - Code cleanup and clarity
    - Test result: pass
    - Machine Data: stage: refactor, status: complete, updated_at: T16:10:00Z
  
  → [CLOSED]
```

---

## Task t2 Execution: Add Jitter

### RED Stage

After t1 closes, the implementation subagent is launched for task #N+7b with stage `red`.

**Subagent action**:
1. Read task t2 issue; see `stage: red`
2. Check that dependency (t1) is closed
3. Write failing test for jitter (randomness in backoff)
4. Record RED result as comment

```bash
gh issue comment <t2-issue> --body '
## Slice Update — t2 / red

- **status**: complete
- **files_changed**: src/http/retry.test.ts
- **test_result**: fail (expected)
- **notes**: Test written: "should add randomness to backoff delays". Test fails: "jitter not yet implemented"

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t2
stage: red
status: complete
updated_at: 2026-04-27T16:15:00Z
```
'
```

**Update task issue body**: `stage: green`

### GREEN Stage

```bash
gh issue comment <t2-issue> --body '
## Slice Update — t2 / green

- **status**: complete
- **files_changed**: src/http/retry.ts
- **test_result**: pass
- **notes**: Implemented jitter using Math.random() to add 0-20% randomness to backoff. Test passes.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t2
stage: green
status: complete
updated_at: 2026-04-27T16:20:00Z
```
'
```

**Update task issue body**: `stage: refactor`

### REFACTOR Stage

```bash
gh issue comment <t2-issue> --body '
## Slice Update — t2 / refactor

- **status**: complete
- **files_changed**: src/http/retry.ts, src/http/retry.test.ts
- **test_result**: pass
- **notes**: Extracted jitter formula to constant JITTER_RANGE, added test for edge cases (min 1ms, max 20ms jitter). All tests pass.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t2
stage: refactor
status: complete
updated_at: 2026-04-27T16:25:00Z
```
'
```

**Update task issue body**: `status: closed`

### Close Task t2

```bash
gh issue close <t2-issue>
```

---

## Phase 8 Summary: How `stage` Evolves

For **each task**, the `stage` field follows this lifecycle:

| When | Stage | Location | How It Changes |
|------|-------|----------|-----------------|
| **Phase 7 creates task** | `red` | Machine Data in task issue body | Initial state |
| **RED comment added** | `red` | Still `red` in body; progress in comment | Subagent records RED work |
| **Transitioning to GREEN** | `green` | Task issue body updated by primary agent | Primary agent updates body |
| **GREEN comment added** | `green` | Still `green` in body; progress in comment | Subagent records GREEN work |
| **Transitioning to REFACTOR** | `refactor` | Task issue body updated by primary agent | Primary agent updates body |
| **REFACTOR comment added** | `refactor` | Still `refactor` in body; progress in comment | Subagent records REFACTOR work |
| **Task complete** | `refactor` | Task issue closed | Task issue closed |

**Key insight**: 
- The `stage` field indicates the *current* stage of the task
- Progress is *always* recorded as *separate comments* on the task issue
- The body Machine Data is updated only when transitioning from one stage to the next
- Comments provide the detailed history; the body Machine Data provides the current state

---

## Complete GitHub Issue Tree for Both Tasks

```
#N+7 [phase:task-graph] Task Graph (CLOSED)
  ├─ [BODY] YAML with tasks t1 and t2
  
  ├─ #N+7a [agent:task, phase:implement] Task: t1 — Add retry cap (CLOSED)
  │  ├─ [BODY] Summary, Task Details (t1, depends_on: []), Files, Machine Data (final: stage: refactor, status: closed)
  │  ├─ [COMMENT 1] RED — Test written, fails as expected
  │  ├─ [COMMENT 2] GREEN — Minimal implementation, test passes
  │  └─ [COMMENT 3] REFACTOR — Code polish, tests still pass
  │
  └─ #N+7b [agent:task, phase:implement] Task: t2 — Add jitter (CLOSED)
     ├─ [BODY] Summary, Task Details (t2, depends_on: [t1]), Files, Machine Data (final: stage: refactor, status: closed)
     ├─ [COMMENT 1] RED — Test written, fails as expected
     ├─ [COMMENT 2] GREEN — Minimal implementation, test passes
     └─ [COMMENT 3] REFACTOR — Code polish, tests still pass
```

---

## Key Rules (From the Skill)

From `workflow.md` Phase 7:

> 1. Identify distinct behaviours to implement. Each behaviour becomes one vertical slice: RED → GREEN → REFACTOR.
> 5. Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue. Label each `agent:task`, `phase:implement`, plus `parallel` or `sequential` as appropriate. Initialize each task issue with `stage: red`; RED, GREEN, and REFACTOR progress stays on that same issue as comments rather than separate issues.

From `workflow.md` Phase 8:

> 3. For each task issue, launch an implementation subagent with the task issue, plan context, relevant files, allowed write paths, current stage, and exact tests to run. The subagent performs the full RED → GREEN → REFACTOR slice:
>     a. **RED**: write a failing test that captures the behaviour. Run it and confirm it fails for the expected reason. Record the result as a comment on the task issue while the issue remains at `stage: red`.
>     b. **GREEN**: update the same task issue to `stage: green`, write the minimal code to make the test pass, run it, and record the result as a comment on that issue.
>     c. **REFACTOR**: update the same task issue to `stage: refactor`, clean up if needed, rerun the relevant tests, and record the outcome as another comment on that issue.

---

## Conclusion

For two behaviors (add retry cap, add jitter):

- **Phase 7 creates exactly 2 implementation task issues** (t1 for cap, t2 for jitter)
- **Each task issue** contains one vertical slice and starts with `stage: red`
- **Phase 8 executes each task** through RED → GREEN → REFACTOR
- **Progress is recorded** as three separate comments on each task issue (one per stage)
- **The `stage` field** in the task issue's Machine Data is updated in place by the primary agent
- **Comments provide history**; Machine Data provides current state
- **All progress is durable** in GitHub; no local files

Both tasks complete with all code changes integrated, all tests passing, and complete audit trail in GitHub.
