# Evaluation: Phase 8 Execution Strategy with Parallel and Sequential Tasks

## Summary

**Scenario**: Resumed after Gate E with task graph containing three ready implementation tasks:
- Task A: `parallel`, touches files {x, y}
- Task B: `parallel`, touches files {z, w}  
- Task C: `sequential`

**Question**: How should Phase 8 execute them and who writes the code?

**Answer**:

1. **A and B execute concurrently** in parallel subagents (both ready, marked `parallel`, no file overlap)
2. **C executes sequentially after A and B complete** (marked `sequential`)
3. **Subagents write all code** — the primary agent orchestrates and records progress
4. **Primary agent** validates changes and updates GitHub after each subagent completes

---

## The Golden Rule: Phase 8 Implementation is Always Performed by Subagents

From `SKILL.md` Non-negotiable rule #5:

> Phase 8 implementation is always performed by implementation subagents. The primary agent orchestrates dependency order, parallel groups, file-overlap checks, and GitHub comments; it does not directly write the implementation slice itself.

**This is mandatory.** The primary agent never writes implementation code. Subagents always do.

---

## Execution Strategy Overview

### Step 1: Load State from GitHub

The primary agent resumes with `RESUME=2026-04-27-add-rate-limit-logs` in a fresh session.

```bash
# Read parent issue
gh issue view <parent-issue> --json number,title,body

# Read task-graph issue body to extract YAML
gh issue view <taskgraph-issue> --json number,title,body

# Read all task issues
gh issue view <task-a-issue> --json number,title,body,labels
gh issue view <task-b-issue> --json number,title,body,labels
gh issue view <task-c-issue> --json number,title,body,labels
```

**Result**: Primary agent has full state from GitHub:
- Task A: `stage: red`, `parallelizable: true`, `depends_on: []`, `files: [x, y]`
- Task B: `stage: red`, `parallelizable: true`, `depends_on: []`, `files: [z, w]`
- Task C: `stage: red`, `parallelizable: false`, `depends_on: []` (or other dependencies), `files: [...]`

### Step 2: Identify Ready Tasks

From `delegation-rules.md` Phase 8 partitioning rule #2:

> Identify task issues whose `depends_on` lists are fully satisfied.

All three tasks are ready (all have `depends_on: []` or dependencies satisfied).

### Step 3: Partition Into Execution Batches

From `delegation-rules.md` Phase 8 partitioning rules #3 and #4:

> From those ready tasks, select all non-overlapping tasks labelled `parallel` for the next parallel batch.
> If no safe parallel batch exists, select the next sequential or overlapping ready task and run exactly one implementation subagent for it.

**Batch 1 (Parallel)**: A and B
- Task A: `parallel: true`, files: {x, y}
- Task B: `parallel: true`, files: {z, w}
- **File overlap check**: {x, y} ∩ {z, w} = ∅ (no overlap)
- **Decision**: Run A and B concurrently ✅

**Batch 2 (Sequential)**: C
- Task C: `sequential: true` (or marked sequential)
- **Execution**: After A and B both complete
- **Decision**: Run C alone ✅

---

## Phase 8 Execution: Batch 1 (Parallel A and B)

### Subagent 1: Task A Implementation

The primary agent launches an implementation subagent for task A.

**Subagent prompt**:

```text
You are implementing task issue #NNN for work item 2026-04-27-add-rate-limit-logs.
Task ID: A
Stage: red

Read first:
- The Phase 6 plan issue: [plan summary or link]
- The Phase 7 task-graph issue: [taskgraph summary or link]
- Relevant source files: [list]

Instructions:
1. Write the failing test first (RED).
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN).
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
- src/rate-limit/storage.ts
- src/rate-limit/storage.test.ts

Return:
- status
- files changed
- tests run and result
- RED failure evidence, GREEN pass evidence, and REFACTOR pass evidence
- anything the primary agent should record as a comment on the task issue
```

**Subagent 1 executes**:
1. Writes test for behavior A (RED)
2. Implements minimal code (GREEN)
3. Refactors code (REFACTOR)
4. Returns results

### Subagent 2: Task B Implementation

**Simultaneously** with Subagent 1, the primary agent launches an implementation subagent for task B.

**Subagent prompt**:

```text
You are implementing task issue #MMM for work item 2026-04-27-add-rate-limit-logs.
Task ID: B
Stage: red

Read first:
- The Phase 6 plan issue: [plan summary or link]
- The Phase 7 task-graph issue: [taskgraph summary or link]
- Relevant source files: [list]

Instructions:
1. Write the failing test first (RED).
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN).
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
- src/rate-limit/backoff.ts
- src/rate-limit/backoff.test.ts

Return:
- status
- files changed
- tests run and result
- RED failure evidence, GREEN pass evidence, and REFACTOR pass evidence
- anything the primary agent should record as a comment on the task issue
```

**Subagent 2 executes** (in parallel with Subagent 1):
1. Writes test for behavior B (RED)
2. Implements minimal code (GREEN)
3. Refactors code (REFACTOR)
4. Returns results

### Parallel Execution: Key Rules

From `workflow.md` Phase 8 step 2:

> Run tasks labelled `parallel` concurrently when their dependencies are satisfied and they do not overlap on files.

**Why parallel is safe here**:
- ✅ Both dependencies satisfied (`depends_on: []`)
- ✅ Both marked `parallel: true`
- ✅ No file overlap: {x, y} and {z, w} are disjoint
- ✅ Each subagent writes to its own files only

**Timeline**:
```
T0: Subagent 1 launches    Subagent 2 launches
    ↓ RED (A)              ↓ RED (B)
    ↓ GREEN (A)            ↓ GREEN (B)
    ↓ REFACTOR (A)         ↓ REFACTOR (B)
T1: A complete             B complete
    ↓ returns              ↓ returns
T2: Primary agent receives both results, validates, records progress
```

### Primary Agent: Validate and Record (After Both A and B Complete)

From `delegation-rules.md` Phase 8 rule #7:

> The primary agent records durable GitHub issue comments and stage updates after reviewing each subagent's changed files and test output.

And from `workflow.md` Phase 8 step 4:

> After each subagent finishes, inspect its changed files and test output before updating or closing the task issue. Do not rely on the subagent summary alone.

**Primary agent actions for Task A**:

1. **Validate changes**:
   ```bash
   git diff HEAD -- src/rate-limit/storage.ts
   # Confirm only expected changes
   ```

2. **Validate tests**:
   ```bash
   npm test -- src/rate-limit/storage.test.ts
   # Confirm all tests pass
   ```

3. **Record progress as comments on task A issue**:
   ```bash
   gh issue comment <task-a-issue> --body '
   ## Slice Update — A / red

   - **status**: complete
   - **files_changed**: src/rate-limit/storage.ts, src/rate-limit/storage.test.ts
   - **test_result**: fail (expected)
   - **notes**: Test written for rate-limit storage interface

   ## Machine Data

   ```yaml
   work_id: 2026-04-27-add-rate-limit-logs
   kind: implementation-log
   task_id: A
   stage: red
   status: complete
   updated_at: 2026-04-27T16:00:00Z
   ```
   '
   ```

4. **Update task A issue body** to move stage from `red` to `green`:
   ```bash
   gh issue edit <task-a-issue> --body '
   [updated body with stage: green in Machine Data]
   '
   ```

5. **Add GREEN comment**:
   ```bash
   gh issue comment <task-a-issue> --body '
   ## Slice Update — A / green

   - **status**: complete
   - **files_changed**: src/rate-limit/storage.ts
   - **test_result**: pass
   - **notes**: Implemented minimal storage interface

   ## Machine Data

   ```yaml
   work_id: 2026-04-27-add-rate-limit-logs
   kind: implementation-log
   task_id: A
   stage: green
   status: complete
   updated_at: 2026-04-27T16:05:00Z
   ```
   '
   ```

6. **Update task A issue body** to move stage to `refactor`:
   ```bash
   gh issue edit <task-a-issue> --body '
   [updated body with stage: refactor in Machine Data]
   '
   ```

7. **Add REFACTOR comment**:
   ```bash
   gh issue comment <task-a-issue> --body '
   ## Slice Update — A / refactor

   - **status**: complete
   - **files_changed**: src/rate-limit/storage.ts, src/rate-limit/storage.test.ts
   - **test_result**: pass
   - **notes**: Added JSDoc, extracted constants

   ## Machine Data

   ```yaml
   work_id: 2026-04-27-add-rate-limit-logs
   kind: implementation-log
   task_id: A
   stage: refactor
   status: complete
   updated_at: 2026-04-27T16:10:00Z
   ```
   '
   ```

8. **Close task A**:
   ```bash
   gh issue close <task-a-issue>
   ```

**Repeat for Task B**:
Same process — validate, record comments, update stage, close.

### Result of Batch 1

Both A and B complete in parallel. Both issues closed. Time saved vs. sequential: ~50% (both run concurrently).

---

## Phase 8 Execution: Batch 2 (Sequential C)

After **both A and B are closed**, the primary agent launches Task C.

### Subagent 3: Task C Implementation

**Subagent prompt**:

```text
You are implementing task issue #LLL for work item 2026-04-27-add-rate-limit-logs.
Task ID: C
Stage: red

Read first:
- The Phase 6 plan issue: [plan summary or link]
- The Phase 7 task-graph issue: [taskgraph summary or link]
- Relevant source files: [list]
- Completed task issues: A (closed #NNN), B (closed #MMM)

Instructions:
1. Write the failing test first (RED).
2. Confirm the test fails for the right reason.
3. Write the minimal code to make it pass (GREEN).
4. Confirm the test passes.
5. Refactor if needed (REFACTOR).
6. Do not add untested code paths.

Files you may write to:
- src/rate-limit/middleware.ts
- src/rate-limit/middleware.test.ts

Return:
- status
- files changed
- tests run and result
- RED failure evidence, GREEN pass evidence, and REFACTOR pass evidence
- anything the primary agent should record as a comment on the task issue
```

**Subagent 3 executes**:
1. Writes test for behavior C (RED)
2. Implements minimal code (GREEN)
3. Refactors code (REFACTOR)
4. Returns results

### Primary Agent: Validate and Record (After C Completes)

Same validation and recording process as A and B:
- Validate file changes
- Validate test results
- Add RED, GREEN, REFACTOR comments to task C issue
- Update stage field in body
- Close task C issue

### Result of Batch 2

Task C completes. Issue closed.

---

## Complete Execution Timeline

```
T0: Primary agent loads state
    ↓
T1: Subagent A launches (parallel)    Subagent B launches (parallel)
    
    A: RED → GREEN → REFACTOR         B: RED → GREEN → REFACTOR
    (writes to x, y)                  (writes to z, w)
    
    ↓ (both complete)                 ↓ (both complete)
T2: Primary agent validates A         Primary agent validates B
    Records 3 comments (A)            Records 3 comments (B)
    Updates stage (A)                 Updates stage (B)
    Closes task A                     Closes task B
    ↓                                 ↓
T3: Subagent C launches (sequential)
    
    C: RED → GREEN → REFACTOR
    (writes to middleware files)
    
    ↓ (completes)
T4: Primary agent validates C
    Records 3 comments (C)
    Updates stage (C)
    Closes task C
    ↓
T5: Phase 8 complete, all tasks done
```

---

## Who Writes the Code: Subagents, Not Primary Agent

From `SKILL.md`:

> Phase 8 implementation is always performed by implementation subagents. The primary agent orchestrates dependency order, parallel groups, file-overlap checks, and GitHub comments; it does not directly write the implementation slice itself.

**Subagents write**:
- ✅ Tests (RED)
- ✅ Implementation code (GREEN)
- ✅ Refactored code (REFACTOR)
- ✅ Comments on issue with progress details

**Primary agent writes**:
- ✅ GitHub issue comments (recorded by primary, content from subagent)
- ✅ GitHub issue stage field updates
- ✅ GitHub issue close command
- ❌ Does NOT write implementation code

**Why subagents?**
From `README.md`:

> **TDD-first implementation**: work is broken into vertical red→green→refactor slices; implementation always runs through subagents, with safe parallel batches when task dependencies and write paths allow.

Subagents are specialized for TDD implementation. They:
1. Write tests first (RED)
2. Implement minimally (GREEN)
3. Refactor safely (REFACTOR)
4. Never add untested code

---

## Partition Logic (Detailed)

From `delegation-rules.md` Phase 8 partitioning:

### Rules Checklist for Tasks A and B

**Are they ready?**
- Task A: `depends_on: []` → Yes ✅
- Task B: `depends_on: []` → Yes ✅

**Are they marked `parallel`?**
- Task A: `parallelizable: true` → Yes ✅
- Task B: `parallelizable: true` → Yes ✅

**Do they overlap on files?**
- Task A files: {x, y}
- Task B files: {z, w}
- Overlap: {x, y} ∩ {z, w} = ∅ → No overlap ✅

**Decision**: Run A and B concurrently ✅

### Rules Checklist for Task C

**Is it ready after A and B close?**
- Task C: `depends_on: []` or dependencies on [A, B] → After A and B close, yes ✅

**Is it marked `sequential`?**
- Task C: `parallelizable: false` (sequential) → Yes ✅

**Decision**: Run C alone, after A and B ✅

---

## File Overlap Detection: Critical Rule

From `delegation-rules.md` Phase 8 rule #6:

> Agents must not write to the same files. If file overlap is detected, convert the tasks to sequential subagent execution.

**Example if A and B overlapped**:
- Task A files: {x, y}
- Task B files: {y, z}  ← Share file 'y'
- Overlap: {x, y} ∩ {y, z} = {y} → Overlap detected ✗

**What happens**:
1. Detect conflict
2. Convert B to sequential (run after A)
3. Launch Subagent 1 (Task A)
4. Wait for Subagent 1 complete and close Task A
5. Launch Subagent 2 (Task B)
6. Wait for Subagent 2 complete and close Task B

**In our scenario**: No overlap, so parallel is safe.

---

## Strict TDD Rules Enforced by Subagents

From `workflow.md` Phase 8 step 5:

> Never add untested code paths. If a useful branch is not yet covered by a test, do not add it.

Subagents enforce:
1. **RED first**: Write test before code
2. **Failing test**: Confirm it fails for the right reason (not a typo)
3. **Minimal GREEN**: Make test pass with minimal code (no extra features)
4. **Test passes**: Confirm GREEN before refactor
5. **No untested paths**: Never implement beyond what test covers

---

## Primary Agent Responsibilities (Not Implementation)

The primary agent:

1. **Orchestrate**: Determine execution order
2. **Partition**: Identify parallel-safe batches
3. **Launch**: Invoke subagents with correct context
4. **Validate**: Check file changes and test results
5. **Record**: Add GitHub comments with progress
6. **Update**: Change stage field in task issue body
7. **Close**: Close completed task issues
8. **Inspect**: Read actual file diffs, not just summaries

From `workflow.md` Phase 8 step 4:

> After each subagent finishes, inspect its changed files and test output before updating or closing the task issue. Do not rely on the subagent summary alone.

**This is critical**: Primary agent must verify subagent work by reading actual files and test output.

---

## Complete Execution Model

| Phase | Actor | Action |
|-------|-------|--------|
| 8.1 | Primary | Load state from GitHub |
| 8.2 | Primary | Partition tasks: Batch 1 = {A, B parallel}, Batch 2 = {C sequential} |
| 8.3 | Primary | Launch Subagent 1 for Task A |
| 8.3 | Primary | Launch Subagent 2 for Task B (in parallel) |
| 8.3-8.4 | Subagent 1 | RED → GREEN → REFACTOR (Task A) |
| 8.3-8.4 | Subagent 2 | RED → GREEN → REFACTOR (Task B) |
| 8.4 | Primary | Validate A file changes and test results |
| 8.4 | Primary | Record 3 comments on Task A issue |
| 8.4 | Primary | Update Task A stage in body (red → green → refactor) |
| 8.4 | Primary | Close Task A issue |
| 8.4 | Primary | Validate B file changes and test results |
| 8.4 | Primary | Record 3 comments on Task B issue |
| 8.4 | Primary | Update Task B stage in body |
| 8.4 | Primary | Close Task B issue |
| 8.5 | Primary | Launch Subagent 3 for Task C (after A, B closed) |
| 8.5-8.6 | Subagent 3 | RED → GREEN → REFACTOR (Task C) |
| 8.6 | Primary | Validate C file changes and test results |
| 8.6 | Primary | Record 3 comments on Task C issue |
| 8.6 | Primary | Update Task C stage in body |
| 8.6 | Primary | Close Task C issue |
| 8.6 | Primary | Phase 8 complete, ready for Phase 9 (Review) |

---

## Conclusion

**Phase 8 Execution Strategy for Tasks A, B (parallel), and C (sequential)**:

1. **Batch 1 (Parallel)**: A and B run **concurrently**
   - Subagent 1 implements Task A (RED → GREEN → REFACTOR)
   - Subagent 2 implements Task B (RED → GREEN → REFACTOR)
   - No file overlap, both `parallel`, both ready → safe to run together
   - Primary agent validates and records both in parallel

2. **Batch 2 (Sequential)**: C runs **after A and B close**
   - Subagent 3 implements Task C (RED → GREEN → REFACTOR)
   - Task C marked `sequential` and/or depends on completed tasks
   - Primary agent validates and records

3. **Who writes code**:
   - ✅ **Subagents** write all implementation code, tests, refactored code
   - ✅ **Primary agent** orchestrates, validates, records progress
   - ❌ Primary agent does NOT write implementation code

4. **Recording**:
   - Subagents return results
   - Primary agent adds 3 comments per task (RED, GREEN, REFACTOR)
   - Primary agent updates stage field in body after each comment
   - Primary agent closes task issue when complete

5. **Validation**:
   - Primary agent inspects actual file diffs (not just summaries)
   - Primary agent runs tests to confirm results
   - Primary agent records findings in GitHub comments
