# Phase 1 GitHub Issues for New Feature Request (No Existing ISSUE)

## Summary
Now that local per-work-item markdown files are gone, Phase 1 creates **two separate GitHub issues** instead of a single local `.coding-workflow/work/<slug>/00-intake.md` file.

## Exactly What Phase 1 Creates

### 1. **Lightweight Parent Issue** (`agent:parent` label)
- **Purpose**: Top-level tracker for the entire work item
- **Created**: Always created as a new issue (since no existing ISSUE was provided)
- **Body**: Matches the parent issue template from issue-hierarchy.md with:
  - Summary section
  - Current Phase field
  - Acceptance Snapshot (compact checklist)
  - Sub-issues list (placeholder checklist for all phases 1–11)
  - Machine Data block with: `work_id`, `kind: parent`, `classification`, `status`, `current_phase`, `source_issue`
- **Status**: Remains **open** throughout the workflow (not closed until PR merge)
- **Labels**: `agent:parent`

### 2. **Separate Intake Child Issue** (`agent:phase` + `phase:intake` labels)
- **Purpose**: Holds the structured intake artifact (the detailed work analysis)
- **Created**: New child issue attached to the parent via `addSubIssue` GraphQL mutation
- **Body**: Structured intake artifact based on `templates/intake.md`, containing:
  - Summary (one-line description)
  - Classification (feature | bug | refactor | spec | chore)
  - Acceptance Criteria (structured list)
  - Known Constraints
  - References (links to related issues, specs, or documentation)
  - Machine Data block with: `work_id`, `kind: phase`, `phase: intake`, `depends_on`, `status`
- **Status**: **Closed** once intake details are complete (captures historical state)
- **Labels**: `agent:phase`, `phase:intake`

## Linking Process
The child intake issue is **attached to the parent issue** using GitHub's native sub-issue relationship:
1. Create the child issue first
2. Resolve both node IDs (parent and child)
3. Call `gh api graphql` with `addSubIssue` mutation
4. Result: Intake issue becomes a child of the parent in GitHub's UI

## What Is NOT Created
- ❌ **No local `.coding-workflow/work/<slug>/00-intake.md`** — local per-work-item markdown files are gone
- ❌ **No local artifact files in the repo** — all durable state lives in GitHub issues and comments for Phases 1–11
- ❌ **No single combined issue** — intake is not collapsed into the parent body; it lives in its own dedicated child issue

## Why This Design
- **Separation of concerns**: Parent issue tracks overall status; intake issue preserves the intake analysis
- **Resumable state**: Each phase issue can be closed and reopened independently; GitHub is the canonical record
- **Durable history**: When a phase completes, close that phase issue; future `RESUME=<slug>` commands can rebuild full workflow state from GitHub
- **No local sprawl**: Bootstrap (Phase 0) writes override files, but Phases 1–11 exclusively use GitHub—no per-work-item markdown cluttering the repo

## Summary for the User
When Phase 1 runs on a new feature request with no existing ISSUE:

1. **Creates a new parent issue** labelled `agent:parent` that tracks the full work item lifecycle
2. **Creates a separate intake child issue** labelled `phase:intake` with the detailed structured artifact
3. **Attaches the intake issue to the parent** via GitHub sub-issue relationship
4. **Closes the intake issue** once it captures the classification, acceptance criteria, and constraints
5. **Leaves the parent issue open** to track progress through Phases 2–11
6. **Does NOT create any local markdown files** — GitHub is now the durable workflow record
