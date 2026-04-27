# Resume State Reconstruction and Workflow Decision Logic

## Executive Summary

When resuming a `coding-task-workflow` work item using `RESUME=2026-04-27-add-rate-limit-logs` **without a local artifact directory**, the agent:

1. **Rebuilds state entirely from GitHub**, using the work-item slug to locate the parent issue and descendant phase/task issues
2. **Determines the last completed phase** by examining issue closure state, GitHub labels, and approval/implementation-log comments
3. **Resumes from the next incomplete phase** according to the gate-driven workflow sequence

This ensures work is resumable and auditable across agents and sessions, **regardless of local artifact availability**.

---

## Where Resume State Comes From

### GitHub Issue Hierarchy

The `RESUME=<slug>` command uses the slug (`work_id`) to navigate a parent-issue/sub-issue hierarchy in GitHub:

```
Parent issue #N  [label: agent:parent]  Feature/bug/spec description
  ├─ Sub-issue #N+1 [label: phase:intake]         Intake artifact
  ├─ Sub-issue #N+2 [label: phase:worktree]       Worktree metadata
  ├─ Sub-issue #N+3 [label: phase:exploration]    Exploration summary
  │   ├─ Sub-issue: files.csv                     [artifact]
  │   └─ Sub-issue: open-questions                [artifact]
  ├─ Sub-issue #N+4 [label: phase:research]       Research findings
  │   └─ Sub-issue: sources.md                    [artifact]
  ├─ Sub-issue #N+5 [label: phase:clarification]  Human answers
  ├─ Sub-issue #N+6 [label: phase:plan]           Implementation plan
  ├─ Sub-issue #N+7 [label: phase:task-graph]     Task DAG (YAML)
  │   ├─ Sub-issue: task-slice-1                  [agent:task, phase:implement]
  │   └─ Sub-issue: task-slice-2                  [agent:task, phase:implement]
  ├─ Sub-issue #N+8 [label: phase:review]         Code/security/tech-debt review
  ├─ Sub-issue #N+9 [label: phase:verify]         Verification results
  └─ Sub-issue #N+10 [label: phase:pr]            PR metadata
```

### Key Machine Data Fields

Every GitHub artifact includes a `## Machine Data` YAML section with fields like:

```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: phase | task | approval | implementation-log
phase: intake | worktree | exploration | ... | pr
status: open | closed
stage: red | green | refactor  # For implementation tasks
depends_on: [<task-ids>]
```

These fields allow deterministic phase detection without relying on local files.

---

## How Resume Rebuilds State (Step by Step)

When an agent runs `RESUME=2026-04-27-add-rate-limit-logs`:

### Step 1: Locate the Parent Issue

```bash
gh issue list --search "work_id: 2026-04-27-add-rate-limit-logs"
# or
gh issue view <ISSUE> --json number,title,body,url,id
```

The parent issue body contains:
- `## Summary` — lightweight work-item description
- `## Current Phase` — the last recorded phase number
- `## Acceptance Snapshot` — acceptance criteria (for verification later)
- `## Machine Data` with:
  ```yaml
  work_id: 2026-04-27-add-rate-limit-logs
  kind: parent
  status: open
  classification: feature | bug | refactor | spec | chore
  ```

### Step 2: Fetch All Phase and Task Issues

Query GitHub for all child issues with labels matching the work_id:

```bash
gh issue list --search "parent:<PARENT_ISSUE_NUMBER>" --label "agent:phase" --json number,title,body,state,labels
```

Returns all phase issues (intake, worktree, exploration, research, clarification, plan, task-graph, implement, review, verify, pr).

### Step 3: Read the Machine Data from Each Phase Issue

For each phase issue, parse the `## Machine Data` block to determine:

| Phase | Detection Logic | Completeness Marker |
|-------|-----------------|----------------------|
| Phase 1 (Intake) | `label: phase:intake` exists | Issue is **closed** |
| Phase 2 (Worktree) | `label: phase:worktree` exists | Issue is **closed** |
| Phase 3 (Exploration) | `label: phase:exploration` exists | Issue is **closed** + `files.csv` artifact is closed |
| Phase 4 (Research) | `label: phase:research` exists | Issue is **closed** + `sources.md` artifact is closed |
| Phase 5 (Clarification) | `label: phase:clarification` exists | Issue is **closed** + `open-questions` artifact is **closed** |
| Phase 6 (Plan) | `label: phase:plan` exists | Issue is **closed** + contains approval comment |
| Phase 7 (Task Graph) | `label: phase:task-graph` exists | Issue is **closed** + at least one task issue exists |
| Phase 8 (Implementation) | `label: phase:implement` on task issues | All task issues have `stage: complete` or are still incomplete |
| Phase 9 (Review) | `label: phase:review` exists | Issue is **closed** |
| Phase 10 (Verification) | `label: phase:verify` exists | Issue is **closed** |
| Phase 11 (Commit/PR) | `label: phase:pr` exists | Issue is **closed** + PR number is recorded |

### Step 4: Determine the Last Completed Phase

The agent walks through phases 1–11 and stops at the first **incomplete** phase:

1. Check **parent issue body** for `## Current Phase` field (may be stale, but gives a hint)
2. For each phase in sequence (1 → 11):
   - Query for the phase issue by label
   - Check if the phase issue exists
   - Check if the phase issue is **closed**
   - Check gate-specific conditions (approval comment for Plan, closed artifacts for Exploration/Research/Clarification)
3. **Stop at the first incomplete phase** — this is the resume target

**Example logic:**

```python
def find_next_incomplete_phase(parent_issue, work_id):
    phase_issues = query_github(
        search=f"parent:{parent_issue} label:agent:phase",
        sort="closed_at",
        order="asc"
    )
    
    for phase_num in range(1, 12):
        phase_issue = find_by_phase_num(phase_issues, phase_num)
        
        if not phase_issue:
            # Phase hasn't been started yet
            return phase_num
        
        if phase_issue.state == 'open':
            # Phase was started but not completed
            return phase_num
        
        # Check gate-specific conditions
        if phase_num == 6:  # Plan needs approval comment
            if not has_approval_comment(phase_issue):
                return 6
        elif phase_num == 3:  # Exploration needs closed artifacts
            if not is_artifact_closed(phase_issue, 'files.csv'):
                return 3
        
        # Phase is complete; continue
    
    return 12  # All phases complete
```

---

## How the Workflow Decides the Next Phase

### Gate-Driven Sequencing

The workflow is strictly gate-driven. Each phase has explicit **entry and exit gates** defined in `stop-gates.md`:

| Phase | Gate | Conditions for Entry |
|-------|------|-----------------------|
| Phase 1 | — | Always runs (Phase 0 if overrides missing) |
| Phase 2 | — | Phase 1 complete |
| Phase 3 | A | Phase 2 complete |
| Phase 4 | B | Phase 3 complete, exploration closed, files.csv closed, open-questions exists |
| Phase 5 | C | Phase 4 complete, research closed, no `open` questions remain |
| Phase 6 | D | Phase 5 complete, clarification closed |
| Phase 7 | E | Phase 6 complete, plan closed with approval comment |
| **8–11** | — | **Hard stop after Phase 7; must resume in new session** |

### Resume Decision Logic

When resuming, the agent:

1. **Query GitHub for parent issue** by matching `work_id` in Machine Data blocks
2. **Enumerate all child phase/task issues**
3. **Check each phase's completion state:**
   - Closed issue + gate conditions satisfied = **completed phase**
   - Open issue or gate conditions missing = **next phase to resume**
4. **Jump directly to the next incomplete phase** — do NOT restart earlier phases unless their GitHub artifacts indicate incompleteness

**Example resume scenarios:**

#### Scenario A: Phase 7 task graph is complete, resuming for Phase 8
```
Parent issue state:
  - Intake: closed ✓
  - Worktree: closed ✓
  - Exploration: closed ✓, files.csv closed ✓
  - Research: closed ✓, sources.md closed ✓
  - Clarification: closed ✓
  - Plan: closed ✓, approval comment exists ✓
  - Task-graph: closed ✓, task issues exist ✓

→ Resume from Phase 8 (Implementation)
  - Fetch task-graph issue for the task DAG
  - Fetch open task issues for implementation status
  - Start executing the first incomplete task
```

#### Scenario B: Phase 6 Plan is complete but approval is missing
```
Parent issue state:
  - Plan issue exists and is closed
  - But: NO approval comment found

→ Resume from Phase 6 (Plan)
  - Re-read the plan issue body
  - Ask human for approval (even though issue is closed)
  - Add approval comment
  - Close plan issue
  - Proceed to Phase 7
```

#### Scenario C: Phase 8 Implementation is in progress
```
Parent issue state:
  - Task-graph: closed ✓
  - Task #1: open, stage=red
  - Task #2: open, stage=red
  - Task #3: does not exist yet

→ Resume from Phase 8 (Implementation)
  - Task #1 is at `stage: red` — continue working on it
  - RED has a comment with test result
  - Next step: run GREEN (write minimal code)
```

---

## No Local Artifact Directory Required

### What the Agent Does NOT Need

- `~/.coding-workflow/work/<slug>/` directory
- Local `.coding-workflow/work/<slug>/{01-intake,02-worktree,...}.md` files
- Any persistent cache of phase state

### What the Agent DOES Need

1. **GitHub API access** — to query issues and read issue bodies
2. **The work_id slug** — to find the parent issue in GitHub
3. **gh CLI** or equivalent GitHub GraphQL client
4. **read-only GitHub issue hierarchy** — the state is immutable, stored in issues and comments

### Resilience Properties

Because state lives in GitHub, resumable work is:

- **Portable**: Different agents, machines, contexts can resume the same work
- **Durable**: State survives session crashes, network failures, local disk loss
- **Auditable**: Full issue history and comments show all decisions and changes
- **Concurrent-safe**: GitHub issues provide atomic updates (labels, state, comments)

---

## Phase Decision Examples

### Example: Resume after Phase 7

```
Input: RESUME=2026-04-27-add-rate-limit-logs

1. Query GitHub: find parent issue with work_id=2026-04-27-add-rate-limit-logs
   → Issue #42

2. Fetch all child issues of #42:
   - #43 phase:intake (closed) ✓
   - #44 phase:worktree (closed) ✓
   - #45 phase:exploration (closed) ✓
     - #45a artifact files.csv (closed) ✓
     - #45b artifact open-questions (closed) ✓
   - #46 phase:research (closed) ✓
     - #46a artifact sources.md (closed) ✓
   - #47 phase:clarification (closed) ✓
   - #48 phase:plan (closed, has approval comment) ✓
   - #49 phase:task-graph (closed) ✓
     - #49a agent:task implement-logs (open, stage=red) ← INCOMPLETE
     - #49b agent:task implement-logs (open, stage=red) ← INCOMPLETE

3. Determine next phase: Phase 8 (Implementation)
   Reason: Task-graph is closed but task issues are open at stage=red

4. Action: Resume Phase 8
   - Read task-graph YAML from #49 body
   - Process task #49a and #49b in order
   - Start writing RED tests
```

### Example: Resume during Phase 8

```
Input: RESUME=2026-04-27-add-rate-limit-logs

1-2. (Same as above)

3. Phase status scan:
   - #49a agent:task (open)
     - Comments show: RED test written, FAILED as expected
     - stage field: currently "red"
     - Recent comment: GREEN phase started, test PASSED, code written
     - stage field in recent comment: "green"
   
   - #49b agent:task (open)
     - Comments show: RED test written, FAILED as expected
     - stage field: currently "red"

4. Determine next phase: Phase 8 (Implementation)
   Task #49a is at stage=green (in progress)
   Task #49b is at stage=red (waiting)

5. Action: Resume Phase 8
   - Fetch task #49a, read GREEN comment
   - Next step: REFACTOR and close the task
   - Then move to task #49b, write RED tests
```

---

## Summary: The Resume Flow

```
RESUME=<slug>
    ↓
GitHub: Find parent issue with work_id=<slug>
    ↓
GitHub: Fetch all child phase/task issues by label
    ↓
Walk phases 1→11:
  For each phase:
    - Does the phase issue exist?
    - Is the phase issue closed?
    - Are gate conditions satisfied? (approval, artifact closure, etc.)
    - If any check fails → STOP, this is the next phase
    ↓
Execute the next incomplete phase
  - For Phase 8: read task-graph, execute tasks in dependency order
  - For other phases: follow the standard workflow
  - Update issue state, labels, and add comments
    ↓
After each phase: Check if gate is satisfied
  - If gate satisfied: proceed to next phase
  - If gate not satisfied: loop or wait for human
    ↓
After Phase 7: Hard stop, resume from fresh session
```

---

## Key Insight

The `RESUME=<slug>` command is **not** an optimization for local artifacts; it is the **primary durability mechanism** of the workflow. All state lives in GitHub from Phase 1 onward. Local files (`.coding-workflow/overrides/` in Phase 0) are repo-local bootstrap only. Once Phase 1 starts, GitHub issues become the source of truth, making work resumable across any agent, any machine, any time.
