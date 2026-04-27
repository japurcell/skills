Create the child issue first, resolve both node IDs, then attach it with `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.

- **Phase 6 plan issue:** create the `[phase:plan]` issue normally (for example, `gh issue create --title "Plan — <slug>" --body-file <plan-body.md>`), resolve the **Phase 1 parent issue** node ID and the new **plan issue** node ID with `gh issue view <issue-number> --json id --jq .id`, then attach the plan issue to the Phase 1 parent with `addSubIssue`.
- **Phase 7 task issues:** first create the `[phase:task-graph]` issue and attach it to the **Phase 1 parent** the same way. Then create each implementation task issue normally, resolve the **task-graph issue** node ID plus the new **task issue** node ID, and attach each task issue with the same `addSubIssue` mutation. In other words, the implementation-task issues are true GitHub sub-issues under the task-graph issue, which itself sits under the Phase 1 parent.
- **Command shape:**

```bash
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <child-issue-number> --json id --jq .id)

gh api graphql -f query='  mutation($parentId: ID!, $subIssueId: ID!) {    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {      issue { number }    }  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

Only if GitHub sub-issues are unavailable should the workflow fall back to putting `Parent: #N` in the child issue body and recording that the mutation failed or is unsupported.
