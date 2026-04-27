# Phase 3 Exploration Outputs Storage Location

## Overview
In Phase 3 (Codebase Exploration) of the coding-task-workflow, all exploration outputs are stored as **GitHub issues and artifact subissues**—not as local files. This follows the core architectural principle that Phases 1–11 use GitHub issues as the canonical durable workflow record.

## Storage Locations

### 1. Exploration Summary
**Location**: GitHub child issue with labels `agent:phase` and `phase:exploration`

**Details**:
- This is a GitHub issue (not a local file)
- Created as a child issue of the parent issue
- The issue **body** contains the consolidated exploration summary using the template from `references/templates/exploration-summary.md`
- Status: **Closed** once the summary is complete
- Contains all synthesized findings from the parallel code-explorer subagents

### 2. files.csv
**Location**: GitHub artifact subissue under the exploration phase issue

**Details**:
- Created as a child issue of the exploration phase issue
- Labeled with `agent:artifact` (implied by being an artifact subissue)
- The file list is stored in a **fenced `csv` code block** within the issue body
- Format: CSV data directly embedded in the issue body, not as an attachment
- Status: **Closed** as soon as the file ledger is complete
- Purpose: Provides a resumable file ledger for other agents to reference later

### 3. open-questions
**Location**: GitHub artifact subissue under the exploration phase issue

**Details**:
- Created as a child issue of the exploration phase issue
- Labeled with `agent:artifact` (implied by being an artifact subissue)
- Each question includes: `id`, `question`, `status: open`, `resolved_by`, and `answer`
- Format: Markdown table or bullet list within the issue body
- Status: **Left open** until every question is resolved or explicitly marked `needs-human`
- Purpose: Tracks open questions throughout research (Phase 4) and clarification (Phase 5) phases

## GitHub Issue Hierarchy

```
Parent Issue (#N)
├── Exploration Phase Issue (closed)
│   ├── files.csv artifact subissue (closed)
│   └── open-questions artifact subissue (open until Phase 5 completes)
```

## Key References

Per Phase 3 specification (workflow.md lines 112-116):
- **Line 113**: "Create a GitHub child issue labelled `agent:phase` and `phase:exploration`. Its body uses [templates/exploration-summary.md](templates/exploration-summary.md) for the consolidated exploration summary."
- **Line 114**: "Create a `files.csv` artifact subissue under the exploration issue. Store the file list in a fenced `csv` block so other agents can resume from GitHub alone."
- **Line 115-116**: "Create an `open-questions` artifact subissue under the exploration issue. Store each question with `id`, `question`, `status: open`, `resolved_by`, and `answer`."

## Critical Principle

All Phase 3 outputs live exclusively in **GitHub issue bodies and artifact subissues**. There are **no local per-work-item artifacts** created under `.coding-workflow/work/<slug>/` in Phases 1–11. This design enables:

- **Resume capability**: Any future session can fetch complete exploration state from GitHub
- **Durable workflow record**: GitHub issues serve as the single source of truth
- **Cross-phase continuity**: Phase 4 research agents read the `open-questions` artifact issue directly from GitHub
- **No local file management**: Simplifies resumption and eliminates stale local artifacts
