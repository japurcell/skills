# GitHub-Native Workflow: Phase 6, 7, and 8 Artifact Storage

## Overview

The `coding-task-workflow` skill has migrated away from file-based phase artifacts (`05-plan.md`, `06-task-graph.yaml`, `07-implementation-log.md`) to a **GitHub-native** workflow. All Phase 6, 7, and 8 artifacts are now stored directly in GitHub issues and comments as part of the durable workflow record. This follows the core principle: "Phase 0 writes repo-local override files; Phases 1–11 use GitHub issues and comments as the canonical durable workflow record."

---

## Phase 6: Plan — Approval Recording

### Artifact Location

**GitHub child issue body + explicit comment**

- **Issue Label:** `agent:phase` and `phase:plan`
- **Issue Body:** Contains the implementation plan using the `references/templates/plan.md` template structure:
  - Goal and Non-Goals
  - Approach and Rationale
  - Alternatives Considered
  - File-by-File Implementation Map
  - Verification Guidance
- **Approval Recording:** An explicit comment on the plan issue
- **Status After Approval:** The plan issue is immediately closed after the approval comment is recorded

### Workflow Steps (Phase 6, Steps 4–6)

1. Present a concise plan summary to the human
2. Gate on **explicit approval**
3. **Record approval as an explicit comment on the plan issue** (this is now the authoritative approval record)
4. Close the plan issue immediately after approval
5. If the human requests changes, edit the issue body and repeat the approval step

### Why This Works

- **Immutable History**: The comment is time-stamped and cannot be edited (or edits are tracked), making it a durable approval record
- **Linked Context**: The comment lives on the same issue as the plan, keeping approval and plan together
- **Resume-Friendly**: When resuming from `RESUME=<slug>`, the workflow reads the GitHub issue hierarchy and immediately sees that Gate D is satisfied by the closed plan issue with an approval comment
- **No Local Files**: Eliminates the need to hunt for `05-plan.md` on disk or risk it being stale

### Gate D Checkpoint

**Gate D passes when:**
- The plan issue is closed
- **The plan issue contains an explicit approval comment**
- Before Phase 7 begins

---

## Phase 7: TDD Task Graph — YAML Storage in Issue Body

### Artifact Location

**GitHub child issue body (task-graph phase issue)**

- **Issue Label:** `agent:phase` and `phase:task-graph`
- **Issue Body:** Contains the task graph in a **fenced YAML block** (not a separate file)
- **YAML Template:** Based on `references/templates/task-graph.yaml`
- **Status After Creation:** The task-graph issue is closed once the YAML and all implementation task issues are created

### Task Graph YAML Structure

The YAML is embedded directly in the Phase 7 issue body:

```yaml
work_id: WORK_ID
phase: task-graph
status: complete
updated_at: "ISO8601_TIMESTAMP"

tasks:
  - id: t1
    name: "BEHAVIOUR_1 vertical slice"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/example/feature.test.ts
      - src/example/feature.ts
  
  - id: t2
    name: "BEHAVIOUR_2 vertical slice"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/example/feature.test.ts
      - src/example/feature.ts
```

### Workflow Steps (Phase 7, Steps 3–6)

1. Identify distinct behaviours and create a task DAG
2. Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`
3. **Put the task graph in a fenced YAML block** inside the issue body
4. Create one GitHub child issue **per vertical slice**:
   - Label: `agent:task`, `phase:implement`, plus `parallel` or `sequential`
   - Initialize each with `stage: red`
   - Each task issue becomes the durable record for one vertical TDD slice
5. Close the task-graph issue once the YAML and task issues are complete
6. **After Gate E is satisfied, stop and hand off**: `coding-task-workflow RESUME=<slug>`. Do not proceed to Phase 8 in the same invocation.

### Implementation Task Issues (Child of Task-Graph Issue)

- **One issue per vertical slice** (one per task ID in the YAML)
- **Labels:** `agent:task`, `phase:implement`, plus `parallel` or `sequential`
- **Body:** Describes the slice behaviour and expected outcome
- **Progress Tracking:** Initial stage is `stage: red`; RED, GREEN, and REFACTOR progress stays as comments on this same issue (no separate sub-issues for each stage)
- **Lifecycle:** Open at end of Phase 7; closed in Phase 8 when the vertical slice is complete

### Why This Works

- **YAML in GitHub**: The task graph is part of the authoritative issue body, eliminating the need for a separate `06-task-graph.yaml` file
- **Single Source of Truth**: Resuming from GitHub means you always have the current task structure without file sync issues
- **Decoupled Storage**: The YAML lives in the phase issue; each implementation task issue is independent and can be worked on in parallel or sequentially
- **Resume-Friendly**: `coding-task-workflow RESUME=<slug>` reconstructs the full task graph and implementation task list from GitHub alone

### Gate E Checkpoint

**Gate E passes when:**
- The task-graph issue is closed
- At least one implementation task issue has `stage: red`
- Every task issue records an explicit dependency list
- Before Phase 8 begins (in a fresh, resumed session)

---

## Phase 8: Implementation — Progress as Issue Comments

### Artifact Location

**GitHub implementation task issue comments (one per task)**

- **Parent Issues:** Each task issue is a child of the Phase 7 task-graph issue
- **Progress Recording:** RED, GREEN, and REFACTOR stages are recorded as **comments on the same task issue**, not in a separate log file
- **Status Field:** The task issue body records the current `stage: red | green | refactor`

### Workflow Steps (Phase 8, Steps 3–4)

For each implementation task issue:

1. **RED Stage:**
   - Write a failing test that captures the behaviour
   - Run it and confirm it fails for the expected reason
   - **Record the result as a comment on the task issue** while the issue remains at `stage: red`
   - Comments include: test name, failure output, expected failure reason

2. **GREEN Stage:**
   - Update the task issue body to `stage: green`
   - Write minimal code to make the test pass
   - Run the test
   - **Record the result as a comment on the same task issue**
   - Comments include: code changes summary, test output showing pass

3. **REFACTOR Stage:**
   - Update the task issue body to `stage: refactor`
   - Clean up if needed
   - Rerun relevant tests
   - **Record the outcome as another comment on the same task issue**
   - Comments include: refactoring changes, test output

4. Close the task issue when the slice is complete

### Example Task Issue Comment Flow

**Task Issue: `#42 - User authentication vertical slice`**

```
Issue Body (updated at each stage):
stage: red | green | refactor

Comments (cumulative record):
1. @agent: RED STAGE COMPLETE
   Test: test_login_with_valid_credentials
   Status: FAIL (expected)
   
2. @agent: GREEN STAGE COMPLETE
   Code changes: added loginUser() in auth.ts
   Status: PASS ✓
   
3. @agent: REFACTOR STAGE COMPLETE
   Changes: extracted password validation, improved error handling
   Status: PASS ✓
   All tests passing
```

### Why This Works

- **No Separate Log File**: Implementation progress is recorded as comments on the task issue, eliminating the need for `07-implementation-log.md`
- **Issue = Vertical Slice Owner**: The task issue is the durable, time-stamped record of one behaviour from RED to GREEN to REFACTOR
- **Linked to Phase 7**: The task issue is a child of the task-graph issue, maintaining the full hierarchy
- **Resume-Friendly**: Resuming from `RESUME=<slug>` reads the task issue comments to understand what's been done, what stage each task is at, and any blockers
- **Parallelism Support**: Multiple task issues can be worked on concurrently; each maintains its own comment history

### Strict TDD Rules

- Never add untested code paths
- If a useful branch is not covered by a test, do not add it
- Each comment documents RED/GREEN/REFACTOR progress with test results and evidence

### Phase 8 Outputs

- Modified source files and tests (in the worktree)
- **Implementation task issue comments** (durable record of work)
- Updated task issue stage fields
- Closed implementation task issues (once the vertical slice is complete)

---

## GitHub Issue Hierarchy Summary

```
Parent Issue (#N)
├── Phase 1: Intake Issue (phase:intake) [CLOSED]
├── Phase 2: Worktree Issue (phase:worktree) [CLOSED]
├── Phase 3: Exploration Issue (phase:exploration) [CLOSED]
│   ├── Artifact: files.csv (artifact:) [CLOSED]
│   └── Artifact: open-questions (artifact:) [CLOSED]
├── Phase 4: Research Issue (phase:research) [CLOSED]
│   └── Artifact: sources.md (artifact:) [CLOSED]
├── Phase 5: Clarification Issue (phase:clarification) [CLOSED]
├── Phase 6: Plan Issue (phase:plan) [CLOSED]
│   └── Comment: "Approved by human" ← EXPLICIT APPROVAL RECORD
├── Phase 7: Task-Graph Issue (phase:task-graph) [CLOSED]
│   ├── YAML: task graph in issue body
│   ├── Task #1: "User auth vertical slice" (agent:task, phase:implement) [OPEN → CLOSED]
│   │   └── Comments: RED result, GREEN result, REFACTOR result
│   ├── Task #2: "Email validation vertical slice" (agent:task, phase:implement) [OPEN → CLOSED]
│   │   └── Comments: RED result, GREEN result, REFACTOR result
│   └── Task #3: "Error handling vertical slice" (agent:task, phase:implement) [OPEN → CLOSED]
│       └── Comments: RED result, GREEN result, REFACTOR result
├── Phase 8: (no separate phase issue)
│   └── Task issues updated with stage and comments as work progresses
├── Phase 9: Review Issue (phase:review) [CLOSED]
├── Phase 10: Verification Issue (phase:verify) [CLOSED]
└── Phase 11: PR Issue (phase:pr) [CLOSED]
    └── Pull Request Reference and commit link
```

---

## Key Design Principles for GitHub-Native Workflow

### 1. No Local Per-Phase Files

- **Phase 6 (Plan):** No `05-plan.md` file. Plan lives in the GitHub issue body.
- **Phase 7 (Task Graph):** No `06-task-graph.yaml` file. Task graph YAML is embedded in the GitHub issue body.
- **Phase 8 (Implementation):** No `07-implementation-log.md` file. Progress is recorded as issue comments.

### 2. GitHub as Single Source of Truth

- Resume from `RESUME=<slug>` by fetching the parent issue and all descendant phase/task issues
- The GitHub hierarchy contains all durable workflow state
- No need to hunt for local files or worry about sync issues

### 3. Explicit Approval Comments

- Gate D approval is an explicit comment (not an edit to the plan body)
- Time-stamped, immutable, and linked to the plan
- Makes the approval moment crystal clear when reading the issue history

### 4. Task Issues as Vertical Slice Owners

- One task issue per TDD vertical slice
- Each task issue accumulates RED/GREEN/REFACTOR comments
- No separate sub-issues for each stage
- Parallelizable tasks have independent issue comment threads

### 5. Issue Comments for Work Progress

- RED, GREEN, REFACTOR results are comments, not separate files
- Comments are time-stamped and immutable
- Multiple agents can comment simultaneously on independent task issues

---

## Migration Path

If you have existing work from the old file-based workflow (`05-plan.md`, `06-task-graph.yaml`, `07-implementation-log.md`):

1. **Phase 6 Plan Migration:**
   - Copy the content from `05-plan.md` into the Phase 6 plan issue body
   - Record the approval as an explicit comment
   - Close the plan issue
   - Delete the local `05-plan.md` file

2. **Phase 7 Task Graph Migration:**
   - Extract the YAML from `06-task-graph.yaml`
   - Paste it as a fenced YAML block into the Phase 7 task-graph issue body
   - Create implementation task issues for each task in the YAML
   - Close the task-graph issue
   - Delete the local `06-task-graph.yaml` file

3. **Phase 8 Implementation Migration:**
   - Migrate existing implementation log entries from `07-implementation-log.md` into comments on the corresponding task issues
   - Update task issue stage fields
   - Continue with Phase 8 from the fresh resumed session
   - Delete the local `07-implementation-log.md` file

---

## Summary

| Phase | Previous Storage | GitHub-Native Storage | Approval/Closure |
|-------|------------------|----------------------|-----------------|
| **6: Plan** | `05-plan.md` file | GitHub issue body + explicit approval comment | Plan issue closed after approval comment recorded |
| **7: Task Graph** | `06-task-graph.yaml` file | Fenced YAML block in GitHub issue body | Task-graph issue closed after YAML and task issues created |
| **8: Implementation** | `07-implementation-log.md` file | Comments on implementation task issues | Task issues closed after all stages complete |

The GitHub-native workflow **eliminates file synchronization issues, makes resumption seamless, and provides an immutable, time-stamped record of every decision and action**.
