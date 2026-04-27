# How coding-task-workflow Creates Phase 6 (Plan) and Phase 7 (Task Graph) Issues

## Overview

The `coding-task-workflow` creates Phase 6 (Plan) and Phase 7 (Task Graph) issues as child issues under the parent issue established in Phase 1. The workflow uses GitHub's actual sub-issue relationship for linking, not just body references, with `addSubIssue` GraphQL mutations to attach each phase issue to the parent.

---

## Phase 6 — Plan Issue Creation

### Context
- The parent issue was created in Phase 1 and serves as the top-level container for all phase-specific work.
- Before Phase 6 begins, Phases 1–5 have already been completed and their issues have been created and attached to the parent.

### Steps and GitHub Commands

#### Step 1: Create the Plan Issue

Create a new GitHub issue with the `phase:plan` label and `agent:phase` role label:

```bash
gh issue create \
  --title "Plan — <work-item-slug>" \
  --body-file plan_issue_body.md \
  --label "agent:phase" \
  --label "phase:plan" \
  --repo <owner>/<repo>
```

The issue body uses the **Phase issue template** from [issue-hierarchy.md](issue-hierarchy.md#phase-issue-template) and must include:
- A summary of what the plan produced
- Inputs section listing `Parent: #N` and dependencies on prior phase issues
- The deliverable: the full implementation plan including goal/non-goals, approach/rationale, alternatives, file-by-file implementation map, and verification guidance
- Exit criteria (copied from Gate D)
- Machine data block (YAML):

```yaml
work_id: <slug>
kind: phase
phase: plan
depends_on: [<issue numbers for intake, exploration, research, clarification>]
status: open
```

#### Step 2: Resolve Node IDs for Parent and Plan Issue

Before attaching the Plan issue to the parent, get the internal GraphQL node IDs:

```bash
# Get the parent issue's node ID
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)

# Get the Plan issue's node ID (immediately after creation)
PLAN_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)
```

#### Step 3: Attach Plan Issue to Parent with GraphQL Mutation

Use the `addSubIssue` GraphQL mutation to establish the parent-child relationship:

```bash
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$PLAN_NODE_ID"
```

**Success criterion**: The GraphQL mutation returns successfully with the parent issue number in the response. If the mutation fails (e.g., repository does not support sub-issues), fall back to adding `Parent: #N` body reference in the plan issue.

#### Step 4: Gate on Human Approval

- Present a concise plan summary to the human for review
- Wait for explicit approval before proceeding
- Record the approval as a comment on the plan issue using the **Plan approval comment template**:

```markdown
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601 timestamp>
```
```

#### Step 5: Close the Plan Issue

After approval is recorded as a comment, close the plan issue. The plan issue remains attached to the parent and becomes the reference for Phase 7.

---

## Phase 7 — TDD Task Graph and Implementation Task Issues

### Context
- Gate D has passed: the plan issue is closed and contains an explicit approval comment
- The workflow now creates the task graph issue and one child issue per vertical slice
- All task issues are created as grandchildren: attached to the task-graph issue, which is itself attached to the parent

### Steps and GitHub Commands

#### Step 1: Create the Task Graph Issue

Create a GitHub issue with the `phase:task-graph` label and `agent:phase` role label to hold the YAML task graph:

```bash
gh issue create \
  --title "TDD Task Graph — <work-item-slug>" \
  --body-file task_graph_issue_body.md \
  --label "agent:phase" \
  --label "phase:task-graph" \
  --repo <owner>/<repo>
```

The issue body uses the **Phase issue template** and must include:
- A summary describing the decomposition of the plan into vertical slices
- Inputs section listing `Parent: #N` and dependency on the plan issue
- The deliverable: a fenced YAML block containing the task graph (one entry per vertical slice) using [templates/task-graph.yaml](templates/task-graph.yaml) as the shape:

```yaml
tasks:
  - id: <task-id>
    name: <human-readable-name>
    description: <brief description of the vertical slice>
    depends_on: []
    parallelizable: true|false
    files: [<list-of-file-paths>]

  - id: <task-id-2>
    name: <name>
    description: <description>
    depends_on: [<task-id>]
    parallelizable: true|false
    files: [<list-of-file-paths>]
```

Machine data block:

```yaml
work_id: <slug>
kind: phase
phase: task-graph
depends_on: [<plan-issue-number>]
status: open
```

#### Step 2: Attach Task Graph Issue to Parent

Resolve node IDs and attach using the same GraphQL mutation:

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
TASK_GRAPH_NODE_ID=$(gh issue view <task-graph-issue-number> --json id --jq .id)

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

For each vertical slice in the task graph, create one implementation task issue. These issues are attached to the task-graph issue, not directly to the parent.

For each slice:

```bash
gh issue create \
  --title "Implement <task-name> — <work-item-slug>" \
  --body-file task_<id>_body.md \
  --label "agent:task" \
  --label "phase:implement" \
  --label "parallel|sequential" \
  --repo <owner>/<repo>
```

The task issue body uses the **Implementation task issue template** and must include:
- Summary: one sentence describing the vertical slice this task owns
- Task Details:
  - Current stage: red (initialized here)
  - Task ID: the id from the task graph YAML
  - Depends on tasks: list of task IDs this task depends on
- Files: list of files this task may write to
- Progress Log: empty section where RED / GREEN / REFACTOR comments will be added
- Machine data block (YAML):

```yaml
work_id: <slug>
kind: task
phase: implement
task_id: <id>
stage: red
parallelizable: true|false
depends_on: [<list-of-task-ids>]
files: [<paths>]
status: open
```

#### Step 4: Attach Each Task Issue Under the Task Graph Issue

For each implementation task issue, resolve node IDs and attach to the task-graph issue (not to the parent):

```bash
TASK_GRAPH_NODE_ID=$(gh issue view <task-graph-issue-number> --json id --jq .id)

for TASK_ISSUE_NUMBER in <list-of-task-issue-numbers>; do
  TASK_NODE_ID=$(gh issue view $TASK_ISSUE_NUMBER --json id --jq .id)
  
  gh api graphql -f query='
    mutation($parentId: ID!, $subIssueId: ID!) {
      addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
        issue { number }
      }
    }' \
    -f parentId="$TASK_GRAPH_NODE_ID" \
    -f subIssueId="$TASK_NODE_ID"
done
```

#### Step 5: Close the Task Graph Issue

After all implementation task issues are created and attached, close the task-graph issue:

```bash
gh issue close <task-graph-issue-number>
```

The task issues remain open at `stage: red`, ready for Phase 8 execution.

#### Step 6: Hard Stop and Hand Off

After Gate E is satisfied (task-graph issue is closed, at least one implementation task is at `stage: red`, and every task issue records explicit dependencies), stop the current session. Hand off a resume command:

```
coding-task-workflow RESUME=<slug>
```

Do NOT proceed to Phase 8 in the same invocation.

---

## Complete Issue Hierarchy

After Phase 7 completes, the GitHub issue hierarchy looks like this:

```
Parent issue: #N  [agent:parent]  <work-item-title>
├── Intake issue:          [phase:intake]         (closed)
├── Worktree issue:        [phase:worktree]       (closed)
├── Exploration issue:     [phase:exploration]    (closed)
├── Research issue:        [phase:research]       (closed)
├── Clarification issue:   [phase:clarification]  (closed)
├── Plan issue:            [phase:plan]           (closed, with approval comment)
└── Task graph issue:      [phase:task-graph]     (closed)
    ├── Task issue #1:     [phase:implement]      (open, stage: red)
    ├── Task issue #2:     [phase:implement]      (open, stage: red)
    └── Task issue #3:     [phase:implement]      (open, stage: red)
```

---

## Key Principles

1. **Create, then attach**: Each issue is created first as a standalone GitHub issue, then resolved to its GraphQL node ID, then attached via the `addSubIssue` mutation.

2. **Exact command shape**: The workflow expects the exact `gh api graphql` mutation shape shown above, with `-f query='...'` and `-f parentId/subIssueId` parameters.

3. **GraphQL success is the criterion**: The mutation succeeding is what makes the link real. Only fall back to `Parent: #N` body references if the repository cannot run the mutation.

4. **Metadata in YAML**: Every issue includes machine-readable YAML in a `## Machine Data` block to track work_id, phase, status, and dependencies. This enables resuming and reconstructing the workflow state.

5. **Labels consistently applied**: `agent:phase` and `phase:plan` for Phase 6; `agent:phase` and `phase:task-graph` for Phase 7; `agent:task`, `phase:implement`, and `parallel|sequential` for each implementation task.

6. **Sequential phases 6–7, parallel tasks in 8**: Phase 6 and Phase 7 are created sequentially in the same session. Phase 7 tasks are designed for parallelization in Phase 8, but created serially in Phase 7.

---

## When GitHub Sub-Issues Are Not Available

If the GraphQL `addSubIssue` mutation fails (repository does not support sub-issues):

1. Create the child issue normally
2. Add `Parent: #N` as an explicit body reference in the child issue
3. Record the failed mutation attempt as a comment on the child issue
4. Do NOT fall back to local per-work-item markdown artifacts

The workflow treats the GraphQL mutation failure as a repository limitation, not a fallback to local files.
