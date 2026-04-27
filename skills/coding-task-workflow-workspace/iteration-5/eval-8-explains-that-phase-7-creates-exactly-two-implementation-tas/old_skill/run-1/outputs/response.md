# Evaluation: Phase 7–8 Task Decomposition for Two Behaviors (Retry Cap + Jitter)

## Overview

For a plan with two distinct behaviors ("add a retry cap" and "add jitter"), the baseline `coding-task-workflow` skill creates **exactly two implementation task issues** in Phase 7. Each task issue represents one vertical TDD slice (RED → GREEN → REFACTOR) and is executed independently in Phase 8.

**Phase 7 Step 1** (workflow.md line 210):

> "Identify distinct behaviours to implement. Each behaviour becomes one vertical slice: RED → GREEN → REFACTOR."

**Phase 7 Step 5** (workflow.md line 214):

> "Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue."

---

## Phase 7: Task Graph Creation and Task Issue Creation

### Phase 7 Step 1: Identify Behaviors and Create Task Graph YAML

Phase 7 analyzes the approved plan and identifies two distinct behaviors:

1. **Behavior 1**: Add a retry cap (e.g., max 5 retries)
2. **Behavior 2**: Add jitter to the backoff calculation (e.g., ±10%)

For each behavior, Phase 7 creates a task in the task graph YAML:

```yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "2026-04-27T14:00:00Z"

tasks:
  - id: t1
    name: "Add retry cap (max 5 retries)"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/http/client.ts
      - src/http/client.test.ts

  - id: t2
    name: "Add jitter to backoff calculation"
    stage: red
    depends_on: []
    parallelizable: true
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts
```

### Why Exactly Two Tasks?

The workflow creates one task per **distinct behavior** (not per file, not per test, not per acceptance criterion). In this example:
- Behavior 1 (retry cap) → one task
- Behavior 2 (jitter) → one task

Both start at `stage: red`. Both are independent (`depends_on: []`) and can run concurrently (`parallelizable: true`).

### Phase 7 Step 4: Create Task-Graph Issue

Phase 7 creates one Phase 7 task-graph issue (#N+7) containing the YAML above:

```bash
gh issue create \
  --title "Task Graph — 2026-04-27-add-retry-mechanism" \
  --body-file <(cat <<'EOF'
## Summary

Decomposition of the approved plan into vertical TDD slices.

## Inputs

- Parent: #N (main parent)
- Depends on: #N+6 (plan issue)

## Deliverable

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "2026-04-27T14:00:00Z"

tasks:
  - id: t1
    name: "Add retry cap (max 5 retries)"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/http/client.ts
      - src/http/client.test.ts

  - id: t2
    name: "Add jitter to backoff calculation"
    stage: red
    depends_on: []
    parallelizable: true
    files:
      - src/http/retry.ts
      - src/http/retry.test.ts
\`\`\`

## Exit Criteria

- Phase 7 task-graph issue is closed.
- At least one implementation task issue has stage: red.
- Every implementation task issue has an explicit dependency list.
- No circular dependencies exist in the task graph YAML.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: task-graph
depends_on: [#N-6]
status: open
\`\`\`
EOF
) \
  --label agent:phase,phase:task-graph
```

This returns task-graph issue number, e.g., **#N+7**.

### Phase 7 Step 5: Create Implementation Task Issues

For each task in the YAML (t1 and t2), Phase 7 creates one implementation task issue:

#### Task Issue #1 (for behavior "Add retry cap"):

```bash
gh issue create \
  --title "Task t1 — Add retry cap (max 5 retries)" \
  --body-file <(cat <<'EOF'
## Summary

Enforce a maximum retry count (5) on the HTTP client. Requests that would exceed this limit fail immediately.

## Task Details

- **Current stage**: red
- **Task ID**: t1
- **Depends on tasks**: (none)

## Files

- src/http/client.ts
- src/http/client.test.ts

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t1
stage: red
parallelizable: false
depends_on: []
files:
  - src/http/client.ts
  - src/http/client.test.ts
status: open
\`\`\`
EOF
) \
  --label agent:task,phase:implement,sequential
```

This returns task issue number, e.g., **#N+8**.

#### Task Issue #2 (for behavior "Add jitter"):

```bash
gh issue create \
  --title "Task t2 — Add jitter to backoff calculation" \
  --body-file <(cat <<'EOF'
## Summary

Add random jitter (±10%) to the exponential backoff delay to prevent thundering herd. Formula: delay * (0.9 + 0.2 * random()).

## Task Details

- **Current stage**: red
- **Task ID**: t2
- **Depends on tasks**: (none)

## Files

- src/http/retry.ts
- src/http/retry.test.ts

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t2
stage: red
parallelizable: true
depends_on: []
files:
  - src/http/retry.ts
  - src/http/retry.test.ts
status: open
\`\`\`
EOF
) \
  --label agent:task,phase:implement,parallel
```

This returns task issue number, e.g., **#N+9**.

### Phase 7 Step 5b: Attach Task Issues to Task-Graph Issue

Phase 7 attaches both task issues to the task-graph issue:

```bash
# Attach t1 to task-graph
TASKGRAPH_NODE_ID=$(gh issue view N+7 --json id --jq .id)
TASK1_NODE_ID=$(gh issue view N+8 --json id --jq .id)
gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) { addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) { issue { number } } }' -f parentId="$TASKGRAPH_NODE_ID" -f subIssueId="$TASK1_NODE_ID"

# Attach t2 to task-graph
TASK2_NODE_ID=$(gh issue view N+9 --json id --jq .id)
gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) { addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) { issue { number } } }' -f parentId="$TASKGRAPH_NODE_ID" -f subIssueId="$TASK2_NODE_ID"
```

### Phase 7 Step 6: Close Task-Graph Issue

```bash
gh issue close N+7
```

### End of Phase 7

**Summary of GitHub state after Phase 7**:

```
Task-graph issue: #N+7 [CLOSED]
├── Implementation task #1 (t1): #N+8 [OPEN, stage: red]
└── Implementation task #2 (t2): #N+9 [OPEN, stage: red]
```

Both task issues start at `stage: red` in their Machine Data and issue body. Gate E verifies this condition before allowing the session to stop.

---

## Phase 8: Implementation and Stage Field Transitions

Phase 8 begins in a fresh session after resuming with `RESUME=2026-04-27-add-retry-mechanism`. It loads the task graph from the closed task-graph issue and executes the two tasks according to their parallelization rules.

### Phase 8 Execution: Task #1 (Retry Cap)

Task #1 is `parallelizable: false` and has no dependencies, so it executes first.

#### RED Stage

Phase 8 writes a failing test:

```bash
# Write failing test to src/http/client.test.ts
# Test: verify that a 6th retry attempt fails immediately without making a network call
```

Then run the test (it fails as expected):

```bash
npm test -- --testNamePattern="retry cap"
# FAIL: Test fails because client does not enforce max retries
```

Record the RED result as a comment on task issue #N+8:

```bash
gh issue comment N+8 --body <(cat <<'EOF'
## Slice Update — t1 / red

- **status**: complete
- **files_changed**: src/http/client.test.ts
- **test_result**: fail (expected)
- **notes**: Test verifies that a 6th retry attempt fails immediately. Currently fails because max-retry enforcement is not implemented.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: red
status: complete
updated_at: "2026-04-27T15:00:00Z"
\`\`\`
EOF
)
```

Update the task issue body to reflect `stage: red` (if not already there):

```bash
gh issue edit N+8 --body "...Task Details...
- **Current stage**: red
..."
```

**After RED**: Task issue #N+8 has:
- Body: `stage: red` (in "Current stage" field)
- Machine Data: `stage: red`
- Comments: [RED result comment]
- Status: open

#### GREEN Stage

Phase 8 writes implementation code to enforce max retries:

```bash
# Modify src/http/client.ts
# Add: const MAX_RETRIES = 5;
# Add logic to track and enforce retry count
```

Update the task issue to `stage: green`:

```bash
gh issue edit N+8 --body "...Task Details...
- **Current stage**: green
..."
```

Run the test (it now passes):

```bash
npm test -- --testNamePattern="retry cap"
# PASS: Test passes
```

Record the GREEN result as a comment on task issue #N+8:

```bash
gh issue comment N+8 --body <(cat <<'EOF'
## Slice Update — t1 / green

- **status**: complete
- **files_changed**: src/http/client.ts, src/http/client.test.ts
- **test_result**: pass
- **notes**: Implemented max-retry enforcement with MAX_RETRIES = 5. Test passes. A 6th retry attempt now fails immediately.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: green
status: complete
updated_at: "2026-04-27T15:10:00Z"
\`\`\`
EOF
)
```

**After GREEN**: Task issue #N+8 has:
- Body: `stage: green` (in "Current stage" field)
- Machine Data: `stage: green`
- Comments: [RED result, GREEN result]
- Status: open

#### REFACTOR Stage

Phase 8 cleans up (if needed) and reruns tests:

```bash
# Refactor: extract retry limit to a constant at module level
# Extract retry count tracking to a helper function
# No logic change; code clarity improvement
```

Update the task issue to `stage: refactor`:

```bash
gh issue edit N+8 --body "...Task Details...
- **Current stage**: refactor
..."
```

Rerun the tests (they still pass):

```bash
npm test
# PASS: All tests pass
```

Record the REFACTOR result as a comment on task issue #N+8:

```bash
gh issue comment N+8 --body <(cat <<'EOF'
## Slice Update — t1 / refactor

- **status**: complete
- **files_changed**: src/http/client.ts
- **test_result**: pass
- **notes**: Extracted retry tracking into RetryCounter class for clarity. Extracted MAX_RETRIES constant. All tests pass. No behavior change.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: implementation-log
task_id: t1
stage: refactor
status: complete
updated_at: "2026-04-27T15:20:00Z"
\`\`\`
EOF
)
```

Close the task issue:

```bash
gh issue close N+8
```

**After REFACTOR and close**: Task issue #N+8 has:
- Body: `stage: refactor` (in "Current stage" field)
- Machine Data: `stage: refactor`
- Comments: [RED result, GREEN result, REFACTOR result]
- Status: closed

### Phase 8 Execution: Task #2 (Jitter)

Task #2 is `parallelizable: true` and has no dependencies, so it can run concurrently with Task #1 or sequentially after. In this example, it runs after Task #1 completes (since Task #1 is sequential).

The flow is identical to Task #1:

#### RED Stage

```bash
# Write failing test for jitter
# Test: verify that backoff delay includes random variation
# Test fails (jitter not implemented yet)
```

Record RED result as comment on task issue #N+9.
Update task issue body to `stage: red`.

**After RED**: Task issue #N+9 has:
- Body: `stage: red`
- Machine Data: `stage: red`
- Comments: [RED result]
- Status: open

#### GREEN Stage

```bash
# Implement jitter in src/http/retry.ts
# Apply formula: delay * (0.9 + 0.2 * random())
# Test passes
```

Update task issue to `stage: green`.
Record GREEN result as comment on task issue #N+9.

**After GREEN**: Task issue #N+9 has:
- Body: `stage: green`
- Machine Data: `stage: green`
- Comments: [RED result, GREEN result]
- Status: open

#### REFACTOR Stage

```bash
# Extract jitter calculation to named function for clarity
# Rerun tests (pass)
```

Update task issue to `stage: refactor`.
Record REFACTOR result as comment on task issue #N+9.
Close the task issue.

**After REFACTOR and close**: Task issue #N+9 has:
- Body: `stage: refactor`
- Machine Data: `stage: refactor`
- Comments: [RED result, GREEN result, REFACTOR result]
- Status: closed

---

## Summary: Exact Task Count and Stage Lifecycle

### Number of Task Issues

**Exactly 2 task issues** are created:

1. **Task #1** (#N+8) — "Add retry cap (max 5 retries)"
   - Represents one vertical slice
   - Contains one behavior
2. **Task #2** (#N+9) — "Add jitter to backoff calculation"
   - Represents one vertical slice
   - Contains one behavior

### Stage Field Lifecycle

Each task issue follows the same stage progression:

| Phase | Issue #N+8 (Retry Cap) | Issue #N+9 (Jitter) | Recorded In |
|-------|------------------------|---------------------|------------|
| End of Phase 7 | `stage: red` | `stage: red` | Body + Machine Data |
| Phase 8 RED complete | `stage: red` | `stage: red` | Body + Comment |
| Phase 8 GREEN complete | `stage: green` | `stage: green` | Body + Comment |
| Phase 8 REFACTOR complete | `stage: refactor` | `stage: refactor` | Body + Comment |
| Issue closed | `stage: refactor` | `stage: refactor` | Body (final) |

### Progress Recording

Each task issue accumulates three comments:

```
Task issue #N+8 (Retry Cap) Timeline:
├── Comment 1: "## Slice Update — t1 / red" + RED test failure
├── Comment 2: "## Slice Update — t1 / green" + implementation success
├── Comment 3: "## Slice Update — t1 / refactor" + cleanup success
└── [Issue closed]

Task issue #N+9 (Jitter) Timeline:
├── Comment 1: "## Slice Update — t2 / red" + RED test failure
├── Comment 2: "## Slice Update — t2 / green" + implementation success
├── Comment 3: "## Slice Update — t2 / refactor" + cleanup success
└── [Issue closed]
```

**No local files are created.** All progress is recorded as comments on the task issues themselves.

### Stage Field Mutation

The `stage` field in the task issue body and Machine Data is **updated in place** (not replaced):

| Operation | Before | After |
|-----------|--------|-------|
| Phase 7 creates task | N/A | Body + Machine Data: `stage: red` |
| Phase 8 RED comment recorded | `stage: red` | Still `stage: red` (comment added) |
| Phase 8 GREEN begins | `stage: red` | Body updated to `stage: green` |
| Phase 8 GREEN comment recorded | `stage: green` | Still `stage: green` (comment added) |
| Phase 8 REFACTOR begins | `stage: green` | Body updated to `stage: refactor` |
| Phase 8 REFACTOR comment recorded | `stage: refactor` | Still `stage: refactor` (comment added) |
| Task issue closed | `stage: refactor` | Frozen at `stage: refactor` (issue closed) |

The issue body's `## Task Details` section is edited each time the stage changes:

```bash
# When transitioning RED → GREEN
gh issue edit N+8 --body-file <(cat <<'EOF'
## Task Details

- **Current stage**: green
- **Task ID**: t1
- **Depends on tasks**: (none)
EOF
)
```

---

## Key Rules

**Phase 7 Step 3** (workflow.md line 212):

> "Do not write all RED slices before any GREEN slices. Each vertical slice is independent."

This means: don't create all RED comments first, then all GREEN comments. Instead, each task executes its own RED → GREEN → REFACTOR cycle independently (though they may run in parallel if dependencies allow).

**Phase 8 Step 3** (workflow.md line 237–239):

> Record RED results as comments while issue remains at `stage: red`.
> Update issue to `stage: green`, record GREEN results as a comment.
> Update issue to `stage: refactor`, record REFACTOR results as a comment.

**Issue Lifecycle** (issue-hierarchy.md lines 313–315):

> Implementation slice begins — Create one task issue for the slice and initialize it with `stage: red`.
> Implementation slice progresses — Add RED / GREEN / REFACTOR comments to the same task issue and update its `stage` field in place.
> Implementation slice finishes — Close the task issue.
