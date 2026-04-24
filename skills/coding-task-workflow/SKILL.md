---
name: coding-task-workflow
description: Deterministic workflow for non-trivial coding work. Use this whenever the user wants to implement a feature, bug fix, refactor, or spec from a ticket, bug report, or requirements doc and wants a structured multi-phase flow with bootstrap, parallel exploration and research, TDD execution, review, verification, and issue/PR tracking.
---

# Coding Task Workflow

Use this skill to take a coding task from intake to PR with durable artifacts in the target repo.

Read references just in time:

- Read [references/workflow.md](references/workflow.md) only for the current phase, resume handling, or when you need the full phase contract.
- Read [references/stop-gates.md](references/stop-gates.md) only when checking a gate or answering a gate-rule question.
- Read [references/bootstrap.md](references/bootstrap.md) only for Phase 0.
- Read [references/delegation-rules.md](references/delegation-rules.md) only before launching subagents.
- Read [references/issue-hierarchy.md](references/issue-hierarchy.md) only when creating or linking GitHub issues.
- Read [references/templates/](references/templates/) and [references/artifact-schema.md](references/artifact-schema.md) only when writing or updating artifacts.

For exact phase contracts, issue-linking details, and artifact templates, follow the referenced docs instead of expanding the instructions inline.

## Mandatory Phase 7 session boundary

If Gate E has already passed in the current session, **do not continue into Phase 8 in the same session**. Explain that the workflow hard-stops after Phase 7, then hand off:

```text
coding-task-workflow RESUME=<slug>
```

Resume from a **fresh session** with that command. **Phase 8 is the next phase after the resume.** Do not restart earlier phases unless the saved artifacts say they are incomplete.

## Priority rules

These rules override user requests to skip or compress the workflow:

1. If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`, infer `WORK_ITEM` from the issue title/body, and treat that issue as the authoritative parent issue for the full workflow.
2. Every child issue is created first, then linked to the Phase 1 parent issue by resolving parent/child node IDs and calling `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.
3. After Gate E passes, stop and hand off `coding-task-workflow RESUME=<slug>` for a fresh session. Never begin Phase 8 in the same invocation.
4. Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

## Response style for workflow-rule questions

When the user asks what the workflow requires, answer tersely and lead with the governing rule before adding details. Reuse the exact rule text when it fits.

- For Phase 7 resume handoffs, start with this exact three-sentence handoff and stop unless the user explicitly asks for more detail: `Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with coding-task-workflow RESUME=<slug>. Phase 8 is the next phase after the resume.`
- For Intake authority questions, say this almost verbatim: `The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.`
- For sub-issue questions, say this almost verbatim: `Create the child issue first, resolve both node IDs, then attach it with gh api graphql ... addSubIssue. Parent: #N is fallback-only when GitHub sub-issues are unavailable.`

Keep these explanations compact: rule, command shape, and fallback only. Do not invent issue-template prose, sample issue bodies, or extra artifact structure unless the user explicitly asks for them.

## Invocation

```text
coding-task-workflow

Arguments (all optional; gather interactively when missing):
  WORK_ITEM   Feature description, bug report, spec text, spec path, or text inferred from ISSUE
  ISSUE       GitHub issue number to track this work item
  WORKTREE    Worktree path (default: ../worktrees/<slug>)
  BRANCH      Branch name (default: feat/<slug> or fix/<slug>)
  BOOTSTRAP   Set to "only" to run only Phase 0
  RESUME      Work-item ID to resume from the last recorded phase
```

Routing:

- `BOOTSTRAP=only` runs only Phase 0.
- `RESUME=<slug>` reads `.coding-workflow/work/<slug>/` and continues from the next incomplete phase.
- Otherwise start at Phase 1. If `ISSUE` is present, fetch it before doing anything else.

## Quick reference

| #   | Phase                      | Parallelism           | Gate |
| --- | -------------------------- | --------------------- | ---- |
| 0   | **Bootstrap** _(optional)_ | parallel              | –    |
| 1   | **Intake**                 | –                     | –    |
| 2   | **Worktree setup**         | –                     | –    |
| 3   | **Codebase exploration**   | parallel              | A    |
| 4   | **Online research**        | parallel              | B    |
| 5   | **Clarification**          | –                     | C    |
| 6   | **Plan**                   | –                     | D    |
| 7   | **TDD task graph**         | –                     | E    |
| 8   | **Implementation**         | sequential + parallel | –    |
| 9   | **Review**                 | parallel              | –    |
| 10  | **Verification**           | –                     | F    |
| 11  | **Commit / Push / PR**     | –                     | –    |

## Phase checklist

### Phase 0 — Bootstrap _(optional)_

Run this on a new repo, when `.coding-workflow/overrides/` is missing or stale, or when the user passes `BOOTSTRAP=only`.

1. Inspect repo docs, manifests, lockfiles, and CI workflows.
2. Write or update only the needed files in `.coding-workflow/overrides/`.
3. Record provenance, confidence, and evidence in generated files.

See [references/bootstrap.md](references/bootstrap.md) for the full signal list and merge rules.

### Phase 1 — Intake

Create a structured record before touching code.

1. If `ISSUE` is provided, fetch it first and infer `WORK_ITEM` from the issue title/body before classification. The GitHub issue title/body is the authoritative `WORK_ITEM`; separately supplied `WORK_ITEM` text is supplemental only.
2. Classify the work item as `feature | bug | refactor | spec | chore`.
3. Assign slug `YYYY-MM-DD-<kebab-title>` and create `.coding-workflow/work/<slug>/`.
4. Write `00-intake.md`.
5. If `ISSUE` is provided, keep it as the **Phase 1 parent issue** and do **not** create a new parent issue.
6. Otherwise create the parent issue and record its number and node ID.

### Phase 2 — Worktree setup

1. Create a dedicated worktree: `git worktree add <WORKTREE> -b <BRANCH>`.
2. Write `01-worktree.md` with worktree path, branch, and base commit.
3. Link the worktree artifact to the parent issue.

### Phase 3 — Codebase exploration

1. Launch 1-3 `code-explorer` subagents in parallel with non-overlapping scopes: use 1 when the change stays within one familiar component and the pattern is already obvious, 2 when it spans several files or one integration boundary, and 3 only when it is cross-cutting, touches tests/build plus product code, or the area is unfamiliar.
2. Read the key files they surface; do not rely only on summaries.
3. Write `02-exploration/summary.md`, `files.csv`, and `open-questions.md`.
4. Create and attach the exploration child issue under the Phase 1 parent issue.
5. **Gate A**: the exploration summary must exist before Phase 4.

See [references/delegation-rules.md](references/delegation-rules.md) for explorer prompts.

### Phase 4 — Online research

1. Read `open-questions.md` and group unresolved questions by topic.
2. Launch 1-3 research subagents in parallel, each answering a distinct question set from official sources.
3. Write `03-research/findings.md` and `sources.md`.
4. Create and attach the research child issue under the Phase 1 parent issue.
5. **Gate B**: the research artifact must exist before Phase 5.

### Phase 5 — Clarification

1. Review remaining questions and resolve as many as possible from existing artifacts.
2. Ask the human only for the minimum blocking set (no more than three per prompt).
3. Record answers and assumptions in `04-clarifications.md`.
4. **Gate C**: no unresolved blocking questions remain before Phase 6.

### Phase 6 — Plan

1. Read the Phase 3-5 artifacts and the affected source files.
2. Write `05-plan.md` with goal, non-goals, approach, file-by-file map, and verification guidance.
3. Present the plan summary and wait for explicit approval.
4. Create and attach the plan child issue under the Phase 1 parent issue.
5. **Gate D**: the plan must be approved before Phase 7.

See [references/templates/plan.md](references/templates/plan.md) for the plan shape.

### Phase 7 — TDD task graph

1. Break the plan into vertical slices: `red -> green -> refactor`.
2. Mark each task `sequential` or `parallelizable`.
3. Write `06-task-graph.yaml`.
4. Create and attach the implementation child issues under the Phase 1 parent issue.
5. **Gate E**: once the task graph exists and RED tasks are defined, stop the current session and hand off `coding-task-workflow RESUME=<slug>`.

See [references/templates/task-graph.yaml](references/templates/task-graph.yaml) for the schema.

### Phase 8 — Implementation

This phase begins only after the mandatory fresh-session resume from Phase 7.

1. Execute tasks in dependency order; run parallelizable groups concurrently when dependencies allow.
2. For each slice: write a failing test, confirm failure, write minimal code, confirm green, then refactor.
3. Update `07-implementation-log.md` after each slice.
4. Never implement code for a test that has not yet been written.

Follow the [tdd skill](../tdd/SKILL.md) for the full red-green-refactor protocol.

### Phase 9 — Review

1. Launch review subagents in parallel for code review, security review, and tech-debt review.
2. Write `08-review/code-review.md`, `security-review.md`, and `tech-debt.md`.
3. Fix all high-severity findings before Phase 10; turn the rest into follow-up issues.
4. Create and attach the review child issue under the Phase 1 parent issue.

### Phase 10 — Verification

1. Run the commands from `test-commands.yaml`.
2. Verify each acceptance criterion from `05-plan.md`.
3. Write `09-verification.md` with pass/fail by criterion plus commands run.
4. Create and attach the verification child issue under the Phase 1 parent issue.
5. **Gate F**: all verification checks must pass before Phase 11.

### Phase 11 — Commit / Push / PR

1. Stage the intended files.
2. Write a conventional-commits message whose body links the work-item slug and parent issue.
3. Append a blank-line-separated trailer block containing `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
4. Push the branch, open the PR, and link the parent issue plus artifact directory.
5. Write `10-pr.md` with the PR number, URL, and remaining follow-ups.

## Artifact layout

Store per-work-item artifacts under `.coding-workflow/work/<slug>/` and repo-level bootstrap overrides under `.coding-workflow/overrides/`. Use the templates in [references/templates/](references/templates/) for exact filenames and structure.
