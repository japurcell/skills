---
name: coding-task-workflow
description: Deterministic workflow for non-trivial coding work from ticket/spec to PR. Use whenever implementing a feature, bug fix, refactor, or requirements doc that needs bootstrap, exploration, research, TDD task graph, review, verification, and GitHub issue/PR tracking.
---

# Coding Task Workflow

Use this skill to take non-trivial coding work from intake to PR with durable artifacts in GitHub and repo-local Bootstrap overrides.

## Reference index

Read only the needed reference:

| When | Read |
| --- | --- |
| Start or phase mechanics | [references/workflow.md](references/workflow.md) |
| Crossing a gate, resuming, or unclear gate state | [references/stop-gates.md](references/stop-gates.md) |
| Creating/attaching sub-issues or writing the PR | [references/issue-hierarchy.md](references/issue-hierarchy.md) |
| Phase 0 or stale/missing overrides | [references/bootstrap.md](references/bootstrap.md) |
| Before launching subagents | [references/delegation-rules.md](references/delegation-rules.md) |
| Writing/updating artifacts | [references/artifact-schema.md](references/artifact-schema.md) and [references/templates/](references/templates/) |

Follow references exactly. Do not duplicate them in responses.

## Non-negotiable rules

These rules override user requests to skip or compress the workflow:

1. If `ISSUE` is provided, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`. The GitHub issue title/body is the authoritative `WORK_ITEM`, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.
2. Phase 0 is the only phase that writes durable repo-local workflow artifacts. For Phases 1–11, GitHub parent issues, phase issues, artifact subissues, and issue comments are the canonical workflow record; do not create `.coding-workflow/work/<slug>/...` artifacts.
3. Every child issue is created first, then linked to the appropriate parent issue by resolving parent/child node IDs and calling `gh api graphql ... addSubIssue`. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.
4. After Gate E passes, hard-stop the session and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session. Resume from a fresh session; Phase 8 is the next phase after the resume. Do not restart earlier phases unless the GitHub artifact state says they are incomplete.
5. Phase 8 implementation is always performed by implementation subagents. The primary agent orchestrates dependency order, parallel groups, file-overlap checks, and GitHub comments; it does not directly write the implementation slice itself.
6. Phase 10 verification step 1 is always performed by verification subagents. Split independent checks across parallel subagents when the repo supports concurrent execution; otherwise run one verification subagent at a time.
7. Phase 11 commit messages use a conventional-commits subject, a body that references the work-item slug and parent issue, then a blank-line-separated trailer block. For GitHub Copilot CLI, include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.

## Workflow-rule answers

Lead with the governing rule; add only command shape and fallback details.

| User asks about | Answer |
| --- | --- |
| Phase 7 resume handoff | `Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with coding-task-workflow RESUME=<slug>. Phase 8 is the next phase after the resume.` |
| Intake authority | `The GitHub issue title/body is the authoritative WORK_ITEM, and the supplied issue remains the Phase 1 parent issue; do not create a new parent issue.` |
| Sub-issue linking | `Create the child issue first, resolve both node IDs, then attach it with gh api graphql ... addSubIssue. Parent: #N is fallback-only when GitHub sub-issues are unavailable.` |
| Workflow record | `Phase 0 keeps repo-local overrides, but Phases 1–11 persist durable state in GitHub issues and comments instead of local per-work-item markdown files.` |

Do not invent issue-template prose, sample issue bodies, or extra artifact structure unless explicitly asked.

## Invocation

```text
coding-task-workflow [WORK_ITEM] [ISSUE=number] [WORKTREE=path] [BRANCH=name] [BOOTSTRAP=only|RESUME=slug]
```

Arguments are optional; gather missing values interactively:

- `WORK_ITEM`: feature description, bug report, spec text/path, or text inferred from `ISSUE`
- `ISSUE`: GitHub issue number to track this work item
- `WORKTREE`: default `../worktrees/<slug>`
- `BRANCH`: default `feat/<slug>` or `fix/<slug>`
- `BOOTSTRAP`: set to `only` to run only Phase 0
- `RESUME`: work-item slug to resume

Routing precedence:

1. `BOOTSTRAP=only`: run only Phase 0.
2. `RESUME=<slug>`: rebuild state from the GitHub issue hierarchy for that `work_id` and continue from the next incomplete phase.
3. Otherwise start at Phase 1. If `ISSUE` is present, fetch it before doing anything else.
4. Do not improvise phase order or skip a gate unless the canonical references explicitly allow it.

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
| 8   | **Implementation**         | subagents; parallel groups when safe | –    |
| 9   | **Review**                 | parallel              | –    |
| 10  | **Verification**           | subagents; parallel checks when safe | F    |
| 11  | **Commit / Push / PR**     | –                     | –    |
