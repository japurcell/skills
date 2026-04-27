# Phase 3 Exploration Outputs Storage in GitHub

## Overview

In the `coding-task-workflow` skill, Phase 3 (Codebase Exploration) produces multiple artifacts that are **all stored in GitHub as part of the issue hierarchy**, not as local repository files. This follows the core principle stated in the workflow specification: "Phase 0 writes repo-local override files; Phases 1–11 use GitHub issues and comments as the canonical durable workflow record."

## Artifact Storage Locations

### 1. Exploration Summary

**Location:** GitHub child issue body (the exploration phase issue itself)

- **Label:** `agent:phase` and `phase:exploration`
- **Content:** The consolidated exploration summary using the template from `references/templates/exploration-summary.md`
- **Sections included:**
  - Summary paragraph explaining the exploration outcome
  - Track Selected (light/standard/deep with rationale)
  - Key Findings (important patterns, constraints, architectural insights)
  - Anti-patterns to Avoid
  - Relevant Files Snapshot (3–5 key files)
  - Open Questions Snapshot (high-level unresolved questions)
  - Machine Data (YAML metadata with `work_id`, `kind: phase`, `phase: exploration`, `status`, `track`, `agents_launched`, `depends_on`)
- **Status:** Closed once the summary is complete
- **Parent:** Attached to the main parent issue via `addSubIssue` GraphQL mutation

### 2. files.csv Artifact

**Location:** GitHub artifact subissue under the exploration phase issue

- **Label:** `artifact` (plus `phase:exploration` for context)
- **Artifact Name:** `files.csv`
- **Content Format:** Fenced CSV block in the issue body
- **Contents:** A ledger of 5–10 key files with:
  - File path
  - Reason for inclusion (why it's relevant to the work item)
  - Observed patterns
  - Any notes or context
- **Status:** Closed as soon as the file ledger is complete
- **Purpose:** Allows other agents to resume from GitHub alone without re-reading exploration summaries
- **Parent:** Attached under the exploration phase issue via `addSubIssue`

### 3. open-questions Artifact

**Location:** GitHub artifact subissue under the exploration phase issue

- **Label:** `artifact` (plus `phase:exploration` for context)
- **Artifact Name:** `open-questions`
- **Content Format:** Structured entries in the issue body (can be bullet list or table format)
- **Contents:** Each question includes:
  - `id`: unique identifier for the question
  - `question`: the unresolved question text
  - `status`: `open`, `resolved`, or `needs-human`
  - `resolved_by`: which phase/agent resolved it (if applicable)
  - `answer`: the resolution or answer (once available)
- **Status:** 
  - Stays **open** through Phase 3
  - May remain open into Phase 4 (Online Research) and Phase 5 (Clarification)
  - Closed in Phase 5 once every question is either `resolved` or explicitly marked `needs-human`
- **Parent:** Attached under the exploration phase issue via `addSubIssue`
- **Lifecycle:** Unlike `files.csv` which closes immediately, `open-questions` is intentionally left open to track resolution across multiple phases

## GitHub Issue Hierarchy Structure

```
Parent Issue (parent:)
├── Phase 1: Intake Issue (phase:intake)
├── Phase 2: Worktree Issue (phase:worktree)
├── Phase 3: Exploration Issue (phase:exploration) ← HERE
│   ├── Artifact: files.csv (artifact:)
│   └── Artifact: open-questions (artifact:)
├── Phase 4: Research Issue (phase:research)
│   ├── Artifact: sources.md (artifact:)
│   └── (open-questions updated here, not moved)
├── Phase 5: Clarification Issue (phase:clarification)
│   └── (open-questions closed here)
...
```

## Key Design Principles

1. **No Local Per-Work-Item Files**: Phase 3 does NOT create `.coding-workflow/work/<slug>/exploration/` directories or local markdown files. All state is in GitHub.

2. **Separate Artifact Subissues**: Rather than putting all Phase 3 outputs in the phase issue body, the workflow creates separate artifact subissues for:
   - `files.csv` (to support resume from GitHub alone)
   - `open-questions` (to track resolution across multiple phases)

3. **Resume-Friendly**: When a session resumes with `RESUME=<slug>`, it reads the exploration phase issue and its artifact subissues directly from GitHub. The `files.csv` artifact is particularly important for resuming from Phase 4+ without re-reading the full exploration summary.

4. **Gate A Checkpoint**: Phase 3 completes when:
   - The exploration phase issue is closed
   - The `files.csv` artifact subissue is closed
   - The `open-questions` artifact subissue exists and is open

## Summary Table

| Artifact | GitHub Location | Parent | Format | Status at End of Phase 3 |
|----------|-----------------|--------|--------|--------------------------|
| Exploration Summary | Phase 3 issue body | Parent issue | Markdown | Closed |
| files.csv | Artifact subissue | Phase 3 issue | CSV block | Closed |
| open-questions | Artifact subissue | Phase 3 issue | Markdown table/bullets | Open |

