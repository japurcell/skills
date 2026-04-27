# Phase 1 (Intake) Issue Creation for New Feature Requests

## The Scenario

A new feature request arrives with no existing GitHub issue. The `coding-task-workflow` is invoked with just a work item description (no `ISSUE` parameter).

## Exactly What Phase 1 Creates

Phase 1 creates **two distinct GitHub issues**:

### 1. **Lightweight Parent Issue** (`agent:parent` label)

This is the top-level tracker for the entire work item across all 11 phases.

**Characteristics:**
- Single parent issue that persists for the entire workflow lifecycle
- Labelled `agent:parent`
- No phase label (it tracks work across all phases, not a single phase)
- Body follows the parent template from [issue-hierarchy.md](issue-hierarchy.md):
  - Summary section (one paragraph describing the work item, source, and expected outcome)
  - Current Phase section (names the next phase or blocker)
  - Acceptance Snapshot section (short numbered list from the intake issue)
  - Sub-issues section (checklist of all phase issues, initially unchecked)
  - Machine Data block (YAML with `work_id`, `kind: parent`, `classification`, `status`, `current_phase`, `source_issue: null`)
- Closed only at the very end (Phase 11 PR closes it via `Fixes #N`)

### 2. **Intake Child Issue** (`phase:intake` label, `agent:phase` label)

This is a separate phase-specific issue that holds the structured intake artifact.

**Characteristics:**
- Labelled both `agent:phase` and `phase:intake`
- Body is the structured intake artifact based on [templates/intake.md](templates/intake.md):
  - Summary (one paragraph describing the work item)
  - Classification (feature | bug | refactor | spec | chore, with rationale)
  - Acceptance Criteria (numbered list of independently verifiable criteria)
  - Known Constraints (language/framework, scope, deadline, compatibility, etc.)
  - References (parent issue link, source spec, related issues, prior art)
  - Machine Data block (YAML with `work_id`, `kind: phase`, `phase: intake`, `classification`, `status`, `source_issue: null`)
- **Attached to the parent issue** using the GitHub sub-issue relationship (via `gh api graphql ... addSubIssue`)
- Closed once the body contains the accepted summary, classification, acceptance criteria, known constraints, references, and Machine Data
- This issue holds all the intake details; the parent issue only keeps an Acceptance Snapshot

## Linking the Two Issues

The two issues are linked by:
1. **GitHub sub-issue relationship**: The intake issue is created first, then attached to the parent via GraphQL mutation `addSubIssue`
2. **Machine Data references**: Both issues record the `work_id` (the deterministic slug `YYYY-MM-DD-<kebab-title>`)
3. **Parent issue checklist**: The parent's Sub-issues section includes a checkbox for the intake issue (e.g., `- [ ] #N+1 Intake`)

## What Is NOT Created

- **No local per-work-item markdown files** under `.coding-workflow/work/<slug>/00-intake.md` or similar
- The workflow no longer creates durable phase artifacts as local files
- Phases 1–11 use GitHub issues and comments as the canonical durable workflow record
- Only Phase 0 (Bootstrap) creates repo-local override files under `.coding-workflow/overrides/`

## Why Two Separate Issues?

Separating the parent from the intake phase issue enables:
1. **Durable artifact isolation**: Each phase gets its own issue, so Phase 3 exploration findings are separate from Phase 1 intake, Phase 4 research is separate, etc.
2. **Independent closure**: The parent stays open until merge; phase issues close as they complete
3. **Clear provenance**: Each GitHub issue records exactly which phase produced it (via the `phase` label and Machine Data)
4. **Resume capability**: When resuming a workflow after Phase 7 with `RESUME=<slug>`, the agent can rebuild the full state from GitHub alone, reading the parent issue and its descendant phase issues in order

## Summary

For a new feature request with no existing issue:

**Phase 1 creates:**
1. A new **parent issue** (labelled `agent:parent`) that serves as the top-level tracker for all 11 phases
2. A new **intake phase issue** (labelled `phase:intake` + `agent:phase`) containing the structured intake artifact
3. An explicit **sub-issue relationship** linking the intake issue to the parent (via GitHub's sub-issue API)

**Phase 1 does NOT create:**
- Local per-work-item markdown files (these were removed in favor of GitHub-native tracking)
- Any other phase issues (those are created in their respective phases)
