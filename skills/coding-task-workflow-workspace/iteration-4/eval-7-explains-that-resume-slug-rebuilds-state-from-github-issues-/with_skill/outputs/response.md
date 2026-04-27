# Resume State Reconstruction in coding-task-workflow

## Executive Summary

When resuming with `coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs` from a fresh agent session with no local artifact directory, the workflow **rebuilds all state from GitHub issues alone** using the work-item slug (`2026-04-27-add-rate-limit-logs`) as the single source of truth. This design makes the workflow **portable across agents, sessions, and machines** while keeping GitHub as the canonical durable record.

---

## Where Resume State Comes From

### Single Source of Truth: GitHub Issue Hierarchy

The resume slug (e.g., `2026-04-27-add-rate-limit-logs`) identifies a **parent issue** and its entire descendant hierarchy in GitHub. The state is stored in:

1. **Parent issue body** — contains:
   - `work_id: 2026-04-27-add-rate-limit-logs` in the Machine Data YAML block
   - `current_phase` field indicating where work was interrupted
   - `status: open` (still active)
   - `classification: feature | bug | refactor | spec | chore`

2. **Child phase issues** — each labeled with `agent:phase` and `phase:<name>`:
   - Intake (`phase:intake`) — work classification, acceptance criteria
   - Worktree (`phase:worktree`) — git branch, base commit, worktree path
   - Exploration (`phase:exploration`) — files identified, architecture notes
   - Research (`phase:research`) — findings and approved decisions
   - Clarification (`phase:clarification`) — human-answered blocking questions
   - Plan (`phase:plan`) — approved implementation plan with explicit approval comment
   - Task-graph (`phase:task-graph`) — YAML graph of vertical slices
   - Implementation task issues (`phase:implement`) — one per TDD slice with `stage: red|green|refactor`
   - Review (`phase:review`) — code/security/tech-debt findings
   - Verification (`phase:verify`) — test results, acceptance criteria pass/fail
   - PR (`phase:pr`) — pull request metadata

3. **Artifact subissues** under phase issues:
   - `files.csv` under exploration — full file manifest
   - `open-questions` under exploration — research questions with status
   - `sources.md` under research — URLs and research evidence

4. **Task issue comments** (not separate files):
   - RED / GREEN / REFACTOR implementation progress
   - Each comment contains a `## Machine Data` YAML block with `stage` and timestamp

### Why Not Local Files?

The skill **deliberately avoids local per-work-item directories** after Bootstrap. From workflow.md rule #2:

> Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.

This design choice enables:
- **Multi-agent resumption**: fresh agent with no local state can pull full context from GitHub
- **Portable across worktrees**: different machines, branches, or repositories
- **Atomic cross-session handoffs**: Phase 7→Phase 8 boundary is a clean resume point
- **Audit trail**: every decision is in GitHub with timestamps and approvers

---

## How Resume Detects the Next Phase

### Resume Routing (from SKILL.md)

When invoked with `RESUME=2026-04-27-add-rate-limit-logs`, the workflow follows this precedence:

```
RESUME=<slug>: rebuild state from the GitHub issue hierarchy for that work_id 
               and continue from the next incomplete phase.
```

### Phase Completion Detection

The agent **determines the last completed phase** by inspecting GitHub issue state:

| Phase | Completion Signal | What to Check |
|-------|-------------------|---------------|
| 1 Intake | Issue closed (`state: closed`) | Intake issue `phase:intake` is closed |
| 2 Worktree | Issue closed | Worktree issue `phase:worktree` is closed |
| 3 Exploration | Issues closed + Gate A satisfied | Exploration issue closed, `files.csv` closed, `open-questions` exists |
| 4 Research | Issues closed + Gate B satisfied | Research issue closed, `sources.md` closed, `open-questions` has no open questions |
| 5 Clarification | Issue closed + Gate C satisfied | Clarification issue closed, `open-questions` closed, no blocking unanswered questions |
| 6 Plan | Issue closed + Gate D satisfied | Plan issue closed AND contains an explicit approval comment |
| 7 Task-graph | Issue closed + Gate E satisfied | Task-graph issue closed, implementation task issues created with `stage: red`, dependencies recorded |
| 8 Implementation | All task issues closed | Comments show RED/GREEN/REFACTOR for all tasks |
| 9 Review | Issue closed | Review issue `phase:review` is closed |
| 10 Verification | Issue closed + Gate F satisfied | Verification issue closed, all acceptance criteria marked `pass` |
| 11 Commit/PR | Issue closed | PR issue `phase:pr` is closed |

### Concrete Example: Resume from Phase 8

If `RESUME=2026-04-27-add-rate-limit-logs` and the GitHub issue tree shows:

```
Parent issue #42 [agent:parent] — current_phase: implement
  ✓ #43 [phase:intake] — CLOSED
  ✓ #44 [phase:worktree] — CLOSED
  ✓ #45 [phase:exploration] — CLOSED
    ✓ #45a [artifact] files.csv — CLOSED
    ○ #45b [artifact] open-questions — CLOSED
  ✓ #46 [phase:research] — CLOSED
    ✓ #46a [artifact] sources.md — CLOSED
  ✓ #47 [phase:clarification] — CLOSED
  ✓ #48 [phase:plan] — CLOSED (with approval comment)
  ✓ #49 [phase:task-graph] — CLOSED
    ○ #50 [phase:implement] stage: green — OPEN (rate-limit-config)
    ○ #51 [phase:implement] stage: red — OPEN (rate-limit-header)
    ○ #52 [phase:implement] stage: red — OPEN (rate-limit-retry)
  (No review/verify/pr issues yet)
```

**Resume logic:**
1. Fetch parent issue #42 → read `work_id: 2026-04-27-add-rate-limit-logs`
2. Scan child issues → find all open `phase:implement` task issues
3. Read each task issue body → extract `stage: red|green|refactor`, `depends_on`, `task_id`
4. Read task issue comments → find most recent `## Slice Update` to resume from `stage: green` or `stage: red` as needed
5. **Result**: "Gates A through E satisfied. Phase 8 implementation is in progress. Continue from GREEN task #50."

---

## Decision Logic for Next Phase

From workflow.md, Phase 8 step 1:

> Resolve `RESUME=<slug>` by loading the parent issue and descendant phase/task issues for that `work_id`. Do not rely on local phase files.

The agent then:

1. **Queries GitHub** with the parent issue work_id
   - Run: `gh issue view <issue-number> --json number,title,body,url,id`
   - Extract `work_id` from Machine Data YAML
   - Fetch all child issues and read their closure state + `current_phase` field

2. **Evaluates every gate in order** (A through F):
   - Gate A? If exploration issue is closed and `files.csv` closed → ✓ Gate A satisfied
   - Gate B? If research issue closed and `sources.md` closed and no open questions → ✓ Gate B satisfied
   - Gate C? If clarification issue closed and `open-questions` closed → ✓ Gate C satisfied
   - Gate D? If plan issue closed AND contains approval comment → ✓ Gate D satisfied
   - Gate E? If task-graph issue closed and task issues exist with `stage: red` → ✓ Gate E satisfied
   - Gate F? If verification issue closed and all acceptance criteria marked `pass` → ✓ Gate F satisfied

3. **Identifies the first incomplete gate**:
   - Example: If Gate D is not satisfied (plan issue is still open or has no approval) → **next phase is 6 (Plan)**
   - Example: If Gate E is satisfied but no review issue exists → **next phase is 9 (Review)**

4. **Reads contextual state for the resuming phase**:
   - For Phase 8: Read all open task issues, their current `stage`, and their dependencies
   - For Phase 9: Read which files have changed (inferred from closed task issues)
   - For Phase 10: Read acceptance criteria from intake issue, verification commands from bootstrap overrides

---

## No Local Artifacts = No Problem

Key architectural decisions that make portability work:

### 1. Bootstrap Overrides Are Optional Context
The `.coding-workflow/overrides/` files (if they exist) are **read-only hints** used to improve phase execution, but they are not required:
- If `test-commands.yaml` exists → use it in Phase 10 verification
- If it doesn't exist → infer commands from repo signals or ask the human
- If overrides are stale (>30 days) → Phase 0 can be run to refresh them, but resuming works without them

### 2. All Phase Inputs Come from GitHub Issues
Example: Phase 8 implementation needs:
- Acceptance criteria? → Read from intake issue (`phase:intake`)
- Approved plan? → Read from plan issue (`phase:plan`) + its approval comment
- Task graph? → Read YAML from task-graph issue (`phase:task-graph`)
- Current task progress? → Read task issue `stage` field and latest comment
- Which files to modify? → Read from task issue `files` array in Machine Data

No local `07-implementation-log.md` or `.coding-workflow/work/<slug>/task-graph.yaml` needed.

### 3. Deterministic Slug Makes GitHub Queries Reliable
The slug format `YYYY-MM-DD-<kebab-title>` (max 50 chars) is:
- **Deterministic** — same work item always produces same slug
- **Queryable** — can search GitHub issues by `work_id: 2026-04-27-add-rate-limit-logs` in body
- **Globally unique** within a repository (ensured by date prefix + kebab title)

Workflow recovers parent issue with:
```bash
gh issue list --search "work_id: 2026-04-27-add-rate-limit-logs in:body" --state all
```

---

## Practical Resume Example

### Session 1 (Agent A, initial session):
```
$ Use coding-task-workflow skill.
$ WORK_ITEM: Add rate-limit logging to HTTP client
```
Agent A runs Phases 1–7, creates GitHub issues, passes Gate E, outputs:
```
Gate E satisfied. Hard stop after Phase 7.
Resume from a fresh session with:
  coding-task-workflow RESUME=2026-04-27-add-rate-limit-logs
Phase 8 is the next phase after the resume.
```

GitHub now has issues:
- #100 [agent:parent] Add rate-limit logging
  - #101 [phase:intake]
  - #102 [phase:worktree]
  - ...
  - #109 [phase:task-graph]
    - #110–112 [phase:implement] tasks

### Session 2 (Agent B, different machine, no local state):
```
$ Use coding-task-workflow skill.
$ RESUME=2026-04-27-add-rate-limit-logs
```

Agent B:
1. Parses `RESUME=` slug
2. Queries GitHub: "find parent issue with `work_id: 2026-04-27-add-rate-limit-logs`"
3. Finds parent #100
4. Fetches #100 and all children
5. Evaluates gates → all A–E satisfied
6. Checks if task issues (#110–112) are closed → NO, they are still open
7. **Decision**: "Gate E satisfied, implementation tasks exist, no review yet → **Start Phase 8**"
8. Reads task issues, finds:
   - Task #110 (config): `stage: red`
   - Task #111 (header): `stage: red`
   - Task #112 (retry): `stage: red` and `depends_on: [config]`
9. Executes implementation workflow starting with Task #110

---

## Resume State Integrity Guarantees

### Machine Data YAML Blocks
Every GitHub issue/comment has a `## Machine Data` section that Agent B can parse to validate state:

**Parent issue Machine Data:**
```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: parent
classification: feature
status: open
current_phase: task-graph
```

**Task issue Machine Data:**
```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: task
task_id: config
stage: red
depends_on: []
files: [src/http_client.py, tests/test_rate_limit.py]
```

**Implementation progress comment Machine Data:**
```yaml
work_id: 2026-04-27-add-rate-limit-logs
kind: implementation-log
task_id: config
stage: green
status: complete
updated_at: 2026-04-27T14:23:00Z
```

Agent B validates:
- ✓ work_id matches RESUME slug
- ✓ Kind matches expected phase
- ✓ No circular task dependencies
- ✓ Stage progression is RED → GREEN → REFACTOR

---

## Summary: Resume Decision Flow

```
┌─────────────────────────────────────────────────────┐
│ RESUME=2026-04-27-add-rate-limit-logs               │
│ (slug identifies parent issue)                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Query GitHub: find parent issue by work_id          │
│ Response: #100 [agent:parent]                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Fetch parent + all child issues                     │
│ Check closure state of each phase issue             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Evaluate gates A through F in order:                │
│ - Gate A satisfied? ✓ exploration closed            │
│ - Gate B satisfied? ✓ research closed               │
│ - Gate C satisfied? ✓ clarification closed          │
│ - Gate D satisfied? ✓ plan closed + approved        │
│ - Gate E satisfied? ✓ task-graph closed             │
│ - Gate F satisfied? ✗ verification issue missing    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ First incomplete gate is F (no verification)        │
│ Work backward: if E complete but no review → Phase 9
│ if E complete but no task issues → Phase 8         │
│ Result: Phase 8 tasks exist and are still OPEN     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ **NEXT PHASE: 8 (Implementation)**                  │
│                                                     │
│ Read context from GitHub:                          │
│ - Acceptance criteria from #101 (intake)            │
│ - Plan from #108 (plan)                             │
│ - Task list + stages from #110–#112                 │
│ - Skip Bootstrap overrides (not required)           │
└─────────────────────────────────────────────────────┘
```

**Conclusion**: The resume slug acts as a **content-addressable pointer to the entire work-item history in GitHub**. No local state is needed; all decisions are derived by inspecting issue closure state, phase labels, and Machine Data YAML blocks. This design makes the workflow portable, auditable, and resilient to agent restart.
