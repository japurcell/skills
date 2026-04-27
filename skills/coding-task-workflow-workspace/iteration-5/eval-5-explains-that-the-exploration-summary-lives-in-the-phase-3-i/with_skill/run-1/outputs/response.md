# coding-task-workflow Phase 3 Exploration Artifact Storage Evaluation

## Overview

In the current coding-task-workflow specification, **Phase 3 exploration outputs are stored exclusively in GitHub as a hierarchy of interconnected issues**. There are no local markdown files created per work item.

## Storage Architecture

The skill specifies a **three-level GitHub issue hierarchy** for Phase 3 exploration outputs:

```
Parent Issue (#N)
└── Phase 3 Exploration Issue [phase:exploration]
    ├── Artifact Sub-issue: files.csv
    └── Artifact Sub-issue: open-questions
```

## Detailed Storage Locations

### 1. Exploration Summary

**Storage**: `phase:exploration` child issue (main phase issue)

**From workflow.md Phase 3, Step 5:**
> Create a GitHub child issue labelled `agent:phase` and `phase:exploration`. Its body uses [templates/exploration-summary.md](templates/exploration-summary.md) for the consolidated exploration summary.

**Details**:
- **Type**: GitHub issue (child of parent, peer to other phase issues)
- **Labels**: `agent:phase`, `phase:exploration`
- **Body content**: Consolidated exploration summary using the exploration-summary template
- **Content includes**:
  - Codebase findings and anti-patterns
  - Key modules and their interactions
  - Observed patterns and conventions
  - Initial recommendations
- **Lifecycle**: Created in Phase 3, closed once summary is complete (Step 9)

### 2. files.csv Artifact

**Storage**: Artifact subissue under the exploration issue

**From workflow.md Phase 3, Step 6:**
> Create a `files.csv` artifact subissue under the exploration issue. Store the file list in a fenced `csv` block so other agents can resume from GitHub alone.

**Details**:
- **Type**: GitHub issue (artifact subissue of phase:exploration)
- **Labels**: `artifact` (implied; acts as a named artifact container)
- **Title**: `files.csv` (or similar identifying label)
- **Body content**: File list stored in fenced `csv` code block
- **Structure**: CSV table with columns like:
  - `file_path`
  - `reason` (why this file is relevant)
  - `agent_found_by` (which explorer agent surfaced it)
  - Possibly: `pattern`, `notes`
- **Lifecycle**: Created in Phase 3 Step 6, **closed in Phase 3 Step 7 immediately after the file ledger is complete**
- **Why GitHub**: "so other agents can resume from GitHub alone"

### 3. Open Questions Artifact

**Storage**: Artifact subissue under the exploration issue

**From workflow.md Phase 3, Step 8:**
> Create an `open-questions` artifact subissue under the exploration issue. Store each question with `id`, `question`, `status: open`, `resolved_by`, and `answer`.

**Details**:
- **Type**: GitHub issue (artifact subissue of phase:exploration)
- **Labels**: `artifact` (implied; acts as a named artifact container)
- **Title**: `open-questions` (or similar identifying label)
- **Body content**: Question ledger with machine-readable fields per entry:
  - `id`: unique question identifier
  - `question`: the open question text
  - `status`: `open | resolved | needs-human`
  - `resolved_by`: which phase/agent resolved it (if applicable)
  - `answer`: the answer or resolution (if applicable)
- **Format**: Structured markdown or YAML (must survive across phases)
- **Lifecycle**: Created in Phase 3 Step 8
  - **Left open** at end of Phase 3 (Step 9)
  - Updated during Phase 4 research (research findings resolve questions)
  - Updated during Phase 5 clarification (human answers questions)
  - **Closed in Phase 5** once every question is either resolved or marked `needs-human` (Step 8 of Phase 5)

## GitHub Issue Hierarchy Structure

From README.md and issue-hierarchy.md:

```
Parent Issue: #N [agent:parent]  ← Lightweight work-item index
  │
  ├── Exploration Issue: #N+3 [phase:exploration]  ← Phase 3 summary
  │   ├── Artifact Issue: files.csv  ← Closed in Phase 3
  │   └── Artifact Issue: open-questions  ← Left open, updated through Phase 5
  │
  ├── Research Issue: #N+4 [phase:research]  ← Phase 4 (uses open-questions)
  │   └── Artifact Issue: sources.md
  │
  ├── Clarification Issue: #N+5 [phase:clarification]  ← Phase 5 (updates open-questions)
  │
  ├── Plan Issue: #N+6 [phase:plan]
  │   ...
```

## Linking Mechanism

**From issue-hierarchy.md:**

Every artifact subissue follows this flow:

1. **Create** the artifact issue first:
   ```bash
   gh issue create --title "files.csv" --body "..." --repo owner/repo
   ```

2. **Resolve both node IDs**:
   ```bash
   PARENT_NODE_ID=$(gh issue view <phase:exploration-issue> --json id --jq .id)
   CHILD_NODE_ID=$(gh issue view <files.csv-issue> --json id --jq .id)
   ```

3. **Attach with GraphQL mutation**:
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

4. **Fallback**: If GitHub sub-issues are unavailable, use `Parent: #N` body reference only

## Key Principle: No Local Files

**From SKILL.md, Non-negotiable rule #2:**

> Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.

**Implication for Phase 3**: Do not create local exploration artifacts like:
- ❌ `.coding-workflow/work/2026-04-23-add-retry-mechanism/exploration-summary.md`
- ❌ `.coding-workflow/work/2026-04-23-add-retry-mechanism/files.csv`
- ❌ `.coding-workflow/work/2026-04-23-add-retry-mechanism/open-questions.md`

All of these live in GitHub issues instead.

## Why This Design?

1. **Persistence across sessions**: All workflow state persists in GitHub, not in local ephemeral files
2. **Resume-friendly**: A fresh session can fetch the parent issue, find all child issues, and resume from anywhere
3. **Parallel agent safety**: Multiple agents can read and update `open-questions` atomically via GitHub's issue API
4. **Audit trail**: GitHub preserves all edits, comments, and issue state transitions
5. **Cross-phase visibility**: Later phases (4, 5) directly reference and update Phase 3 artifacts via issue links

## Summary Table

| Artifact | Parent | Type | Status at end of Phase 3 | Updated by | Closed by |
|----------|--------|------|--------------------------|------------|-----------|
| **Exploration Summary** | Parent Issue | `phase:exploration` child issue | Closed | Exploration agents | Phase 3 Step 9 |
| **files.csv** | Exploration issue | Artifact subissue | **Closed** | Exploration agents | Phase 3 Step 7 |
| **open-questions** | Exploration issue | Artifact subissue | **Open** | Research (Phase 4), Clarification (Phase 5) | Phase 5 Step 8 |

## Specification References

- **README.md**: "Phase artifacts" table (lines 150–170)
- **issue-hierarchy.md**: Hierarchy tree structure and linking flow
- **workflow.md Phase 3**: Step-by-step artifact creation and lifecycle (lines 91–125)
- **SKILL.md, Non-negotiable rule #2**: GitHub issues are canonical; no local per-work-item files (line 30)

This GitHub-native design ensures that all exploration work is discoverable, resumable, and auditable through the parent issue and its child/artifact issue hierarchy.
