# How coding-task-workflow Creates Phase 6 Plan and Phase 7 Task-Graph Issues

## Overview

The `coding-task-workflow` skill uses a GitHub parent-issue / sub-issue hierarchy to create and link Phase 6 (Plan) and Phase 7 (Task-Graph) issues as child issues of the parent issue created in Phase 1.

Both phases follow the same proven sub-issue creation and linking pattern:
1. Create the child issue normally with `gh issue create`
2. Resolve both parent and child node IDs
3. Attach the child to the parent with a GitHub GraphQL `addSubIssue` mutation

---

## Phase 6 — Plan Issue Creation

### When It Happens

Phase 6 runs **after Gate C is satisfied** (clarification is complete).

### What Gets Created

**One closed Phase 6 issue** with labels:
- `agent:phase`
- `phase:plan`

The issue body contains:
- **Summary** (one sentence)
- **Inputs** reference (parent issue)
- **Deliverable**: the complete implementation plan including:
  - Goal and non-goals
  - Approach and rationale
  - Alternatives considered
  - File-by-file implementation map
  - Verification guidance
- **Exit Criteria** (from workflow.md)
- **Machine Data** (YAML block with metadata)

### The Creation Pattern for Phase 6

```bash
# Step 1: Create the Phase 6 issue normally
gh issue create \
  --title "Plan — 2026-04-27-<work-id>" \
  --body-file /tmp/phase_6_plan.md \
  --label agent:phase \
  --label phase:plan

# Captures the new issue number: PLAN_ISSUE_NUMBER
# For example: Plan issue is #42
```

### Sub-Issue Attachment for Phase 6

Once the Phase 6 issue is created, it is **attached to the parent issue** from Phase 1 using GitHub's GraphQL mutation:

```bash
# Step 2: Resolve the parent node ID (from Phase 1)
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)

# Step 3: Resolve the Plan issue node ID
PLAN_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)

# Step 4: Attach the Plan issue to the parent with GraphQL mutation
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$PLAN_NODE_ID"
```

### Phase 6 Gate (Gate D)

The workflow does **not** proceed to Phase 7 until:
- The Plan issue is **closed**
- An explicit **approval comment** exists on the Plan issue

The approval comment follows this shape:

```markdown
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```
```

---

## Phase 7 — Task-Graph and Implementation Task Issues

### When It Happens

Phase 7 runs **after Gate D is satisfied** (plan is approved and closed).

### What Gets Created

**Two types of issues** are created in Phase 7:

#### 1. The Task-Graph Phase Issue (One)

**Closed Phase 7 issue** with labels:
- `agent:phase`
- `phase:task-graph`

The issue body contains:
- **Summary** (one sentence describing the task graph)
- **Inputs** reference (plan issue)
- **Deliverable**: a fenced YAML block containing the task graph DAG
  - Each task has: `id`, `name`, `depends_on` (list), `parallelizable` (bool), `files` (list)
  - Each task starts at `stage: red`
- **Exit Criteria** (from workflow.md)
- **Machine Data** (YAML block with metadata)

#### 2. Implementation Task Issues (Multiple)

**One issue per vertical slice** with labels:
- `agent:task`
- `phase:implement`
- `parallel` or `sequential` (depending on graph)

Each task issue body contains:
- **Summary** (one sentence describing the slice)
- **Task Details**:
  - `Current stage: red` (initialized)
  - `Task ID: <id>` (from YAML graph)
  - `Depends on tasks: [<ids>]` (from YAML graph)
- **Files** (list of files this task writes to)
- **Progress Log** (empty at creation; will hold RED/GREEN/REFACTOR comments during Phase 8)
- **Machine Data** (YAML block with task metadata)

### The Creation Pattern for Phase 7

#### Step 1: Create the Task-Graph Phase Issue

```bash
# Create the Phase 7 task-graph issue
gh issue create \
  --title "Task Graph — 2026-04-27-<work-id>" \
  --body-file /tmp/phase_7_task_graph.md \
  --label agent:phase \
  --label phase:task-graph

# Captures: TASK_GRAPH_ISSUE_NUMBER (e.g., #43)
```

#### Step 2: Attach Task-Graph Issue to Parent

```bash
# Resolve node IDs
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
TASK_GRAPH_NODE_ID=$(gh issue view <task-graph-issue-number> --json id --jq .id)

# Attach Task-Graph to parent
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$TASK_GRAPH_NODE_ID"
```

#### Step 3: Create Implementation Task Issues

For each task in the YAML graph (e.g., two tasks: `write-test-for-retry` and `implement-backoff`):

```bash
# Create task issue #1
gh issue create \
  --title "Task: write-test-for-retry — 2026-04-27-<work-id>" \
  --body-file /tmp/task_1_body.md \
  --label agent:task \
  --label phase:implement \
  --label parallel

# Captures: TASK_1_ISSUE_NUMBER (e.g., #44)

# Create task issue #2
gh issue create \
  --title "Task: implement-backoff — 2026-04-27-<work-id>" \
  --body-file /tmp/task_2_body.md \
  --label agent:task \
  --label phase:implement \
  --label sequential

# Captures: TASK_2_ISSUE_NUMBER (e.g., #45)
```

#### Step 4: Attach Implementation Task Issues to Task-Graph Issue

Each implementation task is attached to the **Phase 7 task-graph issue** (not directly to the parent):

```bash
# Resolve the task-graph issue node ID (from Step 1)
TASK_GRAPH_NODE_ID=$(gh issue view <task-graph-issue-number> --json id --jq .id)

# Attach Task 1 to Task-Graph issue
TASK_1_NODE_ID=$(gh issue view <task-1-issue-number> --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASK_GRAPH_NODE_ID" \
  -f subIssueId="$TASK_1_NODE_ID"

# Attach Task 2 to Task-Graph issue
TASK_2_NODE_ID=$(gh issue view <task-2-issue-number> --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$TASK_GRAPH_NODE_ID" \
  -f subIssueId="$TASK_2_NODE_ID"
```

### Phase 7 Gate (Gate E)

The workflow **stops** after Phase 7 and does **not** proceed to Phase 8 in the same session.

Gate E is satisfied when:
- The Phase 7 task-graph issue is **closed**
- **At least one implementation task issue has** `stage: red` in its Machine Data
- **Every implementation task issue records an explicit dependency list** (in Machine Data or body)

After Gate E, the workflow **hard-stops** and hands off a resume command:

```
coding-task-workflow RESUME=<slug>
```

The user must resume in a **fresh session** to proceed to Phase 8.

---

## Hierarchy Summary

The complete GitHub issue hierarchy for Phase 6 and Phase 7 looks like this:

```
Parent issue: #N  [agent:parent]  Feature / bug / spec
  ├── Phase 1–5 issues (intake, worktree, exploration, research, clarification)
  │
  ├── Phase 6 issue:  #42 [phase:plan]  Implementation plan
  │   └── (contains approval comment with Machine Data)
  │
  └── Phase 7 issue:  #43 [phase:task-graph]  Task graph
      ├── Task issue: #44 [phase:implement]  Task: slice-name-1
      ├── Task issue: #45 [phase:implement]  Task: slice-name-2
      └── Task issue: #46 [phase:implement]  Task: slice-name-3
```

---

## Key Command Patterns

### Creation Pattern (for any child issue)

```bash
# 1. Create the issue
gh issue create --title "..." --body-file ... --label label1 --label label2

# 2. Capture the new issue number from output
# (or query: gh issue list --search "title" --json number --limit 1)

# 3. Resolve node IDs
PARENT_NODE_ID=$(gh issue view <parent> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <child> --json id --jq .id)

# 4. Attach with GraphQL mutation
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

### Fallback (when GitHub sub-issues are disabled)

If the `addSubIssue` mutation fails, the workflow falls back to a body reference:

```markdown
Parent: #N
```

However, this is **not the primary approach**. The workflow expects GitHub sub-issues to be available.

---

## Non-Negotiable Rules

1. **Child issues are created first**, then linked with `addSubIssue` (not created as subissues directly).
2. **Phase 6 and 7 issues are created as closed or transition to closed** immediately after their content is complete.
3. **Approval for Phase 6 is an explicit comment** on the Phase 6 issue with Machine Data; it is not part of the issue body.
4. **Phase 7 hard-stops after creating task issues**; implementation happens in a resumed session (Phase 8+).
5. **Implementation task issues are children of the Phase 7 task-graph issue**, not the parent issue directly.
6. **Labels are applied consistently**: `agent:phase` and `phase:plan` for Phase 6; `agent:phase` and `phase:task-graph` for Phase 7; `agent:task`, `phase:implement`, and `parallel|sequential` for task issues.

---

## References

- **Phase 6 specification**: `references/workflow.md` (lines 179–198)
- **Phase 7 specification**: `references/workflow.md` (lines 202–223)
- **Issue hierarchy and sub-issue linking**: `references/issue-hierarchy.md` (lines 34–62)
- **GraphQL mutation example**: `references/issue-hierarchy.md` (lines 50–61)
- **Non-negotiable rules**: `SKILL.md` (lines 25–33) and `references/workflow.md` (lines 1–16)
