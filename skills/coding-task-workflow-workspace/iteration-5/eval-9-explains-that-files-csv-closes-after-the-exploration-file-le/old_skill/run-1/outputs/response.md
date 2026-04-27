# Evaluation: Artifact Closure Timeline and Phase 7 Task Graph Storage

## Test Case

- **Goal**: Understand the clean issue tree lifecycle
- **Artifacts**: `files.csv`, `sources.md`, `open-questions`
- **Phase 7**: Where task graph YAML lives
- **Context**: Ensuring GitHub issue hierarchy ends cleanly

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), the closure timeline and storage locations are explicitly defined across multiple canonical references.

---

## Artifact Closure Timeline

### 1. files.csv — Closes After Phase 3

**Phase created**: Phase 3 (Codebase Exploration)

**Closure trigger**: Phase 3 Step 7 — as soon as the file ledger is complete

**Reference**: `references/workflow.md` Phase 3 line 114:
> Close the `files.csv` artifact subissue as soon as the file ledger is complete.

**Issue lifecycle confirmation** (`references/issue-hierarchy.md` line 305):
> `files.csv` ledger is complete — Close the `files.csv` artifact subissue

**Status once closed**: 
- Issue state: `closed`
- Not reopened in later phases
- Remains available for reading by Phase 6 (Plan) and beyond

**GitHub location**:
- Parent: Exploration phase issue (#N+3)
- Labels: `agent:artifact`
- Body contains: fenced `csv` block with file list
- Never re-opened after closure

---

### 2. sources.md — Closes After Phase 4

**Phase created**: Phase 4 (Online Research)

**Closure trigger**: Phase 4 Step 6 — as soon as the source ledger is complete

**Reference**: `references/workflow.md` Phase 4 line 139:
> Close the `sources.md` artifact subissue as soon as the source ledger is complete.

**Issue lifecycle confirmation** (`references/issue-hierarchy.md` line 306):
> `sources.md` ledger is complete — Close the `sources.md` artifact subissue

**Status once closed**:
- Issue state: `closed`
- Not reopened in later phases
- Remains available for reading by Phase 5+ as reference for human clarification decisions

**GitHub location**:
- Parent: Research phase issue (#N+4)
- Labels: `agent:artifact`
- Body contains: markdown table with `URL`, `date_checked`, `finding`, `confidence`, `applicability`
- Never re-opened after closure

---

### 3. open-questions — Stays Open Through Phase 5, Then Closes

**Phase created**: Phase 3 (Codebase Exploration)

**Initial status**: `open` (created in Phase 3)

**Phase 3 behavior**: Leave open for Phase 4 research to answer

**Reference** (`references/workflow.md` Phase 3 line 116):
> Leave the `open-questions` artifact issue open until every question is resolved or explicitly marked `needs-human`.

**Phase 4 update**:
- Research phase updates existing questions with answers
- Marks questions `resolved` or escalates to `needs-human`
- Issue remains **open** unless all questions are resolved (rare)

**Reference** (`references/workflow.md` Phase 4 lines 141–142):
> If the `open-questions` artifact issue has no question left at `status: open`, close it here; otherwise leave it open for Phase 5.

**Phase 5 closure trigger**: Phase 5 Step 8

**Reference** (`references/workflow.md` Phase 5 line 167):
> Close the `open-questions` artifact issue once every entry is either resolved or explicitly finalized as `needs-human`; do not leave it open after clarification completes.

**Gate C enforcement** (`references/workflow.md` Phase 5 line 173):
> Gate C: the clarification issue is closed, the `open-questions` artifact issue is closed, and no entry contains both `blocking: true` and `status: unanswered` before Phase 6 begins.

**Status after closure**:
- Issue state: `closed`
- Never re-opened in later phases
- Remains as durable record of all questions asked and their final status

**Issue lifecycle confirmation** (`references/issue-hierarchy.md` lines 307–308):
> `open-questions` still has unresolved entries — Keep the `open-questions` artifact issue open across phases 3–5  
> Every open question is finalized — Close the `open-questions` artifact issue

**GitHub location**:
- Parent: Exploration phase issue (#N+3)
- Labels: `agent:artifact`
- Body contains: markdown table with `id`, `question`, `status`, `resolved_by`, `answer`
- Updated across phases 3, 4, and 5
- Closed in Phase 5, after clarification completes

---

## Phase 7 Task Graph YAML Storage

### Location: Phase Issue Body (Not Artifact Subissue)

**Key specification** (`references/issue-hierarchy.md` lines 193–194):
> For Phase 7 specifically, keep the task graph YAML in the phase issue body. Do not create a separate `task-graph.yaml` artifact subissue.

### Where It Lives

**GitHub issue**: Phase 7 task-graph issue (#N+7)

**Labels**: `agent:phase`, `phase:task-graph`

**Parent**: Top-level parent issue (not an artifact sub-issue)

**Body format**:
```markdown
## Summary

One sentence describing the task decomposition.

## Inputs

- Depends on: #N+6 (plan issue)

## Deliverable

Fenced `yaml` block containing the task graph.

## Exit Criteria

- Task-graph issue is closed
- At least one task has stage: red
- All tasks have dependencies defined
- No circular dependencies

## Machine Data

```yaml
work_id: <slug>
kind: phase
phase: task-graph
status: closed
```
```

### Task Graph YAML Content

Stored in a fenced `yaml` block directly in the Phase 7 issue body, using `references/templates/task-graph.yaml` as the format template.

**Example structure**:
```yaml
version: "1"
tasks:
  - id: task-001
    name: "Write test for retry count"
    depends_on: []
    parallelizable: true
    files:
      - tests/http/retry.test.ts
      - src/http/retry.ts
    
  - id: task-002
    name: "Implement exponential backoff"
    depends_on: [task-001]
    parallelizable: false
    files:
      - src/http/retry.ts
      - src/utils/backoff.ts
    
  - id: task-003
    name: "Add jitter to backoff"
    depends_on: [task-002]
    parallelizable: true
    files:
      - src/http/retry.ts
      - src/utils/jitter.ts
```

### Why Not an Artifact Subissue?

From the README (line 166):
> Task graph | 7 | `phase:task-graph` child issue | YAML task graph in fenced `yaml`

The task graph is **phase-owned** — it lives in the phase issue body, not as a separate artifact subissue, because:

1. **Single primary output**: Phase 7 has one main deliverable (the task graph), not multiple artifacts
2. **Durable reference**: The YAML must stay with the phase issue for GitHub sub-issue hierarchy clarity
3. **Distinction from tasks**: Task issues are separate entities (`#N+7a`, `#N+7b`, etc.), not the graph itself
4. **Simpler closure**: Phase issue closes when YAML and task issues are ready; no extra artifact issue to manage

### Related Task Issues

While the YAML stays in the Phase 7 issue, **task issues are separate GitHub issues**:

- **Creation**: One issue per vertical slice (Step 5)
- **Attachment**: Each task issue is attached as a sub-issue to the Phase 7 task-graph issue
- **Labels**: `agent:task`, `phase:implement`, `parallel` or `sequential`
- **Body**: Task details, files list, progress log section, Machine Data
- **Closure**: Each task issue closes when its vertical slice is complete (after RED → GREEN → REFACTOR)

**Example task issue hierarchy**:
```
Phase 7 (#N+7) [phase:task-graph]
├── Task issue #N+7a [agent:task] [phase:implement] — Task: task-001
├── Task issue #N+7b [agent:task] [phase:implement] — Task: task-002
└── Task issue #N+7c [agent:task] [phase:implement] — Task: task-003
```

Each task issue contains its own progress log as comments, but the overall task graph YAML stays in `#N+7` body.

---

## Clean Issue Tree Summary

### Timeline and Closures

| Phase | Artifact | Created | Status | Closed In | Never Reopened |
|-------|----------|---------|--------|-----------|----------------|
| 3 | `files.csv` | Phase 3 | `closed` | Phase 3 (step 7) | Yes |
| 4 | `sources.md` | Phase 4 | `closed` | Phase 4 (step 6) | Yes |
| 3–5 | `open-questions` | Phase 3 | `open` (3–5) → `closed` | Phase 5 (step 8) | Yes |
| 7 | Task graph YAML | Phase 7 | `in issue body` | N/A (phase-owned) | N/A |

### Expected Final Issue Tree (After Phase 11, Before PR Merge)

```
Parent issue #N [agent:parent] [OPEN — closes on PR merge]
├── #N+1 [phase:intake] [closed]
├── #N+2 [phase:worktree] [closed]
├── #N+3 [phase:exploration] [closed]
│   ├── #N+3a [artifact] files.csv [CLOSED]
│   └── #N+3b [artifact] open-questions [CLOSED]
├── #N+4 [phase:research] [closed]
│   └── #N+4a [artifact] sources.md [CLOSED]
├── #N+5 [phase:clarification] [closed]
├── #N+6 [phase:plan] [closed]
├── #N+7 [phase:task-graph] [CLOSED with YAML in body]
│   ├── #N+7a [phase:implement] Task 1 [closed]
│   ├── #N+7b [phase:implement] Task 2 [closed]
│   └── #N+7c [phase:implement] Task 3 [closed]
├── #N+8 [phase:review] [closed]
├── #N+9 [phase:verify] [closed]
└── #N+10 [phase:pr] [CLOSED immediately after PR opened]
```

**Result**: Clean, linear tree with all child issues closed except parent (which closes on PR merge).

---

## References

| Specification | Location |
|---|---|
| files.csv closure | `references/workflow.md` Phase 3, line 114 |
| sources.md closure | `references/workflow.md` Phase 4, line 139 |
| open-questions lifecycle | `references/workflow.md` Phases 3–5, lines 116, 141–142, 167 |
| Phase 7 task graph storage | `references/issue-hierarchy.md` line 193 |
| Issue lifecycle table | `references/issue-hierarchy.md` lines 299–320 |
| Gate C (open-questions closure) | `references/workflow.md` Phase 5, line 173 |
| README phase artifacts | `README.md` line 166 |
