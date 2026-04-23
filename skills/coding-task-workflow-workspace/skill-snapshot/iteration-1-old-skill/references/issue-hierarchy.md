# Issue Hierarchy

This document defines how GitHub issues and sub-issues are used to track work items and make the order of operations visible in GitHub.

---

## Hierarchy Structure

Every work item has one **parent issue** and a set of **sub-issues**, one per phase that produces a discrete deliverable.

```
Parent issue: #N  [agent:parent]  <work-item title>
  ├── Sub-issue: [phase:exploration]   Codebase exploration — <slug>
  ├── Sub-issue: [phase:research]      Online research — <slug>
  ├── Sub-issue: [phase:plan]          Implementation plan — <slug>
  ├── Sub-issue: [phase:implement]     Task: <t1 name>
  ├── Sub-issue: [phase:implement]     Task: <t2 name>
  ├── ...
  ├── Sub-issue: [phase:review]        Code / security / tech-debt review — <slug>
  └── Sub-issue: [phase:verify]        Verification and PR — <slug>
```

Sub-issues are linked using GitHub's sub-issue feature (available in repos with the feature enabled) or by referencing the parent issue number in the sub-issue body with "Parent: #N".

---

## Labels

Apply the following labels consistently. Create them in the repository if they do not exist.

### Role labels

| Label          | Color     | Meaning                           |
| -------------- | --------- | --------------------------------- |
| `agent:parent` | `#0075ca` | Top-level work-item issue         |
| `agent:phase`  | `#cfd3d7` | A workflow phase sub-issue        |
| `agent:task`   | `#e4e669` | An individual implementation task |

### Phase labels

| Label               | Color     | Phase    |
| ------------------- | --------- | -------- |
| `phase:exploration` | `#84b6eb` | Phase 3  |
| `phase:research`    | `#84b6eb` | Phase 4  |
| `phase:plan`        | `#0e8a16` | Phase 6  |
| `phase:implement`   | `#fbca04` | Phase 8  |
| `phase:review`      | `#d93f0b` | Phase 9  |
| `phase:verify`      | `#0075ca` | Phase 10 |

### Status labels

| Label         | Color     | Meaning                               |
| ------------- | --------- | ------------------------------------- |
| `needs-human` | `#e11d48` | Waiting for human input               |
| `blocked`     | `#b60205` | Cannot proceed; reason in body        |
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

<One paragraph describing the work item, source (feature request / bug / spec), and expected outcome.>

## Inputs

- Spec / description: `.coding-workflow/work/<slug>/00-intake.md`
- Source issue or spec: <link if applicable>

## Acceptance Criteria

<Copied from 00-intake.md — numbered list.>

## Sub-issues

<!-- Created automatically as each phase begins -->

- [ ] #N+1 Codebase exploration
- [ ] #N+2 Online research
- [ ] #N+3 Implementation plan
- [ ] #N+4 Task: ...
- [ ] #N+M Review
- [ ] #N+M+1 Verification

## Machine Data

```yaml
work_id: <slug>
kind: parent
classification: feature | bug | refactor | spec | chore
artifact_dir: .coding-workflow/work/<slug>/
status: open
```
````

````

### Phase sub-issue template

```markdown
## Summary

<One sentence describing what this phase does.>

## Inputs

- Parent: #N
- artifact: `.coding-workflow/work/<slug>/<artifact-path>`

## Deliverables

- `.coding-workflow/work/<slug>/<output-path>`

## Exit Criteria

<Copied from the gate definition in stop-gates.md for this phase.>

## Dependencies

- Depends on: #<prior sub-issue number>

## Machine Data

```yaml
work_id: <slug>
kind: phase
phase: exploration | research | plan | implement | review | verify
sequence: <number>
parallelizable: true | false
depends_on: [<prior issue numbers>]
artifact: .coding-workflow/work/<slug>/<artifact-path>
status: open
````

````

### Implementation task sub-issue template

```markdown
## Summary

<One sentence describing what this task implements.>

## Task Details

- **Stage**: red | green | refactor
- **Task ID**: <id from task-graph.yaml>
- **Depends on tasks**: <ids>

## Files

<List of files this task may write to.>

## Parent

#N (work-item parent issue)
#N+3 (plan sub-issue)

## Machine Data

```yaml
work_id: <slug>
kind: task
task_id: <id>
stage: red | green | refactor
parallelizable: true | false
depends_on: [<task ids>]
files: [<paths>]
status: open
````

````

---

## Issue Lifecycle

| Event | Action |
|-------|--------|
| Phase begins | Open sub-issue, label with phase label |
| Phase's gate condition is satisfied | Close sub-issue |
| Blocking question raised | Add `needs-human` label to parent issue |
| Blocking question answered | Remove `needs-human` label |
| High-severity review finding | Open separate labelled issue (`security` or `tech-debt`) |
| PR opened | Link PR to parent issue with `Closes #N` |
| PR merged | Close parent issue |
| Follow-up items | Leave as open labelled issues |

---

## When GitHub Issues Are Not Available

If the repository does not use GitHub or issue creation is disabled:

1. Skip all GitHub issue creation steps.
2. Record the work-item hierarchy in `.coding-workflow/work/<slug>/issue-hierarchy.md` using the same structure as the issue templates above.
3. Reference artifact files directly in the PR body instead of issue links.
4. All artifact files still exist and the workflow proceeds identically.


---

## Relationship to PR

The final PR:
- Title matches the parent issue title.
- Body includes `Closes #N` (the parent issue number).
- Body links to `.coding-workflow/work/<slug>/` for artifact access.
- PR description includes a checklist mirroring the sub-issues.

Example PR body:

```markdown
## Summary

Implements retry mechanism with exponential backoff and jitter for the HTTP client.

Closes #42

## artifacts

See `.coding-workflow/work/2026-04-23-add-retry-mechanism/` for full decision history.

## Checklist

- [x] #43 Codebase exploration
- [x] #44 Online research
- [x] #45 Implementation plan (approved)
- [x] #46 Implementation tasks
- [x] #47 Review (0 High findings)
- [x] #48 Verification (all criteria pass)

## Follow-up

- #49 [tech-debt] Extract retry policy into config struct
````
