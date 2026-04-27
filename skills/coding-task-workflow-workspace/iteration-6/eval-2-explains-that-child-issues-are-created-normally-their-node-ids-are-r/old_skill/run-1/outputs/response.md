Create each child issue first, then link it. The older command shape resolves both node IDs and calls `gh api graphql` with `addSubIssue`, for example:

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }'               -f parentId="$PARENT_NODE_ID"               -f subIssueId="$CHILD_NODE_ID"
```

Use that flow for the Phase 6 plan issue and the Phase 7 implementation issues. `Parent: #N` is only the fallback when GitHub sub-issues cannot be created.
