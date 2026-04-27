# GitHub Artifact Schema

Every durable Phase 1–11 artifact produced by `coding-task-workflow` must be represented in GitHub as an issue body, artifact subissue, task issue, or issue comment. This document defines the shared structure.

---

## Common `## Machine Data` Fields

All workflow issues and durable comments must include a `## Machine Data` section with a fenced YAML block.

```yaml
work_id: <slug>         # e.g. 2026-04-27-add-retry-mechanism
kind: <kind>            # parent | phase | artifact | task | approval | implementation-log
status: <status>        # open | closed | approved | complete | blocked
```

Add the following fields where applicable:

```yaml
phase: <phase-name>     # intake | worktree | exploration | research | clarification | plan | task-graph | implement | review | verify | pr
depends_on:             # issue numbers, artifact keys, or task ids
  - <dependency>
classification: <type>  # feature | bug | refactor | spec | chore (parent / intake only)
artifact_name: <name>   # files.csv | open-questions | sources.md | <custom> (artifact issues only)
format: <format>        # markdown | csv | yaml | table | checklist
task_id: <id>           # implementation task issues and implementation-log comments only
stage: <stage>          # current stage for a task issue or implementation-log comment: red | green | refactor
parallelizable: <bool>  # implementation task issues only
updated_at: <ISO8601>
```

---

## Parent Issue Requirements

Required sections:

- `## Summary`
- `## Current Phase`
- `## Acceptance Snapshot`
- `## Sub-issues`
- `## Machine Data`

The parent issue stays lightweight. It links the workflow together but does not replace the detailed phase artifacts.

---

## Phase Issue Requirements

Required sections:

- `## Summary`
- `## Inputs`
- `## Deliverable`
- `## Exit Criteria`
- `## Machine Data`

Use the phase issue body for the primary artifact. When the phase has multiple named outputs that need durable status or separate resume context, create artifact subissues beneath the phase issue rather than overloading the body.

The Phase 7 task graph is phase-owned: keep the fenced `yaml` block in the `phase:task-graph` issue body rather than creating a separate `task-graph.yaml` artifact subissue.

---

## Artifact Subissue Requirements

Required sections:

- `## Summary`
- `## Parent`
- `## Artifact`
- `## Machine Data`

Artifact subissues preserve file-like outputs in GitHub. Render the payload directly in the body:

- `files.csv` → fenced `csv` block
- `sources.md` → Markdown table
- question ledgers or checklists → Markdown bullets / tables

Artifact subissues should close as soon as their payload is complete unless they intentionally track active state across phases. `open-questions` is the main exception: keep it open only while research/clarification is still resolving entries, then close it once every question is finalized.

---

## Implementation Task Issue Requirements

Required sections:

- `## Summary`
- `## Task Details`
- `## Files`
- `## Progress Log`
- `## Machine Data`

Each implementation task issue represents one vertical slice. Task issue state replaces `07-implementation-log.md`:

- RED / GREEN / REFACTOR progress is recorded as comments.
- The `stage` field records the slice's current stage and is updated in place on the same issue.
- The task issue closes when the slice is complete.
- Dependencies live in the machine-data block and the human-readable body.

---

## Comment Schemas

### Plan approval comment

Required content:

- A short human approval statement.
- A `## Machine Data` YAML block with:

```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```

### Implementation log comment

Required content:

- `## Slice Update — <task_id> / <stage>`
- `status`
- `files_changed`
- `test_result`
- `notes`
- `## Machine Data`

```yaml
work_id: <slug>
kind: implementation-log
task_id: <id>
stage: red | green | refactor
status: complete | blocked
updated_at: <ISO8601>
```

---

## Resume Expectations

`RESUME=<slug>` must reconstruct state from GitHub alone:

1. Find the parent issue or phase issue chain by `work_id`.
2. Read closed phase issues for completed artifacts.
3. Read open artifact / task issues for remaining work.
4. Read approval and implementation-log comments where relevant.

Do **not** assume `.coding-workflow/work/<slug>/` exists.
