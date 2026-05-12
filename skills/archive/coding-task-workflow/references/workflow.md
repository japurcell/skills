# Workflow Specification

This document specifies each phase of the `coding-task-workflow` skill. Follow it exactly. Phase 0 writes repo-local override files and makes sure they are available inside the Phase 2 worktree; Phases 1–11 use GitHub issues and comments as the canonical durable workflow record.

---

## Priority rules

These rules override user requests to skip or compress the workflow:

1. If `ISSUE` is supplied, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`, infer `WORK_ITEM` from that issue title/body, and keep that issue as the parent issue for the full workflow.
2. After Bootstrap, do **not** create local per-work-item artifacts under `.coding-workflow/work/<slug>/`. If `.coding-workflow/overrides/` is missing, incomplete, or stale, run or refresh Phase 0 before Phase 2 creates the worktree and verify the committed override tree exists inside that worktree before later phases continue. Persist durable state in GitHub parent issues, phase issues, artifact subissues, and issue comments.
3. Every child issue must be created first, then linked to its parent with the `addSubIssue` GraphQL mutation. When showing shell commands, use the shell-safe literal-ID form from [issue-hierarchy.md](issue-hierarchy.md) rather than GraphQL `$variables` inside the query text. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.
4. After Gate E passes, stop and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session even if the user explicitly asks for it.
5. Phase 8 implementation is always executed by implementation subagents. The primary agent orchestrates dependency order, safe parallelism, issue updates, and final consolidation; it does not directly implement slices itself.
6. Phase 10 verification step 1 is always executed by verification subagents. Use parallel subagents for independent checks when the repo supports concurrent execution, otherwise run verification subagents sequentially.
7. Phase 11 commit messages end with a blank-line-separated `Co-authored-by: NAME <EMAIL>` trailer block using the agent's own known identity.

---

## Phase 0 — Bootstrap _(optional)_

**Trigger**: run this phase when `.coding-workflow/overrides/` does not exist or is missing required files, when the user passes `BOOTSTRAP=only`, when override files are more than 30 days stale, or when the recorded Phase 2 worktree does not contain the committed override tree.

**Objective**: inspect the target repository and produce or update committed repo-local override files that future phases will read from the Phase 2 worktree.

**Inputs**: target repository root.

**Steps**:

1. List files at repo root and in `docs/`, `.github/`, `.github/workflows/`.
2. Read each signal file that exists (see [bootstrap.md](bootstrap.md) for the full signal list and inference rules).
3. For each override file: if it does not exist, create it from the template; if it exists, merge new findings with existing content, preserving any manually written content.
4. Commit override files with message `chore: bootstrap coding-workflow overrides` so the next Phase 2 worktree creation inherits them as tracked files.
5. If the work item already has a Phase 2 worktree, refresh that worktree so `.coding-workflow/overrides/` in the worktree matches the committed override set before later phases continue.

**Outputs**: committed `.coding-workflow/overrides/*.yaml`, committed `.coding-workflow/overrides/*.md`.

**Gate**: none — bootstrap is a standalone phase.

**Parallelism**: steps 1–2 may run in parallel subagents scanning different areas.

---

## Phase 1 — Intake

**Objective**: capture the work item in GitHub before any code is touched.

**Inputs**: `WORK_ITEM` text or file path; optional `ISSUE` number.

**Steps**:

1. If `ISSUE` is provided, fetch the GitHub issue with `gh issue view <ISSUE> --json number,title,body,url,id` and infer `WORK_ITEM` from the issue title/body before classification. Treat separately supplied `WORK_ITEM` text as supplemental context only.
2. If `WORK_ITEM` is a file path, read the file.
3. Classify the work item as `feature | bug | refactor | spec | chore`.
4. Assign a deterministic slug: `YYYY-MM-DD-<kebab-title>` (max 50 chars).
5. If `ISSUE` is provided, treat that issue as the lightweight parent issue. Refresh its body so it matches the parent template in [issue-hierarchy.md](issue-hierarchy.md), preserving any useful existing summary text. If `ISSUE` is not provided, create a new parent issue labelled `agent:parent`.
6. Create a separate GitHub child issue labelled `agent:phase` and `phase:intake`. Its body is the structured intake artifact based on [templates/intake.md](templates/intake.md).
7. Attach the intake issue to the parent issue with `addSubIssue`.
8. Close the intake issue once the body contains the accepted summary, classification, acceptance criteria, known constraints, references, and `## Machine Data`.

**Outputs**: lightweight parent issue, closed intake child issue.

**Gate**: none — intake always runs.

**Parallelism**: none.

---

## Phase 2 — Worktree Setup

**Objective**: isolate the work in a dedicated git worktree so the main branch is never touched until the PR is ready.

**Inputs**: `WORKTREE` path (default: `../worktrees/<slug>`), `BRANCH` name (default: `feat/<slug>` or `fix/<slug>`), committed override files from Phase 0.

**Steps**:

1. If `.coding-workflow/overrides/` is missing, incomplete, or stale in the source checkout, run or refresh Phase 0 first and commit the override update before creating the worktree.
2. Run `git worktree add <WORKTREE> -b <BRANCH>`.
3. Confirm the worktree was created successfully and that `<WORKTREE>/.coding-workflow/overrides/` exists with the expected files.
4. If the override tree is missing in the new worktree, stop and repair bootstrap/worktree sync before later phases continue; do not defer this to Phase 8.
5. Create a GitHub child issue labelled `agent:phase` and `phase:worktree`. Record the worktree path, branch name, base commit SHA, timestamp, and override-tree verification result in the issue body.
6. Attach the worktree issue to the parent issue with `addSubIssue`.
7. Close the worktree issue once the worktree details are complete.

**Outputs**: closed worktree child issue, git worktree with `.coding-workflow/overrides/` present.

**Gate**: none — worktree setup always runs immediately after intake.

**Parallelism**: none.

---

## Phase 3 — Codebase Exploration

**Objective**: understand the relevant parts of the codebase deeply enough to produce a well-grounded implementation plan.

**Inputs**: intake issue, worktree issue, override files.

**Track selection** (choose one before launching agents):

| Track        | Criteria                                           | Agents   |
| ------------ | -------------------------------------------------- | -------- |
| **Light**    | Well-bounded, familiar area, low ambiguity         | 1 agent  |
| **Standard** | Touches several files, some design ambiguity       | 2 agents |
| **Deep**     | Cross-cutting, high ambiguity, unfamiliar codebase | 3 agents |

**Steps**:

1. Select track based on work-item classification and scope.
2. Launch the selected number of code-explorer subagents in parallel. Each agent must cover a different angle:
   - Agent A: similar existing features and their patterns.
   - Agent B: architecture — module boundaries, dependency graph, data flow.
   - Agent C _(Deep only)_: test infrastructure, build system, integration points.
3. Each agent returns: a list of 5–10 key files with reasons, observed patterns, and open questions.
4. Read all files surfaced by agents (do not rely on summaries alone).
5. Create a GitHub child issue labelled `agent:phase` and `phase:exploration`. Its body uses [templates/exploration-summary.md](templates/exploration-summary.md) for the consolidated exploration summary.
6. Create a `files.csv` artifact subissue under the exploration issue. Store the file list in a fenced `csv` block so other agents can resume from GitHub alone.
7. Close the `files.csv` artifact subissue as soon as the file ledger is complete.
8. Create an `open-questions` artifact subissue under the exploration issue. Store each question with `id`, `question`, `status: open`, `resolved_by`, and `answer`.
9. Close the exploration phase issue once the summary is complete. Leave the `open-questions` artifact issue open until every question is resolved or explicitly marked `needs-human`.

**Outputs**: closed exploration phase issue, closed `files.csv` artifact subissue, open `open-questions` artifact subissue.

**Gate A**: the exploration phase issue is closed, the `files.csv` artifact issue is closed, and the `open-questions` artifact issue exists before Phase 4 begins.

**Parallelism**: explorer agents run in parallel; file reading happens after all agents complete.

---

## Phase 4 — Online Research

**Objective**: answer open questions and verify up-to-date best practices through targeted research.

**Inputs**: `open-questions` artifact issue, override files.

**Steps**:

1. Read the open-questions artifact issue. Group questions by domain (framework docs, security standards, algorithm choices, and so on).
2. Launch 1–3 research subagents in parallel, each assigned a distinct group of questions.
3. Each research agent must return: question, source URL, date checked, finding, confidence, applicability to the repo, and decision.
4. Create a GitHub child issue labelled `agent:phase` and `phase:research`. Its body uses [templates/research-findings.md](templates/research-findings.md).
5. Create a `sources.md` artifact subissue under the research issue. Store the source ledger as a Markdown table.
6. Close the `sources.md` artifact subissue as soon as the source ledger is complete.
7. Update the `open-questions` artifact issue: mark each question `resolved` or `needs-human`, and include the answer or escalation note.
8. If the `open-questions` artifact issue has no question left at `status: open`, close it here; otherwise leave it open for Phase 5.
9. Close the research issue once the findings and sources are recorded.

**Outputs**: closed research phase issue, closed `sources.md` artifact subissue, updated `open-questions` artifact issue (closed here when research fully resolves it; otherwise left open for clarification).

**Gate B**: the research phase issue is closed, the `sources.md` artifact issue is closed, and the `open-questions` artifact issue has no question left at `status: open` before Phase 5 begins.

**Parallelism**: research agents run in parallel.

---

## Phase 5 — Clarification

**Objective**: resolve any blocking questions that remain after exploration and research, with minimum burden on the human.

**Inputs**: updated `open-questions` artifact issue, research issue.

**Steps**:

1. Review all questions marked `needs-human`.
2. Attempt to resolve each using artifacts already available. Update the `open-questions` issue when a question can now be marked `resolved`.
3. Classify remaining questions as `blocking: true` or `blocking: false`.
4. Create a GitHub child issue labelled `agent:phase` and `phase:clarification`.
5. For `blocking: false` questions, record the assumption in the clarification issue and update the question entry accordingly.
6. For `blocking: true` questions, batch them into the smallest prompt that will unblock the work. Add `needs-human` to the parent issue while waiting.
7. Record human answers or assumptions in the clarification issue body using [templates/clarifications.md](templates/clarifications.md). Update the `open-questions` issue to reflect the final status for each question.
8. Close the `open-questions` artifact issue once every entry is either resolved or explicitly finalized as `needs-human`; do not leave it open after clarification completes.
9. Remove `needs-human` from the parent issue once every blocking question is answered.
10. Close the clarification issue once no entry remains with `blocking: true` and `status: unanswered`.

**Outputs**: closed clarification phase issue, closed `open-questions` artifact issue.

**Gate C**: the clarification issue is closed, the `open-questions` artifact issue is closed, and no entry contains both `blocking: true` and `status: unanswered` before Phase 6 begins.

**Parallelism**: none.

---

## Phase 6 — Plan

**Objective**: produce a written, approved implementation plan that Phase 8 can execute without further design work.

**Inputs**: intake issue, exploration issue, `files.csv` artifact subissue, research issue, clarification issue, relevant source files.

**Steps**:

1. Re-read the intake issue (acceptance criteria), exploration summary, research findings, and clarifications.
2. Read the key source files from the `files.csv` artifact issue that are directly affected by the work item.
3. Create a GitHub child issue labelled `agent:phase` and `phase:plan`. Its body uses [templates/plan.md](templates/plan.md) and includes goal / non-goals, approach and rationale, alternatives, file-by-file implementation map, and verification guidance.
4. Present a concise plan summary to the human. Gate on explicit approval.
5. Record approval as an explicit comment on the plan issue.
6. Close the plan issue immediately after approval. If the human requests changes, edit the issue body and repeat the approval step.

**Outputs**: closed plan phase issue with an explicit approval comment.

**Gate D**: the plan issue is closed and contains an explicit approval comment before Phase 7 begins.

**Parallelism**: none.

---

## Phase 7 — TDD Task Graph

**Objective**: decompose the approved plan into a DAG of TDD vertical slices with explicit sequencing.

**Inputs**: plan issue.

**Steps**:

1. Identify distinct behaviours to implement. Each behaviour becomes one vertical slice: RED → GREEN → REFACTOR.
2. For each slice, determine: `id`, `name`, `depends_on`, `parallelizable`, and `files`. Each slice starts at `stage: red` and advances on the same task issue as work progresses.
3. **Do not write all RED slices before any GREEN slices.** Each vertical slice is independent.
4. Create a GitHub child issue labelled `agent:phase` and `phase:task-graph`. Put the task graph in a fenced `yaml` block using [templates/task-graph.yaml](templates/task-graph.yaml) as the content shape.
5. Create one GitHub child issue per vertical slice and attach it under the Phase 7 task-graph issue. Label each `agent:task`, `phase:implement`, plus `parallel` or `sequential` as appropriate. Initialize each task issue with `stage: red`; RED, GREEN, and REFACTOR progress stays on that same issue as comments rather than separate issues.
6. Close the task-graph issue once the YAML and implementation task issues are complete.
7. After Gate E is satisfied, stop the current session and hand off a resume command: `coding-task-workflow RESUME=<slug>`. Do not proceed to Phase 8 in the same invocation.

**Outputs**: closed task-graph phase issue, open implementation task issues.

**Gate E**: the task-graph issue is closed, at least one implementation task issue has `stage: red`, and every task issue records an explicit dependency list before Phase 8 begins.

**Parallelism**: none for authoring the graph; execution in Phase 8 follows the graph's parallelism rules.

---

## Phase 8 — Implementation

**Objective**: execute the task graph using a strict TDD red→green→refactor loop.

**Inputs**: task-graph issue, Phase 2 worktree issue, open implementation task issues, relevant source files, `.coding-workflow/overrides/` inside the worktree, fresh session resumed after the Phase 7 hard stop.

**Steps**:

1. Resolve `RESUME=<slug>` by loading the parent issue and descendant phase/task issues for that `work_id`, including the Phase 2 worktree issue so you recover the recorded worktree path and branch. Do not rely on local phase files.
2. Enter the recorded worktree and confirm `.coding-workflow/overrides/` exists there. If it is missing, incomplete, or stale, return to Phase 0 / Phase 2 maintenance to refresh bootstrap overrides and sync them into the worktree before delegating implementation.
3. Process implementation task issues in dependency order, but delegate every implementation task issue to a subagent. Run tasks labelled `parallel` concurrently when their dependencies are satisfied and they do not overlap on files. Run sequential tasks one at a time, still through a subagent.
4. For each task issue, launch an implementation subagent with the task issue, recorded worktree path, plan context, relevant files, override files, allowed write paths, current stage, and exact tests to run. The subagent performs the full RED → GREEN → REFACTOR slice:
    a. **RED**: write a failing test that captures the behaviour. Run it and confirm it fails for the expected reason. Record the result as a comment on the task issue while the issue remains at `stage: red`.
    b. **GREEN**: update the same task issue to `stage: green`, write the minimal code to make the test pass, run it, and record the result as a comment on that issue.
    c. **REFACTOR**: update the same task issue to `stage: refactor`, clean up if needed, rerun the relevant tests, and record the outcome as another comment on that issue.
5. After each subagent finishes, inspect its changed files and test output before updating or closing the task issue. Do not rely on the subagent summary alone.
6. Never add untested code paths. If a useful branch is not yet covered by a test, do not add it.
7. Close each task issue when its slice is complete. The task issue comments replace `07-implementation-log.md`, and the issue body remains the durable record of the slice's current/final stage.

**Outputs**: modified source files and tests, implementation task issue comments, updated task issue stage fields, closed implementation task issues.

**Gate**: none — the task graph itself is the gate structure.

**Parallelism**: implementation always runs in subagents. Parallelizable task groups run concurrently when dependencies are satisfied and write paths do not overlap; sequential tasks run in order, one subagent at a time.

Strict TDD rules: see [../tdd/SKILL.md](../tdd/SKILL.md).

---

## Phase 9 — Review

**Objective**: catch defects, security issues, and tech debt before the code is committed.

**Inputs**: changed source files and tests, plan issue, task-graph issue, implementation task issue comments.

**Steps**:

1. Determine the scope of changed files.
2. Partition files into non-overlapping groups by module or directory.
3. Launch three specialised review subagents in parallel:
   - **Code review**: conventions, logic, clarity, DRY, dead code.
   - **Security review**: OWASP Top 10, injection, auth, secrets, unsafe defaults, data exposure.
   - **Tech-debt review**: duplication, coupling, complexity, missing abstractions, test gaps.
4. Create a GitHub child issue labelled `agent:phase` and `phase:review`. Record the combined findings in that issue body, using repeated sections based on [templates/review.md](templates/review.md).
5. Classify each finding as `High | Medium | Low | Info`.
6. Fix all `High` findings immediately and update the review issue before closing it.
7. Record `Medium` and `Low` findings as follow-up GitHub issues labelled `tech-debt` or `security`.
8. Close the review issue once no `High` finding remains open.

**Outputs**: closed review phase issue, follow-up issues for deferred findings.

**Gate**: none — review always runs after implementation.

**Parallelism**: three review agents run concurrently.

---

## Phase 10 — Verification

**Objective**: confirm the implementation satisfies every acceptance criterion and all automated checks pass.

**Inputs**: intake issue (acceptance criteria), plan issue (verification guidance), `.coding-workflow/overrides/test-commands.yaml` if available, review issue.

**Steps**:

1. Launch verification subagents to run the test suite, linter, type-checker, and build commands from `.coding-workflow/overrides/test-commands.yaml`. If the file does not exist, use the commands inferred during bootstrap or from repo scripts. Run independent checks in parallel subagents when the repo supports concurrent execution; otherwise run one verification subagent at a time. Each subagent reports command, exit code, output summary, and any failure details.
2. For each acceptance criterion captured in the intake issue, record `pass` or `fail` with evidence.
3. Verify that no `High` severity issue remains open from Phase 9 review.
4. Create a GitHub child issue labelled `agent:phase` and `phase:verify`. Its body uses [templates/verification.md](templates/verification.md).
5. If any criterion fails: return to Phase 8 to fix the failing behaviour, then re-run verification.
6. Close the verification issue only when every acceptance criterion passes and every required automated check exits 0.

**Outputs**: closed verification phase issue.

**Gate F**: the verification issue is closed, every acceptance criterion is marked `pass`, all automated checks exit 0, and no `High` review finding remains open before Phase 11 begins.

**Parallelism**: Phase 10 step 1 always runs in verification subagents. Independent checks may run in parallel subagents when safe; dependent or resource-conflicting checks run sequentially through subagents.

---

## Phase 11 — Commit / Push / PR

**Objective**: land the verified work into a PR while leaving only the top-level parent issue open.

**Inputs**: all changed files, verification issue, parent GitHub issue number.

**Steps**:

1. Stage all changed files.
2. Write a conventional-commits message: `<type>(<scope>): <subject>`. Include a body linking to the work-item slug and parent issue, then append a `Co-authored-by: NAME <EMAIL>` trailer block separated from that body by a blank line using your own known co-author identity. For GitHub Copilot CLI, use `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
3. Push the branch to the remote.
4. Open a pull request:
   - Title: conventional-commits subject.
   - Body: `Fixes #<parent issue number>`, summary of changes, and any open follow-up items.
5. Create a GitHub child issue labelled `agent:phase` and `phase:pr`. Record the PR number, URL, commit subject, and follow-up issues in the issue body.
6. Close the Phase 11 issue immediately after the PR is opened.
7. Ensure every completed child issue is closed. Leave only the top-level parent issue open so the PR can close it on merge.

**Outputs**: closed Phase 11 PR issue, PR, closed child issues.

**Gate**: none after Gate F.

**Parallelism**: none.
