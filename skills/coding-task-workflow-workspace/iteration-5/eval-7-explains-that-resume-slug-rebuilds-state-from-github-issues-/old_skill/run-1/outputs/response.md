# Evaluation: Resume State Reconstruction and Next Phase Detection

## Test Case

- **Resume command**: `coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs`
- **Context**: No local artifact directory (fresh session on a different agent)
- **Goal**: Understand exactly where resume state comes from and how next phase is determined

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), the resume mechanism is explicitly designed to work without local files.

### Non-Negotiable Rule

From `references/artifact-schema.md` lines 144–151:
> `RESUME=<slug>` must reconstruct state from GitHub alone:
> 1. Find the parent issue or phase issue chain by `work_id`.
> 2. Read closed phase issues for completed artifacts.
> 3. Read open artifact / task issues for remaining work.
> 4. Read approval and implementation-log comments where relevant.
> 
> Do **not** assume `.coding-workflow/work/<slug>/` exists.

### Invocation Routing

From `SKILL.md` lines 64–68:
> Routing precedence:
> 1. `BOOTSTRAP=only`: run only Phase 0.
> 2. `RESUME=<slug>`: rebuild state from the GitHub issue hierarchy for that `work_id` and continue from the next incomplete phase.
> 3. Otherwise start at Phase 1...

### Resume Resolution Mechanism

From `references/workflow.md` Phase 8 line 234:
> Resolve `RESUME=<slug>` by loading the parent issue and descendant phase/task issues for that `work_id`. Do not rely on local phase files.

---

## Where Resume State Comes From: GitHub Only

When `RESUME=2026-04-27-add-rate-limit-logs` is invoked:

### Step 1: Find the Parent Issue by `work_id`

The workflow searches GitHub issues for one matching the slug `2026-04-27-add-rate-limit-logs`. The `work_id` is stored in the `## Machine Data` block of every GitHub issue created by the workflow.

**Search method**: Query all issues in the repository for:
```yaml
## Machine Data
work_id: 2026-04-27-add-rate-limit-logs
kind: parent
```

The parent issue contains:
- `work_id`: `2026-04-27-add-rate-limit-logs`
- `kind`: `parent`
- `current_phase`: (the most recent phase started)
- Issue status: `open` (closed only when PR merges)

**What's stored in parent issue body**:
- Summary of the work item
- Current phase indicator
- Acceptance criteria snapshot
- Checklist of all sub-issues (Phase 1–11)

### Step 2: Load All Descendant Phase Issues

Once the parent issue is found, the workflow fetches all sub-issues (GitHub sub-issue relationship, not just body references):

```
Parent: #42 [agent:parent] [work_id: 2026-04-27-add-rate-limit-logs]
├── Phase 1:  #43 [phase:intake]
├── Phase 2:  #44 [phase:worktree]
├── Phase 3:  #45 [phase:exploration]
│   ├── #46 [artifact] files.csv
│   └── #47 [artifact] open-questions
├── Phase 4:  #48 [phase:research]
│   └── #49 [artifact] sources.md
├── Phase 5:  #50 [phase:clarification]
├── Phase 6:  #51 [phase:plan]
├── Phase 7:  #52 [phase:task-graph]
│   ├── #53 [phase:implement] Task 1
│   ├── #54 [phase:implement] Task 2
│   └── #55 [phase:implement] Task 3
├── Phase 8:  (not yet created if <= Phase 7 was last)
├── Phase 9:  (not yet created)
├── Phase 10: (not yet created)
└── Phase 11: (not yet created)
```

**Which issues to read**:

| Phase | Read | Status | Key fields |
|-------|------|--------|-----------|
| 1 (Intake) | Closed issue body | `closed` | classification, acceptance criteria |
| 2 (Worktree) | Closed issue body | `closed` | branch name, worktree path |
| 3 (Exploration) | Closed issue body | `closed` | key findings, track selected |
| 3 artifacts | Closed issue bodies | `closed` (files.csv) or `open` (open-questions) | files ledger, question ledger |
| 4 (Research) | Closed issue body | `closed` | research findings |
| 4 artifacts | Closed/open issue bodies | `closed` (sources.md) or N/A | sources ledger |
| 5 (Clarification) | Closed or open issue body | `closed` | human answers, assumptions |
| 6 (Plan) | Closed issue body + approval comment | `closed` | approved plan |
| 7 (Task graph) | Closed issue body + task issues | `closed` | YAML task graph, task stage |
| 8+ | Issue state and comments | Open or closed | progress, stage, RED/GREEN/REFACTOR logs |

### Step 3: Determine Issue State (Closed vs Open)

The workflow reads the **GitHub issue state** to determine completion:
- **`state: closed`**: Phase is complete
- **`state: open`**: Phase is in progress or not started
- **Machine Data `status` field**: Can be more granular (e.g., `status: complete`, `status: blocked`)

### Step 4: Read Comments for Approval and Progress

For specific phases, comments provide critical context:

**Phase 6 (Plan) approval comment**:
```yaml
## Machine Data
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```

**Phase 8+ implementation-log comments** (one per RED/GREEN/REFACTOR stage):
```yaml
## Slice Update — task-001 / red
- status: complete | blocked
- files_changed: [...]
- test_result: pass | fail

## Machine Data
kind: implementation-log
task_id: task-001
stage: red | green | refactor
status: complete
```

Task issue `stage` field is updated in the issue body's `## Machine Data` block:
```yaml
stage: red | green | refactor
```

---

## How Next Phase is Determined

Once all GitHub issues are loaded, the workflow determines the next phase by checking **gate conditions** and **issue closure states**.

### Algorithm: Find Next Incomplete Phase

```
For phase in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
  If phase_issue_state == "open" OR phase_not_created:
    Check gate conditions for entering this phase
    If gate conditions are satisfied:
      Return this phase as the next phase to run
    Else:
      Stop and report gate violation (cannot proceed)
```

### Gate Checks (Simplified Examples)

**To proceed to Phase 4 (Research)**:
- ✅ Phase 3 exploration issue is **closed**
- ✅ `files.csv` artifact is **closed**
- ✅ `open-questions` artifact **exists** (may still be open)

**To proceed to Phase 5 (Clarification)**:
- ✅ Phase 4 research issue is **closed**
- ✅ `sources.md` artifact is **closed**
- ✅ `open-questions` artifact has **no questions at `status: open`**

**To proceed to Phase 6 (Plan)**:
- ✅ Phase 5 clarification issue is **closed**
- ✅ `open-questions` artifact is **closed**
- ✅ No entry has `blocking: true` AND `status: unanswered`

**To proceed to Phase 7 (Task Graph)**:
- ✅ Phase 6 plan issue is **closed**
- ✅ Plan issue has **explicit approval comment** with `status: approved`

**To proceed to Phase 8 (Implementation)** — Special case:
- ✅ Phase 7 task-graph issue is **closed**
- ✅ At least one task has `stage: red`
- ✅ Every task has explicit `depends_on` list
- ✅ No circular dependencies in task graph YAML
- ⚠️ **Mandatory session boundary**: Cannot proceed to Phase 8 in the same session where Phase 7 completed
- ✅ Must return: `coding-task-workflow RESUME=<slug>` for a fresh session

### Specific Example: Resume After Phase 7

Given `RESUME=2026-04-27-add-rate-limit-logs`:

1. **Find parent issue** `#42` by `work_id`
2. **Check Phase 7 (Task Graph) issue** `#52`:
   - Status: **closed** ✅
   - Contains: YAML task graph with tasks at `stage: red`
   - Approval: N/A (no human approval needed for task graph)
3. **Check task issues** `#53`, `#54`, `#55`:
   - All initialized with `stage: red`
   - All have `depends_on` lists
4. **Check for session boundary**:
   - Phase 7 is complete and gate conditions satisfied
   - **Session boundary enforced**: Original session must have stopped here
   - New session can now proceed to Phase 8
5. **Determine next phase**: Phase 8 (Implementation)
6. **Load task graph**:
   - Read YAML from `#52` issue body
   - Identify task dependency order
   - Determine which tasks can run in parallel
7. **Resume Phase 8** in the fresh session

---

## Complete State Reconstruction Checklist

When `RESUME=2026-04-27-add-rate-limit-logs` is invoked:

```
[ ] Find parent issue by work_id in Machine Data
[ ] Read parent issue body for summary and current_phase
[ ] Fetch all child phase issues (1–11) linked as sub-issues
[ ] For each completed phase:
    [ ] Read closed issue body for findings/decisions
    [ ] Read artifact subissues (files.csv, open-questions, sources.md, etc.)
[ ] For phase 6 (Plan):
    [ ] Check for approval comment with status: approved
[ ] For phases 8+ (Implementation):
    [ ] Read all task issues by querying parent: #N+7 (task graph issue)
    [ ] For each task, read:
        [ ] Current stage (red | green | refactor)
        [ ] Dependencies (depends_on field in Machine Data)
        [ ] Progress log (RED/GREEN/REFACTOR comments)
[ ] Determine next incomplete phase by checking gate conditions
[ ] If gate conditions not met:
    [ ] Report violation and stop
[ ] Else:
    [ ] Proceed to next phase
```

---

## Why No Local Files?

From **Non-negotiable rule #2** (`SKILL.md`):
> Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.

**Benefits of GitHub-only state**:
1. **No setup required**: New agent can resume without needing worktree or local files
2. **Auditable**: All state is visible in GitHub history
3. **Shareable**: Multiple agents can read and update the same work item
4. **Durable**: State persists after the session ends (unlike environment variables or temp files)
5. **Resilient**: Works across different machines, networks, and time zones

---

## Summary: Resume State Flow

```
[RESUME command]
        ↓
[Search GitHub by work_id]
        ↓
[Find parent issue #42]
        ↓
[Load all sub-issues: phases 1–11]
        ↓
[Read issue states (closed/open)]
        ↓
[Read approval comments (phase 6)]
        ↓
[Read implementation-log comments (phases 8+)]
        ↓
[Check gate conditions]
        ↓
[Determine next incomplete phase]
        ↓
[Proceed to that phase or report gate violation]
```

**Local files are never consulted.** All state comes from GitHub issues, sub-issues, issue bodies, and comments.
