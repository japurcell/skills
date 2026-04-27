# Phase 1 Intake: GitHub Issue Authority

## What Intake Should Do

According to the coding-task-workflow skill specification (SKILL.md, line 29 and workflow.md Phase 1 steps):

**Phase 1 Intake with `ISSUE: 42` should:**

1. **Fetch the GitHub issue first** using:
   ```bash
   gh issue view 42 --json number,title,body,url,id
   ```

2. **Use the GitHub issue title/body as the authoritative `WORK_ITEM`**
   - The issue body describing "CSV import bug that silently drops rows" is the authoritative source
   - The separately typed input `WORK_ITEM: maybe clean up auth later` is treated as supplemental context only
   - If there is a conflict between the two, the GitHub issue takes precedence

3. **Keep issue #42 as the Phase 1 parent issue**
   - Do NOT create a new parent issue
   - Refresh the parent issue body to match the parent template from [issue-hierarchy.md](issue-hierarchy.md)
   - Preserve any useful existing summary text

4. **Create a separate intake child issue**
   - Label it: `agent:phase` and `phase:intake`
   - Body: structured intake artifact based on [templates/intake.md](references/templates/intake.md)
   - Include the GitHub-sourced work item (CSV import bug) in the intake summary
   - List acceptance criteria inferred from the bug description
   - Record known constraints

5. **Link the intake child issue to parent #42**
   - Use `gh api graphql` with the `addSubIssue` mutation to create a true GitHub sub-issue relationship
   - This maintains the durable issue hierarchy visible in GitHub

6. **Close the intake issue** once complete

## The Work Item

**Authoritative work item (from GitHub issue #42 body):**
```
Bug: CSV import silently drops rows
```

**Why NOT "maybe clean up auth later":**
- The user's typed `WORK_ITEM: maybe clean up auth later` conflicts with the issue body
- Per the non-negotiable rule in SKILL.md: "The GitHub issue title/body is the authoritative `WORK_ITEM`"
- Local user input is supplemental context only when an `ISSUE` parameter is provided
- Intake must use the authoritative source (the GitHub issue) to ensure consistency, auditability, and prevent operator error

## Governance

This follows the non-negotiable rule from SKILL.md (line 29):

> If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

This rule ensures that:
- The GitHub issue is the single source of truth
- Work item scope is auditable (the issue is always linked in the git history)
- Other agents can resume without losing context
- The issue hierarchy is preserved for visibility
