# Phase 1 Intake Analysis: Authority of GitHub Issue vs. Supplied WORK_ITEM

## Answer Summary

When `ISSUE` is provided, **Phase 1 Intake should:**

1. **Fetch the GitHub issue first** using: `gh issue view 42 --json number,title,body,url,id`
2. **Treat the GitHub issue title/body as the authoritative WORK_ITEM**, not the separately supplied text
3. **Use the CSV import bug** (from the GitHub issue) as the primary work item description
4. **Disregard the separately supplied `WORK_ITEM: maybe clean up auth later`** — treat it only as supplemental context if needed
5. **Use issue #42 as the Phase 1 parent issue** — do not create a new parent issue

## What Intake Should Do

### Step 1: Fetch the Issue
The first step is to fetch GitHub issue #42:
```bash
gh issue view 42 --json number,title,body,url,id
```

The fetched issue title and body will contain the authoritative description: **"CSV import bug that silently drops rows"** (not the auth cleanup mentioned in the separately supplied WORK_ITEM text).

### Step 2: Infer the Primary Work Item
From the GitHub issue:
- **Work Item**: Fix CSV import to prevent silent row drops
- **Classification**: bug (not a feature, refactor, spec, or chore)
- **Why**: The issue describes a broken behavior that must be fixed

### Step 3: Generate the Work Item Slug
Based on the CSV bug:
```
YYYY-MM-DD-fix-csv-import-silent-row-drops
```
(or similar, approximately 50 characters max)

### Step 4: Use Issue #42 as the Parent
- Treat GitHub issue #42 as the lightweight parent issue for the entire workflow
- Do **not** create a new parent issue
- Update its body to match the parent template from [issue-hierarchy.md](references/issue-hierarchy.md)

### Step 5: Create the Intake Child Issue
Create a separate GitHub issue labelled `agent:phase` and `phase:intake` containing the structured intake artifact with:
- **Summary**: One paragraph describing the CSV import bug and its impact
- **Classification**: bug
- **Acceptance Criteria**: Tests that verify CSV rows are no longer silently dropped
- **Known Constraints**: Any constraints on the fix (e.g., backwards compatibility)
- **References**: Link back to parent issue #42
- **Machine Data**: YAML block with work_id, kind, phase, classification, etc.

Attach this intake issue to parent #42 using:
```bash
gh api graphql -f query='mutation($parentId: ID!, $subIssueId: ID!) { addSubIssue(input: {issueId: $parentId, subIssueId: $subIssueId}) { issue { number } } }' \
  -f parentId="$PARENT_NODE_ID" \
  -f subIssueId="$CHILD_NODE_ID"
```

### Step 6: Close the Intake Issue
Once the intake child issue body contains the accepted summary, classification, acceptance criteria, known constraints, references, and machine data, close the issue.

## Governing Workflow Rule

From **SKILL.md (non-negotiable rule #1)**:
> "If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue."

From **workflow.md (Phase 1, Step 1)**:
> "If `ISSUE` is provided, fetch the GitHub issue with `gh issue view <ISSUE> --json number,title,body,url,id` and infer `WORK_ITEM` from the issue title/body before classification. Treat separately supplied `WORK_ITEM` text as supplemental context only."

## Why This Authority Hierarchy

The GitHub issue is the **authoritative source** because:
1. It has been persisted in the repository's issue tracker and can be referenced by others
2. It is the actual work-tracking artifact that downstream phases depend on
3. It survives across sessions and can be audited/verified
4. The inline text provided as `WORK_ITEM: maybe clean up auth later` is transient and may not reflect the actual intended work
5. This rule prevents divergence between what was typed and what is actually tracked in GitHub

The phase 1 Intake must fetch and validate before proceeding so the entire workflow is grounded in the authoritative GitHub issue, not in transient command-line arguments.
