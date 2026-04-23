The workflow requires **true GitHub sub-issues** under the Phase 1 parent issue, not just `Parent: #N`, whenever `addSubIssue` is available.

Assume the Phase 1 parent issue is `#<PARENT>`.

## Phase 6 — plan issue
After writing `05-plan.md`, create the child issue first, using the **phase sub-issue** format and labels `agent:phase` + `phase:plan`.

Command shape:

```bash
gh issue create \
  --title "Implementation plan — <slug>" \
  --label "agent:phase" \
  --label "phase:plan" \
  --body "<phase sub-issue body linking .coding-workflow/work/<slug>/05-plan.md>"
```

Then resolve node IDs and attach it to the parent:

```bash
PARENT_NODE_ID=$(gh issue view <PARENT> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <PLAN_ISSUE_NUMBER> --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

That Phase 6 body should include the required machine data, e.g. `kind: phase`, `phase: plan`, `sequence: 6`, `artifact: .coding-workflow/work/<slug>/05-plan.md`.

## Phase 7 — implementation-task issues
After writing `06-task-graph.yaml`, create one child issue for each **major** implementation task (group minor slices only if there would be more than 8 issues). Each uses the **implementation task sub-issue** format and labels `agent:task`, `phase:implement`, and exactly one of `parallel` or `sequential`.

Command shape per task:

```bash
gh issue create \
  --title "Task: <task name>" \
  --label "agent:task" \
  --label "phase:implement" \
  --label "parallel"    # or "sequential" \
  --body "<implementation task body from 06-task-graph.yaml>"
```

Then attach each task issue with the same required flow:

```bash
PARENT_NODE_ID=$(gh issue view <PARENT> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <TASK_ISSUE_NUMBER> --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

Each Phase 7 body must include task machine data such as `kind: task`, `task_id`, `stage`, `parallelizable`, `depends_on`, and `files`.

## Required order
The workflow’s expected sequence is always:

```bash
gh issue create ...
gh issue view ... --json id --jq .id
gh api graphql ... addSubIssue
```

`Parent: #<PARENT>` is **fallback only** if GitHub sub-issues are unavailable. In that case, create the child issue normally, add `Parent: #<PARENT>` to the body, and record the failed mutation and reason in `.coding-workflow/work/<slug>/issue-hierarchy.md`.
