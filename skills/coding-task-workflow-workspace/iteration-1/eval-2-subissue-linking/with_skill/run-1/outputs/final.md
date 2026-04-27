Create the child issue first, resolve both node IDs, then attach it with `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.

Phase 6 plan issue:
- Use the Phase 1 parent issue as the parent; do not create a new parent.
- Create one child issue for the plan, labeled at least `phase:plan` (and consistently with the hierarchy labels, `agent:phase`). Its body should point at `.coding-workflow/work/<slug>/05-plan.md`.
- Command shape:
  ```bash
  gh issue create     --title "Implementation plan — <slug>"     --label "phase:plan"     --label "agent:phase"     --body "<phase sub-issue body linking 05-plan.md>"
  ```
- Then resolve IDs and link it:
  ```bash
  PARENT_NODE_ID=$(gh issue view <parent-number> --json id --jq .id)
  CHILD_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)

  gh api graphql -f query='    mutation($parentId: ID!, $subIssueId: ID!) {      addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {        issue { number }      }    }'     -f parentId="$PARENT_NODE_ID"     -f subIssueId="$CHILD_NODE_ID"
  ```

Phase 7 implementation-task issues:
- After `06-task-graph.yaml` exists, create child issues for each major implementation task; group minor slices if there would be more than 8 issues.
- Each task issue is created first, then linked to the same Phase 1 parent issue with the same `addSubIssue` flow.
- Label each issue `phase:implement` plus `parallel` or `sequential` as appropriate, and consistently `agent:task`.
- Command shape per task:
  ```bash
  gh issue create     --title "Task: <task name>"     --label "phase:implement"     --label "parallel"   # or sequential
    --label "agent:task"     --body "<implementation task body with task_id, stage, depends_on, files, parent refs>"
  ```
- Then link each created task issue:
  ```bash
  PARENT_NODE_ID=$(gh issue view <parent-number> --json id --jq .id)
  CHILD_NODE_ID=$(gh issue view <task-issue-number> --json id --jq .id)

  gh api graphql -f query='    mutation($parentId: ID!, $subIssueId: ID!) {      addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {        issue { number }      }    }'     -f parentId="$PARENT_NODE_ID"     -f subIssueId="$CHILD_NODE_ID"
  ```

The workflow treats the GraphQL mutation as the success criterion. Only if GitHub sub-issues are unavailable should it fall back to putting `Parent: #<parent-number>` in the child body; if the mutation is disabled, it should also record the failed attempt in `.coding-workflow/work/<slug>/issue-hierarchy.md`.