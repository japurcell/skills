# Evaluation: Phase 1 Intake for coding-task-workflow

## Test Case

- **Input**: `ISSUE: 42` and `WORK_ITEM: maybe clean up auth later`
- **GitHub Issue #42 Body**: Describes a CSV import bug that silently drops rows

## Baseline Skill Specification

From the baseline skill (`skill-snapshot-phase8-phase10`), Phase 1 Intake has the following authoritative rules:

### Non-Negotiable Rule #1

From `SKILL.md` (lines 29):
> If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.

### Phase 1 Workflow Specification

From `references/workflow.md` (Phase 1 — Intake, lines 50-51):
> 1. If `ISSUE` is provided, fetch the GitHub issue with `gh issue view <ISSUE> --json number,title,body,url,id` and infer `WORK_ITEM` from the issue title/body before classification. Treat separately supplied `WORK_ITEM` text as supplemental context only.

## What Phase 1 Intake Should Do

Given `ISSUE: 42` and the conflicting `WORK_ITEM: maybe clean up auth later`:

1. **Fetch GitHub issue #42** with `gh issue view 42 --json number,title,body,url,id`

2. **Use GitHub issue #42 title/body as the authoritative work item**, not the user-supplied text.
   - The GitHub issue describes: **CSV import bug that silently drops rows** (not auth cleanup)

3. **Treat the separately supplied WORK_ITEM text as supplemental context only**
   - `WORK_ITEM: maybe clean up auth later` is **ignored** for classification and artifact creation
   - It may be recorded as a note but does not override the GitHub source

4. **Classify the work item as `bug`** based on the GitHub issue content (it describes a bug, not cleanup work)

5. **Create or use issue #42 as the parent issue** (do not create a new parent issue)

6. **Create a child intake issue** with:
   - Label `phase:intake`
   - Body based on `templates/intake.md` 
   - Summary and classification derived from GitHub issue #42, not from the user text
   - Acceptance criteria capturing what "not silently dropping rows" means

7. **Attach the intake child issue to #42** using the GitHub sub-issue mutation

## Work Item Authority

| Source | Value | Status |
|--------|-------|--------|
| User typed | `maybe clean up auth later` | **Ignored** — supplemental context only |
| GitHub issue #42 | CSV import bug that silently drops rows | **Authoritative** — canonical WORK_ITEM |

## Rationale

The baseline skill implements a principle of **GitHub-as-source-of-truth** for work items when `ISSUE` is provided. This prevents ambiguity where:

- The user might misremember the issue scope
- The GitHub issue has been updated since the user last read it
- Multiple people might be collaborating on the same work item
- Work needs to resume in a fresh session (GitHub is the durable record, not user memory)

By treating the GitHub issue as authoritative, the skill ensures that all phases use consistent context and that the workflow can be audited from GitHub alone.

## Expected Behavior

Phase 1 Intake will:

1. ✅ Fetch issue #42 from GitHub
2. ✅ Use the CSV import bug description as the canonical work item
3. ✅ Classify as `bug` (not `chore` for "cleanup")
4. ✅ Create a structured intake artifact reflecting the bug description
5. ✅ Discard the user-typed `WORK_ITEM: maybe clean up auth later`
6. ✅ Proceed to Phase 2 with the correct work item

This ensures the workflow remains traceable and auditable in GitHub, preventing the user's contradictory text from corrupting the phase artifacts.
