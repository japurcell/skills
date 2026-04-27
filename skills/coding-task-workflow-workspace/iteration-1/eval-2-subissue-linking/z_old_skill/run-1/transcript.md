## Eval Prompt
Using coding-task-workflow, explain exactly how the workflow should create the Phase 6 plan issue and Phase 7 implementation-task issues under the parent issue from Phase 1. Include the concrete GitHub commands or command shapes the workflow expects.

## Files Read
- /home/adam/dev/personal/skills/skills/coding-task-workflow-workspace/skill-snapshot/SKILL.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow-workspace/skill-snapshot/references/workflow.md
- /home/adam/dev/personal/skills/skills/coding-task-workflow-workspace/skill-snapshot/references/issue-hierarchy.md

## Steps
1. Read `SKILL.md` to get the governing rule for sub-issues and the required response style.
2. Read the Phase 6 and Phase 7 sections in `references/workflow.md` to confirm when the plan issue and implementation-task issues are created and which labels/linking sequence they require.
3. Read `references/issue-hierarchy.md` to capture the exact `gh issue view` node-ID lookup commands, the `gh api graphql` `addSubIssue` mutation, and the fallback rule.
4. Wrote the required run artifacts with the final user-facing answer.

## Final Answer
Create the child issue first, resolve both node IDs, then attach it with gh api graphql ... addSubIssue. Parent: #N is fallback-only when GitHub sub-issues are unavailable.

For Phase 6, create one child issue labeled `phase:plan` for the plan artifact, then link it under the Phase 1 parent. The expected shape is:

```bash
gh issue create ... --label phase:plan
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <plan-issue-number> --json id --jq .id)
gh api graphql -f query='
  mutation($parentId: ID!, $subIssueId: ID!) {
    addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) {
      issue { number }
    }
  }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

For Phase 7, create child issues for each major implementation task from `06-task-graph.yaml` (group minor slices if there are more than 8), label each `phase:implement` plus `parallel` or `sequential`, then do the same node-ID lookup and `addSubIssue` mutation for each one:

```bash
gh issue create ... --label phase:implement --label parallel
# or --label sequential
PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_NODE_ID=$(gh issue view <task-issue-number> --json id --jq .id)
gh api graphql -f query='...' -f parentId="$PARENT_NODE_ID" -f subIssueId="$CHILD_NODE_ID"
```

The success criterion is the GraphQL sub-issue mutation. Only if GitHub sub-issues are unavailable should the workflow fall back to putting `Parent: #N` in the child issue body and recording the failed mutation/reason.
