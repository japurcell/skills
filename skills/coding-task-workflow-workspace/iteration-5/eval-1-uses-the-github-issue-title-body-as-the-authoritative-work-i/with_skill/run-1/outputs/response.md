# coding-task-workflow Phase 1 Intake Evaluation

## User Input

- `ISSUE: 42`
- `WORK_ITEM: maybe clean up auth later`
- GitHub issue #42 body describes: a CSV import bug that silently drops rows

## Skill Specification: What Phase 1 Intake Should Do

**From SKILL.md, Non-negotiable rules, rule #1:**

> If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. **The GitHub issue title/body is the authoritative `WORK_ITEM`**, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

**From references/workflow.md, Phase 1 — Intake, Step 1:**

> If `ISSUE` is provided, fetch the GitHub issue with `gh issue view <ISSUE> --json number,title,body,url,id` and infer `WORK_ITEM` from the issue title/body before classification. **Treat separately supplied `WORK_ITEM` text as supplemental context only.**

**From SKILL.md, Workflow-rule answers, "Intake authority" entry:**

> `The GitHub issue title/body is the authoritative WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

## Analysis

Phase 1 Intake has a clear priority order:

1. **Authoritative source**: The GitHub issue title/body (#42 describing the CSV import bug)
2. **Supplemental context**: The user-typed `WORK_ITEM: maybe clean up auth later` (treated as secondary)
3. **Parent issue**: Use issue #42 as-is; do not create a new parent issue

The conflict between the user's typed work item and the GitHub issue body is resolved definitively in the workflow specification: the GitHub issue is authoritative.

## Correct Behavior for Phase 1 Intake

When invoked with `ISSUE: 42 WORK_ITEM: maybe clean up auth later`:

1. **Fetch issue #42** using `gh issue view 42 --json number,title,body,url,id`
2. **Extract the work item from issue #42's title and body** — the CSV import bug description becomes the authoritative `WORK_ITEM`
3. **Acknowledge the user's text** (`maybe clean up auth later`) as supplemental context but do not use it as the primary work item
4. **Classify the work from issue #42**: bug (CSV import silently drops rows)
5. **Generate slug** from the issue title: e.g., `YYYY-MM-DD-csv-import-drops-rows`
6. **Use issue #42 as the parent issue** — refresh its body with the parent template but preserve useful summary text; do not create a new parent issue
7. **Create a child issue** labelled `phase:intake` with the structured intake artifact
8. **Close the intake issue** once complete

## Summary

| Aspect | Decision |
|--------|----------|
| **Work item source** | GitHub issue #42 body (CSV import bug) — authoritative |
| **User-typed WORK_ITEM** | `maybe clean up auth later` — treated as supplemental context only, not used |
| **Parent issue** | Use #42 as-is; do not create a new parent issue |
| **Classification** | `bug` (from the issue description: silent data loss) |
| **Slug basis** | Issue #42's title (e.g., "CSV import silently drops rows" → `YYYY-MM-DD-csv-import-drops-rows`) |
| **Next action** | Create a `phase:intake` child issue under #42 with structured intake artifact |

This ensures the workflow remains grounded in the authoritative source (the GitHub issue) rather than ad-hoc user input that may be stale or incomplete.
