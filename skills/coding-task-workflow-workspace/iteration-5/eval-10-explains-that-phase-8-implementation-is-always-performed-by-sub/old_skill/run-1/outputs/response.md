# Evaluation: Phase 8 Execution Model with Three Tasks (A, B parallel; C sequential)

## Overview

The baseline `coding-task-workflow` skill has a precise execution model for Phase 8 that uses **subagents for parallel tasks only**. The task graph has three ready tasks:

- **Task A**: `parallel`, different files
- **Task B**: `parallel`, different files  
- **Task C**: `sequential`

The workflow will execute them in this order:

1. **Task A and B together** (in parallel) — delegated to two separate subagents
2. **Task C sequentially** — executed by the primary agent

This document explains exactly what the workflow does and who writes the code.

---

## Phase 8 Step 1: Load Task Graph and Determine Ready Tasks

Phase 8 begins after resuming with `RESUME=2026-04-27-add-rate-limit-logs`:

**Workflow Step 1** (workflow.md line 234):

> "Resolve `RESUME=<slug>` by loading the parent issue and descendant phase/task issues for that `work_id`. Do not rely on local phase files."

The workflow:
1. Loads the parent issue (#N)
2. Loads the closed task-graph issue (#N+7)
3. Parses the YAML in the task-graph issue body to get task definitions
4. Loads all open implementation task issues (#A, #B, #C)
5. Determines which tasks are ready: A, B, and C have `depends_on: []` (no dependencies)

---

## Phase 8 Step 2: Process in Dependency Order and Partition by Parallelism

**Workflow Step 2** (workflow.md line 235):

> "Process implementation task issues in dependency order. Run tasks labelled `parallel` concurrently when their dependencies are satisfied and they do not overlap on files."

The workflow:
1. Identifies ready tasks: A, B, C
2. Partitions by label:
   - **Parallel group**: A, B (both marked `parallel`)
   - **Sequential**: C
3. Checks for file overlap between A and B:
   - Task A modifies files in `src/http/client/`
   - Task B modifies files in `src/http/retry/`
   - No overlap ✓ → can run concurrently
4. Execution plan:
   ```
   Phase 8a: Launch subagent for Task A, launch subagent for Task B (concurrent)
   Phase 8b: Wait for both to complete
   Phase 8c: Execute Task C (sequential)
   ```

---

## Phase 8 Step 2a: Launch Subagents for Task A and B (Parallel)

When multiple parallel tasks are ready with no file overlap, the workflow launches dedicated subagents.

**Delegation Rules — Phase 8 (delegation-rules.md lines 101–143)**:

> ### When to use
> 
> Only for implementation task issues marked `parallel` whose dependencies are already satisfied. Sequential tasks are always executed by the primary agent.
> 
> ### How to partition
> 
> 1. Read the task-graph issue body and the open implementation task issues.
> 2. Identify task issues whose `depends_on` lists are fully satisfied.
> 3. From those ready tasks, select all tasks labelled `parallel`.
> 4. Each agent handles exactly one task issue.
> 5. Agents must not write to the same files. If file overlap is detected, convert the tasks to sequential execution.

### Subagent A for Task A

The primary agent launches a subagent to handle task A with a prompt based on the template:

```text
You are implementing task issue #A for work item 2026-04-27-add-rate-limit-logs.
Task ID: A
Stage: red

Read first:
- The Phase 6 plan issue: #N+6 (describes the rate-limit logging plan)
- The Phase 7 task-graph issue: #N+7 (contains the task definitions)
- Relevant source files:
  - src/http/client.ts
  - src/http/client.test.ts
  - src/logging/index.ts

Instructions:
1. Write the failing test first (RED) in src/http/client.test.ts.
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN) in src/http/client.ts.
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
- src/http/client.ts
- src/http/client.test.ts

Return:
- status (complete | blocked)
- files changed
- tests run and result (pass | fail)
- anything the primary agent should record as a comment on task issue #A
```

### Subagent B for Task B

The primary agent launches a second subagent to handle task B:

```text
You are implementing task issue #B for work item 2026-04-27-add-rate-limit-logs.
Task ID: B
Stage: red

Read first:
- The Phase 6 plan issue: #N+6 (describes the rate-limit logging plan)
- The Phase 7 task-graph issue: #N+7 (contains the task definitions)
- Relevant source files:
  - src/http/retry.ts
  - src/http/retry.test.ts
  - src/logging/index.ts

Instructions:
1. Write the failing test first (RED) in src/http/retry.test.ts.
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN) in src/http/retry.ts.
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
- src/http/retry.ts
- src/http/retry.test.ts

Return:
- status (complete | blocked)
- files changed
- tests run and result (pass | fail)
- anything the primary agent should record as a comment on task issue #B
```

### Who Writes the Code?

**Subagent A writes code for Task A**:
- Writes failing test in `src/http/client.test.ts`
- Writes implementation in `src/http/client.ts`
- Writes refactor improvements (if any)

**Subagent B writes code for Task B**:
- Writes failing test in `src/http/retry.test.ts`
- Writes implementation in `src/http/retry.ts`
- Writes refactor improvements (if any)

**Execution timing**: Both subagents run concurrently. The primary agent waits for both to complete before proceeding.

### Concurrency Guarantees

The task graph specification ensures no conflicts:
- Tasks marked `parallel` touch non-overlapping files
- Delegation rules verify file overlap before launching subagents
- If overlap is detected, tasks are converted to sequential execution

---

## Phase 8 Step 2b: Primary Agent Collects Results from Subagents

After both subagents complete, they return:

1. **Subagent A returns**:
   - Status: `complete`
   - Files changed: `src/http/client.ts`, `src/http/client.test.ts`
   - Tests run: `npm test -- --testNamePattern="client"` → PASS
   - Implementation log comment content (for the primary agent to record)

2. **Subagent B returns**:
   - Status: `complete`
   - Files changed: `src/http/retry.ts`, `src/http/retry.test.ts`
   - Tests run: `npm test -- --testNamePattern="retry"` → PASS
   - Implementation log comment content (for the primary agent to record)

### Primary Agent Records Subagent Work

The primary agent records each subagent's work as comments on the corresponding task issues:

```bash
# For Task A (subagent result)
gh issue comment #A --body <(cat <<'EOF'
## Slice Update — A / red

- **status**: complete
- **files_changed**: src/http/client.ts, src/http/client.test.ts
- **test_result**: fail (expected)
- **notes**: Test verifies that rate-limit info is logged in client. Currently fails because client does not capture rate-limit headers.

## Machine Data

\`\`\`yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: implementation-log
task_id: A
stage: red
status: complete
updated_at: "2026-04-27T16:00:00Z"
\`\`\`
EOF
)
```

Then proceed through GREEN and REFACTOR stages (similarly recorded as comments by the primary agent, but based on subagent reports).

Update task issues to reflect current stage and close when complete.

---

## Phase 8 Step 2c: Execute Task C (Sequential) — Primary Agent

Once Task A and B are complete and their task issues are closed, the workflow begins Task C.

**Who writes the code?**: The primary agent (never delegated).

**Workflow Step 3** (workflow.md lines 236–239):

> "For each task issue:
> a. **RED**: write a failing test that captures the behaviour. Run it and confirm it fails for the expected reason. Record the result as a comment on the task issue while the issue remains at `stage: red`.
> b. **GREEN**: update the same task issue to `stage: green`, write the minimal code to make the test pass, run it, and record the result as a comment on that issue.
> c. **REFACTOR**: update the same task issue to `stage: refactor`, clean up if needed, rerun the relevant tests, and record the outcome as another comment on that issue."

The primary agent:

1. **RED stage**: Write failing test for Task C
   - Edit task issue #C to update `stage: red` (if needed)
   - Write test in source file
   - Run test (fails as expected)
   - Record RED result as comment on #C

2. **GREEN stage**: Write implementation for Task C
   - Edit task issue #C to update `stage: green`
   - Write minimal implementation
   - Run test (passes)
   - Record GREEN result as comment on #C

3. **REFACTOR stage**: Clean up Task C
   - Edit task issue #C to update `stage: refactor`
   - Refactor code (if needed)
   - Rerun tests (pass)
   - Record REFACTOR result as comment on #C
   - Close task issue #C

---

## Complete Execution Timeline

```
Phase 8 Start:
├── Load task graph: A (parallel), B (parallel), C (sequential)
│
├── Phase 8a: Parallel execution (A and B concurrent)
│   ├── Subagent A executes: RED → GREEN → REFACTOR on Task A
│   │   └── Writes to: src/http/client.ts, src/http/client.test.ts
│   │   └── Files modified: git tracks changes from both files
│   │
│   └── Subagent B executes: RED → GREEN → REFACTOR on Task B
│       └── Writes to: src/http/retry.ts, src/http/retry.test.ts
│       └── Files modified: git tracks changes from both files
│
├── Phase 8b: Primary agent collects results
│   ├── Record Task A comments on issue #A
│   └── Record Task B comments on issue #B
│
├── Phase 8c: Sequential execution (C after A and B)
│   └── Primary agent executes: RED → GREEN → REFACTOR on Task C
│       └── Writes to: [Task C files per task-graph definition]
│       └── Record Task C comments on issue #C
│
└── Phase 8 End: All tasks complete, all task issues closed
    └── All modified files tracked in git worktree
```

---

## Key Rules

**Delegation Rule** (delegation-rules.md line 105):

> "Only for implementation task issues marked `parallel` whose dependencies are already satisfied. Sequential tasks are always executed by the primary agent."

**File Overlap Check** (delegation-rules.md line 113):

> "Agents must not write to the same files. If file overlap is detected, convert the tasks to sequential execution."

**Who Executes Task C**:
- Task C is marked `sequential` → always executed by primary agent
- Never delegated to a subagent
- Primary agent performs RED → GREEN → REFACTOR loop

**Concurrency of A and B**:
- Both marked `parallel`
- No file overlap (A: `src/http/client.*`, B: `src/http/retry.*`)
- Both dependencies satisfied (`depends_on: []`)
- Execute concurrently via separate subagents

**Full Context for Subagents** (delegation-rules.md line 10):

> "Full context in prompt: each subagent is stateless. Include all necessary context in the launch prompt — do not rely on shared state between agents."

Each subagent receives:
- Work item slug
- Task ID
- Task stage
- Links to plan and task-graph issues
- Explicit list of files they may write to
- Complete instructions for RED → GREEN → REFACTOR

**Recording from Subagent Results** (delegation-rules.md line 12):

> "GitHub is canonical: for Phases 1–11, subagents should return structured findings to the primary agent, and the primary agent records the durable artifact in GitHub issues/comments."

The primary agent is responsible for recording subagent results as comments on task issues.

---

## Summary

| Task | Label | Who Executes | Concurrency | Result Recording |
|------|-------|--------------|-------------|------------------|
| A | `parallel` | Subagent A | Concurrent with B | Primary agent records as comment on #A |
| B | `parallel` | Subagent B | Concurrent with A | Primary agent records as comment on #B |
| C | `sequential` | Primary agent | After A and B complete | Primary agent records as comment on #C |

**Code Writers**:
- **Task A**: Subagent A (concurrent)
- **Task B**: Subagent B (concurrent)
- **Task C**: Primary agent (sequential)

**Comment Recording**:
- All comments recorded by primary agent
- Each comment contains RED/GREEN/REFACTOR stage update
- All comments persisted on GitHub task issues

**No Local Files**:
- No `07-implementation-log.md`
- No per-task stage files
- All progress tracked in GitHub issue comments
