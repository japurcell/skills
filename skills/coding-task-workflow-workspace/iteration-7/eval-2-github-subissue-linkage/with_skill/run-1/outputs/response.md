## Sub-issue creation rule (Phases 6 and 7)

**Create the child issue first, resolve both node IDs, then attach it with `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.**

The same three-step shape applies to the Phase 6 plan sub-issue and to every Phase 7 implementation-task sub-issue. The Phase 1 parent issue (either the supplied `ISSUE` or the one created in Phase 1) is the `parentId` in every call.

### Command shapes

1. Create the child issue:

   ```bash
   gh issue create --title "<child title>" --body "<child body>"
   ```

   - Phase 6: one issue titled e.g. `Implementation plan — <slug>`, labelled `agent:phase` + `phase:plan`.
   - Phase 7: one issue per task from `06-task-graph.yaml`, labelled `agent:task` + `phase:implement` (+ `parallel` or `sequential`).

2. Resolve both node IDs:

   ```bash
   PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
   CHILD_NODE_ID=$(gh issue view <child-issue-number>  --json id --jq .id)
   ```

3. Attach the child as a true GitHub sub-issue:

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

The successful `addSubIssue` mutation is the success criterion. For Phase 7, repeat steps 1–3 for each task in the graph.

### Fallback

Only if the repo cannot use GitHub sub-issues: create the child normally and put `Parent: #N` in its body, then record the failed mutation in `.coding-workflow/work/<slug>/issue-hierarchy.md`.
