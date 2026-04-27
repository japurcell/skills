---
name: coding-task-workflow
description: Deterministic workflow for non-trivial coding work. Use this whenever the user wants to implement a feature, bug fix, refactor, or spec from a ticket, bug report, or requirements doc and wants a structured multi-phase flow with bootstrap, parallel exploration and research, TDD execution, review, verification, and issue/PR tracking.
---

# Coding Task Workflow

Use this skill to take non-trivial coding work from intake to PR with durable artifacts in the target repo.

## Read only what you need

- Read [references/workflow.md](references/workflow.md) at the start for the canonical phase order, required outputs, and phase-by-phase steps.
- Read [references/stop-gates.md](references/stop-gates.md) before crossing a gate, when resuming partial work, or when a gate condition is unclear.
- Read [references/issue-hierarchy.md](references/issue-hierarchy.md) only when creating parent/child issues, attaching sub-issues, or writing the PR.
- Read [references/bootstrap.md](references/bootstrap.md) only for Phase 0 or stale/missing overrides.
- Read [references/delegation-rules.md](references/delegation-rules.md) only before launching subagents.
- Read [references/artifact-schema.md](references/artifact-schema.md) and [references/templates/](references/templates/) only when writing or updating artifacts.

Do not duplicate those references in your response. Follow them exactly and keep the working context lean.

## Non-negotiable rules

These rules override user requests to skip or compress the workflow:

1. If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.
2. Every child issue is created first, then linked to the Phase 1 parent issue by resolving parent/child node IDs and calling `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.
3. After Gate E passes, hard-stop the session and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session. Resume from a fresh session; Phase 8 is the next phase after the resume. Do not restart earlier phases unless the saved artifacts say they are incomplete.
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
- Do not improvise phase order or skip a gate unless the canonical references explicitly allow it.

## Phase map

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

For phase mechanics, artifact paths, issue sequencing, delegation rules, and gate criteria, follow the reference docs exactly rather than restating them.
