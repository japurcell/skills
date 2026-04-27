Create the child issue first, then link it. For Phase 6, create the plan issue with `gh issue create`, resolve both node IDs, and attach it to the Phase 1 parent with the literal-ID `addSubIssue` mutation:

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)
gh api graphql -f query="
  mutation {
    addSubIssue(input: {issueId: "$PARENT_NODE_ID", subIssueId: "$CHILD_NODE_ID"}) {
      issue { number }
    }
  }"
```

Phase 7 uses the same shape: create the `phase:task-graph` issue under the Phase 1 parent, then create each implementation task issue and attach it under the task-graph issue with the same literal-ID mutation pattern. A plain `Parent: #N` marker is fallback-only when true GitHub sub-issues are unavailable.
