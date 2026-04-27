# Evaluation: Phase 6–8 GitHub-Native Recording Flow

## Summary

**Task**: Gate D has passed. Explain how `coding-task-workflow` now records Phase 6 approval, Phase 7 task graph, and Phase 8 implementation log now that local files (`05-plan.md`, `06-task-graph.yaml`, `07-implementation-log.md`) are gone.

**Answer**: All three now live in GitHub as issue bodies and comments:

- **Phase 6 approval** → Explicit comment on the plan issue with Machine Data
- **Phase 7 task graph** → YAML in the task-graph issue body (not a separate artifact subissue)
- **Phase 8 implementation log** → RED/GREEN/REFACTOR comments on each task issue (not a local file)

---

## What Has Changed

### Before (Legacy)
- `05-plan.md` — local file with approved plan
- `06-task-graph.yaml` — local file with task DAG
- `07-implementation-log.md` — local file with RED/GREEN/REFACTOR progress

### Now (Current)
- ❌ No `05-plan.md` — plan lives in issue body, approval in issue comment
- ❌ No `06-task-graph.yaml` — YAML lives in issue body
- ❌ No `07-implementation-log.md` — progress lives in issue comments

The critical rule from `artifact-schema.md`:

> Each implementation task issue represents one vertical slice. Task issue state replaces `07-implementation-log.md`.

And from `issue-hierarchy.md`:

> For Phase 7 specifically, keep the task graph YAML in the phase issue body. Do not create a separate `task-graph.yaml` artifact subissue.

---

## Phase 6: Approval Recording

### Where the Approval Lives

**Location**: A comment on the Phase 6 `phase:plan` issue (the plan issue itself, not a separate artifact).

### How to Record Approval

**Step 1: Plan is written and presented**

The Phase 6 plan issue exists with body containing:
- Goal / Non-Goals
- Recommended Approach
- Alternatives Considered
- File-by-File Implementation Map
- Verification Guidance
- Approval section (initially empty)
- Machine Data YAML

**Step 2: Human reviews and approves**

The human reads the plan and provides explicit approval. This is a required gate (Gate D).

**Step 3: Record approval as an issue comment**

Use `gh issue comment` to add an approval comment with structured Machine Data:

```bash
gh issue comment <plan-issue-number> --body '
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: 2026-04-27T14:32:00Z
```
'
```

**Result**: Comment appears on the plan issue with:
- Human-readable approval statement
- Timestamped Machine Data block marking status as `approved`

### Issue Lifecycle for Phase 6

```
#N+6 [phase:plan] Implementation plan
  status: open (initially)
  
  • [BODY] Plan content (Goal, Approach, Map, Verification, etc.)
  
  • [COMMENT 1] Approval comment with Machine Data
                - approved_by: human
                - status: approved
                - approved_at: ISO8601
```

Then close the issue:

```bash
gh issue close <plan-issue-number>
```

**Result**: Plan issue is closed. Gate D is satisfied when:
1. Plan issue is **closed**
2. Plan issue has an **explicit approval comment** with Machine Data

---

## Phase 7: Task Graph Recording

### Where the Task Graph Lives

**Location**: In the body of the Phase 7 `phase:task-graph` issue as a fenced YAML block.

**NOT** in a separate `task-graph.yaml` artifact subissue. The YAML stays in the phase issue body.

### How to Record the Task Graph

**Step 1: Create the task-graph issue**

```bash
gh issue create \
  --title "Task Graph — 2026-04-27-add-rate-limiting" \
  --body-file taskgraph_body.md \
  --label "agent:phase" \
  --label "phase:task-graph"
```

**Step 2: Write the task-graph issue body**

The body includes:
- `## Summary` — One sentence describing the task graph
- `## Inputs` — References to the plan issue and dependencies
- `## Deliverable` — **Fenced YAML task graph** (the actual artifact)
- `## Exit Criteria` — Copied from Gate E
- `## Machine Data` — YAML block with phase metadata

**Example body** (using template from `references/templates/task-graph.yaml`):

```markdown
## Summary

Task graph for rate limiting feature: 5 vertical TDD slices with sequential and parallel execution.

## Inputs

- Approved plan: #N+6

## Deliverable

```yaml
work_id: 2026-04-27-add-rate-limiting
phase: task-graph
status: complete
updated_at: "2026-04-27T15:00:00Z"

tasks:
  - id: t1
    name: "Create rate-limit storage abstraction"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/ratelimit/storage.ts
      - src/ratelimit/storage.test.ts

  - id: t2
    name: "Implement in-memory sliding-window counter"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/ratelimit/memory-store.ts
      - src/ratelimit/memory-store.test.ts

  - id: t3
    name: "Create rate-limit check middleware"
    stage: red
    depends_on: [t2]
    parallelizable: false
    files:
      - src/middleware/rate-limit.ts
      - src/middleware/rate-limit.test.ts

  - id: t4
    name: "Add rate-limit headers to responses"
    stage: red
    depends_on: [t3]
    parallelizable: false
    files:
      - src/middleware/rate-limit.ts
      - src/middleware/rate-limit.test.ts

  - id: t5
    name: "Add environment configuration"
    stage: red
    depends_on: [t4]
    parallelizable: false
    files:
      - src/config/index.ts
      - src/config/index.test.ts
```

## Exit Criteria

- Task graph is closed
- At least one task has `stage: red`
- Every task has an explicit `depends_on` list
- No circular dependencies exist

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: phase
phase: task-graph
status: open
depends_on:
  - plan
```
```

### Key Rule About Task Graph Location

From `artifact-schema.md`:

> The Phase 7 task graph is phase-owned: keep the fenced `yaml` block in the `phase:task-graph` issue body rather than creating a separate `task-graph.yaml` artifact subissue.

**This is critical**: The YAML does NOT go in a separate child issue. It stays in the phase issue body.

### Phase 7 Issue Lifecycle

```
#N+7 [phase:task-graph] Task Graph
  status: open
  
  • [BODY] Summary, Inputs, YAML block (deliverable), Exit Criteria, Machine Data
  
  ├─ #N+7a [agent:task, phase:implement] Task: t1 — Storage abstraction (open, stage: red)
  ├─ #N+7b [agent:task, phase:implement] Task: t2 — Memory store (open, stage: red)
  ├─ #N+7c [agent:task, phase:implement] Task: t3 — Middleware (open, stage: red)
  ├─ #N+7d [agent:task, phase:implement] Task: t4 — Headers (open, stage: red)
  └─ #N+7e [agent:task, phase:implement] Task: t5 — Config (open, stage: red)
```

After all task issues are created and linked:

```bash
gh issue close <taskgraph-issue-number>
```

Gate E is satisfied when task-graph issue is closed and all tasks have `stage: red` and `depends_on` lists.

---

## Phase 8: Implementation Log Recording

### Where the Implementation Log Lives

**Location**: Comments on each implementation task issue (one task issue per vertical slice).

**NOT** in a local `07-implementation-log.md` file. Progress is recorded as comments directly on task issues.

### How to Record Implementation Progress

Phase 8 is resumed in a fresh session with `RESUME=<slug>`. Implementation subagents run each task.

#### Step 1: Load task from GitHub

The implementation subagent reads the task issue from GitHub:

```bash
gh issue view <task-issue-number> --json number,title,body,labels
# Returns task details including current stage: red
```

#### Step 2: RED Stage — Failing Test

The subagent writes a failing test, confirms it fails, then records the result as a **comment on the same task issue**:

```bash
gh issue comment <task-issue-number> --body '
## Slice Update — t1 / red

- **status**: complete
- **files_changed**: src/ratelimit/storage.ts, src/ratelimit/storage.test.ts
- **test_result**: fail (expected)
- **notes**: Test written for storage interface. Test fails: "Storage.get() not implemented"

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: implementation-log
task_id: t1
stage: red
status: complete
updated_at: 2026-04-27T16:00:00Z
```
'
```

Then update the task issue stage field in its Machine Data:

```bash
# Update the issue body to change stage: red in the Machine Data block
gh issue edit <task-issue-number> --body '
[updated body with stage: green in Machine Data]
'
```

#### Step 3: GREEN Stage — Minimal Code

The subagent implements minimal code to make the test pass, then adds another **comment on the same task issue**:

```bash
gh issue comment <task-issue-number> --body '
## Slice Update — t1 / green

- **status**: complete
- **files_changed**: src/ratelimit/storage.ts
- **test_result**: pass
- **notes**: Implemented minimal Storage interface with in-memory get/set. All tests pass.

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: implementation-log
task_id: t1
stage: green
status: complete
updated_at: 2026-04-27T16:05:00Z
```
'
```

Update task issue stage in Machine Data:

```bash
gh issue edit <task-issue-number> --body '
[updated body with stage: refactor in Machine Data]
'
```

#### Step 4: REFACTOR Stage — Polish

The subagent cleans up if needed, reruns tests, then adds a **final comment on the same task issue**:

```bash
gh issue comment <task-issue-number> --body '
## Slice Update — t1 / refactor

- **status**: complete
- **files_changed**: src/ratelimit/storage.ts, src/ratelimit/storage.test.ts
- **test_result**: pass
- **notes**: Added type safety and JSDoc comments. All tests still pass.

## Machine Data

```yaml
work_id: 2026-04-27-add-rate-limiting
kind: implementation-log
task_id: t1
stage: refactor
status: complete
updated_at: 2026-04-27T16:10:00Z
```
'
```

#### Step 5: Close the Task Issue

```bash
gh issue close <task-issue-number>
```

### Task Issue Lifecycle (Complete)

```
#N+7a [agent:task, phase:implement] Task: t1 — Storage abstraction
  status: initially open
  
  • [BODY] Summary, Task Details, Files, Progress Log placeholder, Machine Data
            (Machine Data initially has stage: red)
  
  • [COMMENT 1] RED: Failing test written
                Machine Data: stage: red, status: complete
                
  • [BODY UPDATED] stage changed to: green
  
  • [COMMENT 2] GREEN: Minimal code implementation
                Machine Data: stage: green, status: complete
                
  • [BODY UPDATED] stage changed to: refactor
  
  • [COMMENT 3] REFACTOR: Cleanup and Polish
                Machine Data: stage: refactor, status: complete
  
  → [CLOSED]
```

### Crucial Rule About Implementation Log

From `workflow.md` Phase 8 step 6:

> The task issue comments replace `07-implementation-log.md`, and the issue body remains the durable record of the slice's current/final stage.

**This is critical**: 
- ✅ Progress comments go on the task issue
- ✅ Stage updates go in the task issue's Machine Data block
- ❌ Do NOT create a separate `07-implementation-log.md` file
- ❌ Do NOT create separate RED/GREEN/REFACTOR issue comments in a parent issue

---

## Resume Behavior (Phase 8 Recovery)

When a new session resumes with `RESUME=2026-04-27-add-rate-limiting`:

```bash
# Load parent issue
gh issue view <parent-issue-number> --json number,title,body,id

# Read task-graph issue body for YAML
gh issue view <taskgraph-issue-number> --json number,title,body

# For each task issue, read:
# 1. Current stage from Machine Data in body
# 2. All RED/GREEN/REFACTOR comments
# 3. Which tasks are done (closed) vs. in progress (open)

# Reconstruct full state from GitHub alone
# NO local files needed
```

From `artifact-schema.md`:

> `RESUME=<slug>` must reconstruct state from GitHub alone:
> 1. Find the parent issue or phase issue chain by `work_id`.
> 2. Read closed phase issues for completed artifacts.
> 3. Read open artifact / task issues for remaining work.
> 4. Read approval and implementation-log comments where relevant.
> Do **not** assume `.coding-workflow/work/<slug>/` exists.

---

## Complete Phase 6–8 GitHub Record

After Phase 8 completes, the GitHub issue tree shows:

```
#N   [agent:parent] 2026-04-27-add-rate-limiting
├── #N+1  [phase:intake]           (closed)
├── #N+2  [phase:worktree]         (closed)
├── #N+3  [phase:exploration]      (closed)
├── #N+4  [phase:research]         (closed)
├── #N+5  [phase:clarification]    (closed)
├── #N+6  [phase:plan]             (closed)
│   └── [BODY] Plan content
│   └── [COMMENT] Approval with Machine Data
│       {
│         kind: approval
│         phase: plan
│         status: approved
│         approved_by: human
│         approved_at: ISO8601
│       }
├── #N+7  [phase:task-graph]       (closed)
│   └── [BODY] Task graph YAML (deliverable)
│   └── Machine Data with phase: task-graph
│   ├── #N+7a [agent:task, phase:implement] Task: t1 (closed)
│   │   └── [BODY] Task details + Machine Data (stage: refactor)
│   │   └── [COMMENT 1] RED result
│   │   └── [COMMENT 2] GREEN result
│   │   └── [COMMENT 3] REFACTOR result
│   ├── #N+7b [agent:task] Task: t2 (closed)
│   │   └── (similar comments structure)
│   ├── #N+7c [agent:task] Task: t3 (closed)
│   │   └── (similar comments structure)
│   ├── #N+7d [agent:task] Task: t4 (closed)
│   │   └── (similar comments structure)
│   └── #N+7e [agent:task] Task: t5 (closed)
│       └── (similar comments structure)
```

---

## Key Rules (Non-Negotiable)

From `workflow.md`, `artifact-schema.md`, and `issue-hierarchy.md`:

1. **Phase 6 approval is an explicit comment** — not in the plan body, not in a local file, but a comment on the plan issue with Machine Data
2. **Phase 7 task graph is in the phase issue body** — as a fenced YAML block, not a separate artifact subissue, not a local file
3. **Phase 8 implementation log is task issue comments** — RED/GREEN/REFACTOR comments on each task issue, not a separate log issue, not a local file
4. **Machine Data is structured YAML** — every issue and durable comment includes a `## Machine Data` YAML block
5. **GitHub is canonical** — all state reconstructable from GitHub issues and comments alone; no local files assumed
6. **Task issue body stays durable** — stage field updates in place in the issue's Machine Data block; previous comments remain for history

---

## Comparison: Local Files vs. GitHub-Native

| Artifact | Legacy (Local File) | Current (GitHub-Native) |
|----------|-------------------|------------------------|
| **Phase 6 Plan** | `05-plan.md` | Plan issue body + approval comment |
| **Phase 6 Approval** | Text in `05-plan.md` | Explicit comment on plan issue with Machine Data |
| **Phase 7 Task Graph** | `06-task-graph.yaml` | YAML in task-graph issue body |
| **Phase 8 Impl Log** | `07-implementation-log.md` | Comments on each task issue |
| **RED/GREEN/REFACTOR** | Sections in log file | Individual comments on task issue |
| **Stage tracking** | Text field in log | Machine Data YAML in task issue body |
| **Resumability** | Read local files | Read GitHub issue state |

---

## Conclusion

The GitHub-native flow eliminates local per-work-item files and replaces them with durable GitHub artifacts:

- **Phase 6 approval** → Explicit comment with Machine Data on the plan issue
- **Phase 7 task graph** → YAML fenced block in the task-graph issue body
- **Phase 8 implementation log** → RED/GREEN/REFACTOR comments on task issues (one comment per stage per task)

All progress is recorded in GitHub issues and comments. Resume sessions read state from GitHub alone. No local files after Bootstrap. The complete workflow is auditable and resumable across agents and sessions.
