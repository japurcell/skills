Use the Phase 1 parent issue as the single root. For both Phase 6 and Phase 7, the workflow requires this exact sequence: **create the child issue first**, **resolve both node IDs**, then **attach it with `addSubIssue`**. A plain `Parent: #N` body reference is fallback-only if GitHub sub-issues are unavailable.

**Phase 6 — plan issue**
1. Write `05-plan.md`.
2. Present the plan summary and get explicit approval.
3. Create a Phase 6 child issue using the **phase sub-issue template**, with labels `agent:phase` and `phase:plan`.

Command shape:
```bash
gh issue create \
  --title "Implementation plan — <slug>" \
  --body "<phase sub-issue body linking .coding-workflow/work/<slug>/05-plan.md>" \
  --label agent:phase \
  --label phase:plan
```
4. Resolve node IDs:
```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)
```
5. Attach the plan issue as a real sub-issue:
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

**Phase 7 — implementation-task issues**
1. Write `06-task-graph.yaml`.
2. Create **one child issue per major implementation task**; if there are more than 8 minor slices, group them to avoid issue noise.
3. Each task issue should use the **implementation task sub-issue template** and be labeled `agent:task`, `phase:implement`, plus `parallel` or `sequential`.

Command shape:
```bash
gh issue create \
  --title "Task: <slice name>" \
  --body "<implementation task body with task_id, stage, depends_on, files, parent refs>" \
  --label agent:task \
  --label phase:implement \
  --label parallel   # or --label sequential
```
4. For each task issue, resolve IDs and link it the same way:
```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <task-issue-number> --json id --jq .id)

gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

The workflow treats the GraphQL mutation succeeding as the success criterion. Only if the repository cannot use GitHub sub-issues should it fall back to adding `Parent: #<parent>` in the child body and recording the failed mutation in `.coding-workflow/work/<slug>/issue-hierarchy.md`.
