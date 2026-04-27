# Evaluation: GitHub Issue Creation and Linking in coding-task-workflow

## Overview

The task: Explain exactly how the workflow should create the Phase 6 plan issue and Phase 7 implementation-task issues under the parent issue from Phase 1, including the concrete GitHub commands the workflow expects.

---

## Executive Summary

The `coding-task-workflow` skill uses a **three-step GitHub issue creation and linking pattern**:

1. **Create the child issue** normally with `gh issue create`
2. **Resolve both parent and child node IDs** using `gh issue view --json id`
3. **Attach via GraphQL mutation** using `gh api graphql` with the `addSubIssue` mutation

This pattern is mandatory and non-negotiable, not optional. Fallback to body references like `Parent: #N` only when the repository cannot execute GraphQL mutations.

---

## Detailed Process for Phase 6 (Plan) and Phase 7 (Implementation Tasks)

### Phase 6 — Creating the Plan Issue

**When**: After Phase 5 (Clarification) is complete and Gate C is satisfied.

**Step 1: Create the plan issue**

```bash
gh issue create \
  --title "Plan — 2026-04-27-add-retry-mechanism" \
  --body-file plan_issue_body.md \
  --label "agent:phase" \
  --label "phase:plan"
```

The `plan_issue_body.md` must follow the template from `references/templates/plan.md` with these required sections:

- `## Goal / Non-Goals` — What the plan covers and does not cover
- `## Recommended Approach` — 1–3 paragraphs with implementation strategy
- `## Alternatives Considered` — Trade-offs (omit if none)
- `## File-by-File Implementation Map` — Table of files and changes
- `## Verification Guidance` — Test commands, manual checks, acceptance mapping
- `## Approval` — Explicit human sign-off required
- `## Machine Data` — YAML block with work_id, kind, phase, status, depends_on

**Output**: Returns the new plan issue number, e.g., `#123`.

**Step 2: Resolve node IDs**

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view 123 --json id --jq .id)
```

**Step 3: Attach to parent via GraphQL**

```bash
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

**Result**: The plan issue (#123) now appears in GitHub as a child of the parent issue. The GraphQL mutation is the success criterion; if it fails, record the failure and use `Parent: #<number>` as a fallback marker in the issue body.

**Step 4: Present for human approval and gate on response**

- Display a concise plan summary to the human.
- Ask for explicit approval: "Does this plan look correct? Should I proceed with implementation?"
- The human responds with a comment on the plan issue.

**Step 5: Record approval as a comment**

```bash
gh issue comment <plan-issue-number> --body '
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: 2026-04-27T14:32:00Z
```
'
```

**Step 6: Close the plan issue**

```bash
gh issue close <plan-issue-number>
```

After Gate D is satisfied (plan issue closed + approval comment exists), proceed to Phase 7.

---

### Phase 7 — Creating the Task-Graph Issue and Implementation Tasks

**When**: After Phase 6 plan is approved and Gate D is satisfied.

#### Step A: Create the task-graph issue

```bash
gh issue create \
  --title "Task Graph — 2026-04-27-add-retry-mechanism" \
  --body-file taskgraph_issue_body.md \
  --label "agent:phase" \
  --label "phase:task-graph"
```

The `taskgraph_issue_body.md` contains:

- `## Summary` — One sentence describing the task graph
- `## Inputs` — References to the plan issue and other dependencies
- `## Deliverable` — The task graph YAML (kept in the phase issue body, not a separate artifact subissue)
- `## Exit Criteria` — Copied from Gate E in `references/stop-gates.md`
- `## Machine Data` — YAML block with work_id, kind, phase, status, depends_on

The **YAML task graph** stays embedded in the phase issue body using the shape from `references/templates/task-graph.yaml`:

```yaml
work_id: 2026-04-27-add-retry-mechanism
phase: task-graph
status: complete
updated_at: "2026-04-27T14:45:00Z"

tasks:
  - id: t1
    name: "Write retry policy test"
    stage: red
    depends_on: []
    parallelizable: false
    files:
      - src/retry/retry.test.ts
      - src/retry/retry.ts

  - id: t2
    name: "Implement retry policy"
    stage: red
    depends_on: [t1]
    parallelizable: false
    files:
      - src/retry/retry.test.ts
      - src/retry/retry.ts

  - id: t3
    name: "Integrate client with retry"
    stage: red
    depends_on: [t2]
    parallelizable: false
    files:
      - src/http/client.ts
      - src/http/client.test.ts
```

**Output**: Returns the task-graph issue number, e.g., `#124`.

#### Step B: Attach task-graph issue to parent

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
TASKGRAPH_NODE_ID=$(gh issue view 124 --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$TASKGRAPH_NODE_ID"
```

#### Step C: Create implementation task issues (one per vertical slice)

For **each task in the YAML** (t1, t2, t3, etc.), create a separate implementation task issue:

```bash
gh issue create \
  --title "Task: t1 — Write retry policy test" \
  --body-file task_t1_body.md \
  --label "agent:task" \
  --label "phase:implement" \
  --label "sequential"
```

Each implementation task issue body follows the template from `references/issue-hierarchy.md`:

```markdown
## Summary

Write failing test for single retry with exponential backoff.

## Task Details

- **Current stage**: red
- **Task ID**: t1
- **Depends on tasks**: (none)

## Files

- src/retry/retry.test.ts
- src/retry/retry.ts

## Progress Log

<!-- RED / GREEN / REFACTOR comments go here as the task progresses -->

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
  - src/retry/retry.test.ts
  - src/retry/retry.ts
status: open
```
```

**Output**: Returns task issue numbers, e.g., `#125` for t1, `#126` for t2, `#127` for t3.

#### Step D: Attach each task issue under the task-graph issue

For **each task issue**, repeat the resolve-and-attach pattern:

```bash
# For t1 task issue #125
TASKGRAPH_NODE_ID=$(gh issue view 124 --json id --jq .id)
TASK_T1_NODE_ID=$(gh issue view 125 --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASKGRAPH_NODE_ID" \
  -f subIssueId="$TASK_T1_NODE_ID"
```

Repeat for t2 (#126), t3 (#127), and all other tasks in the graph.

#### Step E: Close the task-graph issue

```bash
gh issue close 124
```

After Gate E is satisfied (task-graph closed, at least one task at `stage: red`, all tasks have `depends_on` lists), the workflow **stops and does not proceed to Phase 8 in the same session**.

---

## GitHub Issue Hierarchy Diagram

After Phase 7 completes, the GitHub issue tree looks like:

```
#N   Parent issue [agent:parent] — 2026-04-27-add-retry-mechanism
├── #N+1  [phase:intake]         Intake artifact (closed)
├── #N+2  [phase:worktree]       Worktree metadata (closed)
├── #N+3  [phase:exploration]    Exploration summary (closed)
│   ├── #N+3a [artifact]         files.csv (closed)
│   └── #N+3b [artifact]         open-questions (closed)
├── #N+4  [phase:research]       Research findings (closed)
│   └── #N+4a [artifact]         sources.md (closed)
├── #N+5  [phase:clarification]  Clarifications (closed)
├── #N+6  [phase:plan]           Implementation plan (closed, with approval comment)
├── #N+7  [phase:task-graph]     Task graph YAML (closed)
│   ├── #N+7a [agent:task]       Task: t1 — Write test (open, stage: red)
│   ├── #N+7b [agent:task]       Task: t2 — Implement (open, stage: red)
│   └── #N+7c [agent:task]       Task: t3 — Integrate (open, stage: red)
```

All child issues are created via `gh issue create`, then linked with the `addSubIssue` GraphQL mutation. This creates actual GitHub sub-issue relationships visible in the UI.

---

## Label Application

During creation, apply these labels immediately:

**For Phase 6 plan issue**:
- `agent:phase` — identifies this as a phase-level artifact
- `phase:plan` — identifies this as the Plan phase

**For Phase 7 task-graph issue**:
- `agent:phase` — identifies this as a phase-level artifact
- `phase:task-graph` — identifies this as the Task-Graph phase

**For Phase 7 implementation task issues**:
- `agent:task` — identifies this as a task-level issue
- `phase:implement` — identifies these as implementation-phase tasks
- `parallel` — if the task can run concurrently with others (set in `parallelizable: true` in YAML)
- `sequential` — if the task must run in order (set in `parallelizable: false` in YAML)

---

## Machine Data (Structured Metadata)

Every issue must include a `## Machine Data` YAML block for resumability and durable state tracking.

**Phase 6 plan issue Machine Data**:
```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: plan
status: open (or closed after approval)
depends_on:
  - clarification
```

**Phase 7 task-graph issue Machine Data**:
```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: phase
phase: task-graph
status: open (or closed once YAML and task issues complete)
depends_on:
  - plan
```

**Phase 7 implementation task issue Machine Data**:
```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: task
phase: implement
task_id: t1  # matches YAML task id
stage: red   # starts at red, updates to green then refactor as work progresses
parallelizable: false  # or true per YAML
depends_on: []         # or [t1, t2] per YAML task depends_on
files:
  - src/retry/retry.test.ts
  - src/retry/retry.ts
status: open (or closed when slice complete)
```

**Plan approval comment Machine Data**:
```yaml
work_id: 2026-04-27-add-retry-mechanism
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: 2026-04-27T14:32:00Z
```

---

## Fallback to Body References

**Only if GitHub sub-issue mutations fail or are disabled**, use a fallback `Parent: #N` marker in the child issue body:

```markdown
## Summary

Write failing test for single retry with exponential backoff.

## Parent

- Parent issue: #N
- Phase issue: #N+7
```

The comment should explain the mutation failure:

> SubIssue mutation failed (reason). Falling back to body reference Parent: #N. Manual linking may be required.

However, this fallback is **not preferred**. The GitHub `addSubIssue` mutation is the canonical linking mechanism.

---

## What the Workflow Does NOT Do

❌ Create local `.coding-workflow/work/<slug>/phase-6-plan.md` files after Phase 0 Bootstrap.  
❌ Embed child issue numbers only in parent issue body (no actual sub-issue relationship).  
❌ Use `Parent: #N` as the primary linking mechanism (only fallback).  
❌ Skip label assignment or Machine Data blocks.  
❌ Create a separate `task-graph.yaml` artifact subissue (YAML stays in phase issue body).

---

## Complete Example Command Sequence

For a work item with parent issue #100:

```bash
# Phase 6: Create plan issue
PLAN_ISSUE=$(gh issue create --title "Plan — 2026-04-27-add-retry-mechanism" \
  --body-file plan.md --label agent:phase --label phase:plan --json number --jq .number)

# Attach plan to parent
PARENT_ID=$(gh issue view 100 --json id --jq .id)
PLAN_ID=$(gh issue view $PLAN_ISSUE --json id --jq .id)
gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) {
  addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
    issue { number }
  }
}' -f parentId="$PARENT_ID" -f subIssueId="$PLAN_ID"

# Record human approval
gh issue comment $PLAN_ISSUE --body "Approved. Proceed with implementation.
## Machine Data
\`\`\`yaml
work_id: 2026-04-27-add-retry-mechanism
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
\`\`\`"

# Close plan issue
gh issue close $PLAN_ISSUE

# Phase 7: Create task-graph issue
TASKGRAPH_ISSUE=$(gh issue create --title "Task Graph — 2026-04-27-add-retry-mechanism" \
  --body-file taskgraph.md --label agent:phase --label phase:task-graph --json number --jq .number)

# Attach task-graph to parent
TASKGRAPH_ID=$(gh issue view $TASKGRAPH_ISSUE --json id --jq .id)
gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) {
  addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
    issue { number }
  }
}' -f parentId="$PARENT_ID" -f subIssueId="$TASKGRAPH_ID"

# Create and attach each implementation task
for TASK_ID in t1 t2 t3; do
  TASK_ISSUE=$(gh issue create --title "Task: $TASK_ID — [description]" \
    --body-file task_$TASK_ID.md --label agent:task --label phase:implement \
    --label sequential --json number --jq .number)
  
  TASK_NODE=$(gh issue view $TASK_ISSUE --json id --jq .id)
  gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' -f parentId="$TASKGRAPH_ID" -f subIssueId="$TASK_NODE"
done

# Close task-graph issue
gh issue close $TASKGRAPH_ISSUE
```

---

## Key Rules (Non-Negotiable)

From `SKILL.md` Non-negotiable rules and `references/issue-hierarchy.md`:

1. **Child issues are created first**, then linked. Never reverse the order.
2. **GitHub `addSubIssue` GraphQL mutation is mandatory** — the primary linking mechanism, not `Parent: #N` body references.
3. **Both parent and child node IDs must be resolved** with `gh issue view --json id --jq .id` before the mutation.
4. **Only fallback to `Parent: #N`** if the GraphQL mutation fails or the repository disables sub-issues.
5. **Labels are applied at creation time**, not added later.
6. **Machine Data YAML blocks are required** in every issue body and every durable comment.
7. **The task-graph YAML stays in the phase issue body**, not in a separate artifact subissue.

---

## Conclusion

The workflow creates Phase 6 plan issues and Phase 7 implementation task issues as **actual GitHub sub-issues**, not body references. The three-step pattern (create → resolve node IDs → attach via GraphQL) is deterministic, testable, and resumable from GitHub state alone. The complete GitHub issue tree becomes the durable workflow record, enabling agents to resume at any phase by reading issue state.
