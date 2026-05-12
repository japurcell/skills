# Issue Hierarchy

This document defines how GitHub issues and sub-issues are used to track work items. For this workflow, GitHub is the durable record for Phases 1–11; local per-work-item markdown files are intentionally not used after Bootstrap.

---

## Hierarchy Structure

Every work item has one lightweight **parent issue** plus descendant issues that hold the actual phase artifacts.

```text
Parent issue: #N  [agent:parent]  <work-item title>
├── Intake issue:          [phase:intake]         Structured intake artifact
├── Worktree issue:        [phase:worktree]       Worktree / branch metadata
├── Exploration issue:     [phase:exploration]    Exploration summary
│   ├── Artifact issue:    files.csv              files.csv content
│   └── Artifact issue:    open-questions         open/resolved research questions
├── Research issue:        [phase:research]       Research findings
│   └── Artifact issue:    sources.md             sources ledger
├── Clarification issue:   [phase:clarification]  Human answers and assumptions
├── Plan issue:            [phase:plan]           Approved implementation plan
├── Task-graph issue:      [phase:task-graph]     YAML task graph in issue body
│   ├── Task issue:        [phase:implement]      RED/GREEN/REFACTOR slice
│   └── Task issue:        [phase:implement]      RED/GREEN/REFACTOR slice
├── Review issue:          [phase:review]         Combined review findings
├── Verification issue:    [phase:verify]         Acceptance and checks
└── PR issue:              [phase:pr]             PR metadata and follow-ups
```

Use artifact subissues only when a phase has multiple named outputs that need durable status or separate resume context. Otherwise, keep the phase output in the phase issue body.

When GitHub sub-issues are available, link child issues with GitHub's actual sub-issue relationship. A plain `Parent: #N` body reference is only a fallback when the repository cannot create GitHub sub-issues.

### Required sub-issue linking flow

1. Create the parent issue in Phase 1 (or treat the supplied `ISSUE` as the parent).
2. Create each child issue normally, for example:

   ```bash
   gh issue create --title "Exploration — 2026-04-27-add-retry-mechanism" --body-file /tmp/exploration_issue.md
   ```

3. Resolve both node IDs:

   ```bash
   PARENT_NODE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
   CHILD_NODE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
   ```

4. Attach the child issue to the parent with GitHub's GraphQL mutation:

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

5. Treat the GraphQL mutation as the success criterion. Only if the repository cannot use GitHub sub-issues should the workflow fall back to a body reference such as `Parent: #N`.

Nested artifact issues use the same flow: create the artifact issue first, then attach it to the phase issue.

---

## Labels

Apply the following labels consistently. Create them in the repository if they do not exist.

### Role labels

| Label          | Color     | Meaning                                      |
| -------------- | --------- | -------------------------------------------- |
| `agent:parent` | `#0075ca` | Top-level work-item issue                    |
| `agent:phase`  | `#cfd3d7` | A workflow phase issue                       |
| `agent:task`   | `#e4e669` | An individual implementation task issue      |
| `agent:artifact` | `#bfdadc` | A non-task artifact subissue under a phase |

### Phase labels

| Label                 | Color     | Phase      |
| --------------------- | --------- | ---------- |
| `phase:intake`        | `#84b6eb` | Phase 1    |
| `phase:worktree`      | `#84b6eb` | Phase 2    |
| `phase:exploration`   | `#84b6eb` | Phase 3    |
| `phase:research`      | `#84b6eb` | Phase 4    |
| `phase:clarification` | `#84b6eb` | Phase 5    |
| `phase:plan`          | `#0e8a16` | Phase 6    |
| `phase:task-graph`    | `#fbca04` | Phase 7    |
| `phase:implement`     | `#fbca04` | Phase 8    |
| `phase:review`        | `#d93f0b` | Phase 9    |
| `phase:verify`        | `#0075ca` | Phase 10   |
| `phase:pr`            | `#5319e7` | Phase 11   |

### Status labels

| Label         | Color     | Meaning                               |
| ------------- | --------- | ------------------------------------- |
| `needs-human` | `#e11d48` | Waiting for human input               |
| `blocked`     | `#b60205` | Cannot proceed; reason is in the body |
| `parallel`    | `#bfd4f2` | Task can run concurrently with others |
| `sequential`  | `#d4c5f9` | Task must run in order                |

### Quality labels (for follow-up issues)

| Label       | Color     | Meaning                            |
| ----------- | --------- | ---------------------------------- |
| `tech-debt` | `#e4e669` | Tech-debt finding to address later |
| `security`  | `#b60205` | Security finding to address        |

---

## Issue Body Format

Every issue created by the workflow must contain both a human-readable summary and a machine-readable `## Machine Data` block.

### Parent issue template

````markdown
## Summary

<One paragraph describing the work item, source, and expected outcome.>

## Current Phase

<Name the next phase that should run or the blocker that is waiting on input.>

## Acceptance Snapshot

<Short numbered list copied from the intake issue. Keep it compact; the intake issue holds the full artifact.>

## Sub-issues

<!-- Maintained as phases begin -->

- [ ] #N+1 Intake
- [ ] #N+2 Worktree setup
- [ ] #N+3 Codebase exploration
- [ ] #N+4 Online research
- [ ] #N+5 Clarification
- [ ] #N+6 Implementation plan
- [ ] #N+7 TDD task graph
- [ ] #N+8 Review
- [ ] #N+9 Verification
- [ ] #N+10 PR / landing

## Machine Data

```yaml
work_id: <slug>
kind: parent
classification: feature | bug | refactor | spec | chore
status: open
current_phase: intake | worktree | exploration | research | clarification | plan | task-graph | implement | review | verify | pr
source_issue: <number-or-null>
```
````

### Phase issue template

````markdown
## Summary

<One sentence describing what this phase produced.>

## Inputs

- Parent: #N
- Depends on: #<prior phase or artifact issues>

## Deliverable

<The phase artifact itself. Use prose, tables, or fenced code blocks as appropriate. If the phase has secondary durable artifacts, list them here and create artifact subissues for them.>

## Exit Criteria

<Copied from the relevant gate or phase definition in workflow.md / stop-gates.md.>

## Machine Data

```yaml
work_id: <slug>
kind: phase
phase: intake | worktree | exploration | research | clarification | plan | task-graph | review | verify | pr
depends_on: [<issue numbers or artifact keys>]
status: open | closed
```
````

For Phase 7 specifically, keep the task graph YAML in the phase issue body. Do not create a separate `task-graph.yaml` artifact subissue.

### Artifact subissue template

````markdown
## Summary

<Describe the secondary durable artifact.>

## Parent

- Phase issue: #N

## Artifact

<Render the artifact directly in the issue body. For file-like artifacts, preserve the original format in a fenced block, e.g. `csv`, `yaml`, or `markdown`.>

## Machine Data

```yaml
work_id: <slug>
kind: artifact
phase: exploration | research | clarification | review | verify | pr
artifact_name: files.csv | open-questions | sources.md | <custom>
format: csv | yaml | markdown | table | checklist
status: open | closed
```
````

### Implementation task issue template

````markdown
## Summary

<One sentence describing the vertical slice this task issue owns.>

## Task Details

- **Current stage**: red | green | refactor
- **Task ID**: <id from the task graph YAML>
- **Depends on tasks**: <ids>

## Files

<List of files this task may write to.>

## Progress Log

<!-- This issue owns one full vertical slice. Add RED / GREEN / REFACTOR comments here instead of creating stage-specific issues or writing 07-implementation-log.md. -->

## Machine Data

```yaml
work_id: <slug>
kind: task
phase: implement
task_id: <id>
stage: red | green | refactor
parallelizable: true | false
depends_on: [<task ids>]
files: [<paths>]
status: open | closed
```
````

### Plan approval comment template

````markdown
Approved. Proceed with the implementation plan captured in this issue.

## Machine Data

```yaml
work_id: <slug>
kind: approval
phase: plan
status: approved
approved_by: human
approved_at: <ISO8601>
```
````

### Implementation log comment template

````markdown
## Slice Update — <task_id> / <stage>

- **status**: complete | blocked
- **files_changed**: <paths>
- **test_result**: pass | fail
- **notes**: <short explanation>

## Machine Data

```yaml
work_id: <slug>
kind: implementation-log
task_id: <id>
stage: red | green | refactor
status: complete | blocked
updated_at: <ISO8601>
```
````

---

## Issue Lifecycle

| Event | Action |
|-------|--------|
| Phase begins | Create the phase issue, attach it to the correct parent, and apply the phase label |
| Secondary durable artifact appears | Create an artifact subissue under the phase issue |
| `files.csv` ledger is complete | Close the `files.csv` artifact subissue |
| `sources.md` ledger is complete | Close the `sources.md` artifact subissue |
| `open-questions` still has unresolved entries | Keep the `open-questions` artifact issue open across phases 3–5 |
| Every open question is finalized | Close the `open-questions` artifact issue |
| Phase artifact is complete | Close the phase issue |
| Artifact remains active across phases | Keep its subissue open until the tracked status is resolved |
| Blocking question raised | Add `needs-human` to the parent issue |
| Blocking question answered | Remove `needs-human` from the parent issue |
| Implementation slice begins | Create one task issue for the slice and initialize it with `stage: red` |
| Implementation slice progresses | Add RED / GREEN / REFACTOR comments to the same task issue and update its `stage` field in place |
| Implementation slice finishes | Close the task issue |
| High-severity review finding | Fix it before closing the review issue |
| Medium/Low review finding | Open a follow-up issue labelled `security` or `tech-debt` |
| PR opened | Create and then close the `phase:pr` issue; keep the parent issue open |
| PR merged | The PR body closes the parent issue via `Fixes #N` |

---

## When GitHub Issues Are Not Available

This GitHub-native workflow depends on GitHub issues for Phases 1–11. If the repository cannot create issues, stop after any requested Bootstrap work and tell the human that the workflow cannot continue without GitHub issue support.

If GitHub issues are available but the sub-issue mutation is disabled for the repository:

1. Create the child issue normally.
2. Add `Parent: #N` in the child issue body as an explicit fallback marker.
3. Record the failed mutation attempt in the child issue body or a comment.

Do **not** fall back to local per-work-item markdown artifacts.

---

## Relationship to PR

The final PR:

- Title matches the conventional-commits subject.
- Body includes `Fixes #N` for the parent issue.
- Describes follow-up issues created during review.
- Leaves only the top-level parent issue open until merge.

Example PR body:

```markdown
## Summary

Implements retry mechanism with exponential backoff and jitter for the HTTP client.

Fixes #42

## Follow-ups

- #61 Tech-debt: extract retry configuration helper
- #62 Security: review retry logging redaction
```
