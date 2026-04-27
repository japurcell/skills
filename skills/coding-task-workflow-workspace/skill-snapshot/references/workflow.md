# Workflow Specification

This document specifies each phase of the `coding-task-workflow` skill in detail. Follow this document exactly; do not improvise phase ordering or skip phases without satisfying the stated gate.

---

## Priority rules

These rules override user requests to skip or compress the workflow:

1. If `ISSUE` is supplied, fetch it before classification with `gh issue view <ISSUE> --json number,title,body,url,id`, infer `WORK_ITEM` from that issue title/body, and keep that issue as the parent issue for the full workflow.
2. Every child issue must be created first, then linked to the Phase 1 parent issue with the `addSubIssue` GraphQL mutation. `Parent: #N` is fallback-only when GitHub sub-issues are unavailable.
3. After Gate E passes, stop and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session even if the user explicitly asks for it.
4. Phase 11 commit messages end with a blank-line-separated `Co-authored-by: NAME <EMAIL>` trailer block using the agent's own known identity.

---

## Phase 0 — Bootstrap _(optional)_

**Trigger**: run this phase when `.coding-workflow/overrides/` does not exist or is missing required files, when the user passes `BOOTSTRAP=only`, or when override files are more than 30 days stale.

**Objective**: inspect the target repository and produce or update repo-local override files that future phases will read.

**Inputs**: target repository root.

**Steps**:

1. List files at repo root and in `docs/`, `.github/`, `.github/workflows/`.
2. Read each signal file that exists (see [bootstrap.md](bootstrap.md) for the full signal list and inference rules).
3. For each override file: if it does not exist, create it from the template; if it exists, merge new findings with existing content, preserving any manually written content.
4. Commit override files with message `chore: bootstrap coding-workflow overrides`.

**Outputs**: `.coding-workflow/overrides/*.yaml`, `.coding-workflow/overrides/*.md`.

**Gate**: none — bootstrap is a standalone phase.

**Parallelism**: steps 1–2 may run in parallel subagents scanning different areas.

---

## Phase 1 — Intake

**Objective**: create a structured, machine-readable record of the work item before any code is touched.

**Inputs**: `WORK_ITEM` text or file path; optional `ISSUE` number.

**Steps**:

1. If `ISSUE` is provided, fetch the GitHub issue with `gh issue view <ISSUE> --json number,title,body,url,id` and infer `WORK_ITEM` from the issue title/body before classification. Treat separately supplied `WORK_ITEM` text as supplemental context only, and do not let it override the issue.
2. If `WORK_ITEM` is a file path, read the file.
3. Classify the work item as: `feature | bug | refactor | spec | chore`.
4. Assign a deterministic slug: `YYYY-MM-DD-<kebab-title>` (max 50 chars).
5. Create `.coding-workflow/work/<slug>/`.
6. Write `00-intake.md` using the [intake template](templates/intake.md). Include: summary, classification, acceptance criteria (initial draft), known constraints, and links to any referenced issues or specs.
7. If `ISSUE` is provided, treat that issue as the Phase 1 parent issue, record its number and node ID, add a comment linking to `00-intake.md`, and do not create another parent issue.
8. If `ISSUE` is not provided, create a GitHub parent issue with label `agent:parent`, capture its node ID, and link `00-intake.md` in the issue body.

**Outputs**: `00-intake.md`, GitHub parent issue.

**Gate**: none — intake always runs.

**Parallelism**: none.

---

## Phase 2 — Worktree Setup

**Objective**: isolate the work in a dedicated git worktree so the main branch is never touched until the PR is ready.

**Inputs**: `WORKTREE` path (default: `../worktrees/<slug>`), `BRANCH` name (default: `feat/<slug>` or `fix/<slug>`).

**Steps**:

1. Run `git worktree add <WORKTREE> -b <BRANCH>`.
2. Confirm the worktree was created successfully.
3. Write `01-worktree.md` recording: worktree path, branch name, base commit SHA, and timestamp.

**Outputs**: `01-worktree.md`, git worktree.

**Gate**: none — worktree setup always runs immediately after intake.

**Parallelism**: none.

---

## Phase 3 — Codebase Exploration

**Objective**: understand the relevant parts of the codebase deeply enough to produce a well-grounded implementation plan.

**Inputs**: `00-intake.md`, `01-worktree.md`, override files (if present).

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
5. Write `02-exploration/summary.md`: consolidated findings, patterns to follow, anti-patterns to avoid.
6. Write `02-exploration/files.csv`: path, reason, phase-relevance.
7. Write `02-exploration/open-questions.md`: one row per question with `id`, `question`, `status: open`.
8. Create a GitHub child issue labelled `phase:exploration`, then attach it as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md). The sequence is: `gh issue create` → resolve both node IDs → `gh api graphql ... addSubIssue`. Link to `02-exploration/summary.md`.

**Outputs**: `02-exploration/summary.md`, `files.csv`, `open-questions.md`, GitHub sub-issue.

**Gate A**: `02-exploration/summary.md` must exist with `status: complete` in frontmatter before Phase 4 begins.

**Parallelism**: explorer agents run in parallel; step 4 (reading files) runs after all agents complete.

---

## Phase 4 — Online Research

**Objective**: answer open questions and verify up-to-date best practices through targeted research.

**Inputs**: `02-exploration/open-questions.md`, override files.

**Steps**:

1. Read `open-questions.md`. Group questions by domain (e.g., framework docs, security standards, algorithm choices).
2. Launch 1–3 research subagents in parallel, each assigned a distinct group of questions.
3. Each research agent must:
   - State the question being answered.
   - Check the official documentation for the relevant framework/library version in use.
   - Record: question, source URL, date checked, finding, confidence (`high | medium | low`), applicability to repo, decision.
4. Write `03-research/findings.md`: one section per question, structured per the above.
5. Write `03-research/sources.md`: one row per URL checked (even if not ultimately useful).
6. Update `open-questions.md`: mark each question `resolved` or escalate with `status: needs-human`.
7. Create a GitHub child issue labelled `phase:research`, then attach it as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md). The sequence is: `gh issue create` → resolve both node IDs → `gh api graphql ... addSubIssue`. Link to `03-research/findings.md`.

**Outputs**: `03-research/findings.md`, `sources.md`, updated `open-questions.md`, GitHub sub-issue.

**Gate B**: `03-research/findings.md` must exist with `status: complete` in frontmatter before Phase 5 begins.

**Parallelism**: research agents run in parallel.

---

## Phase 5 — Clarification

**Objective**: resolve any blocking questions that remain after exploration and research, with minimum burden on the human.

**Inputs**: `02-exploration/open-questions.md` (updated by Phase 4), `03-research/findings.md`.

**Steps**:

1. Review all questions with `status: needs-human`.
2. Attempt to resolve each using artifacts already available. Mark any newly resolved questions `resolved`.
3. Classify remaining questions as `blocking: true` (implementation cannot proceed without an answer) or `blocking: false` (a reasonable assumption can be stated).
4. For `blocking: false` questions, record the assumption in `04-clarifications.md` and proceed.
5. For `blocking: true` questions: collect all into a single, minimal prompt (≤3 questions per batch). Present to the human.
6. Record human answers in `04-clarifications.md`.
7. Repeat step 5 only if new `blocking: true` questions surface from answers (rare).

**Outputs**: `04-clarifications.md`.

**Gate C**: `04-clarifications.md` must exist and contain no entry with `blocking: true` and `status: unanswered` before Phase 6 begins.

**Parallelism**: none.

---

## Phase 6 — Plan

**Objective**: produce a written, approved implementation plan that Phase 8 can execute without further design work.

**Inputs**: all artifacts from Phases 1–5, relevant source files.

**Steps**:

1. Re-read `00-intake.md` (acceptance criteria), `02-exploration/summary.md`, `03-research/findings.md`, and `04-clarifications.md`.
2. Read the key source files from `files.csv` that are directly affected by the work item.
3. Write `05-plan.md` using the [plan template](templates/plan.md). Required sections:
   - Goal and non-goals.
   - Recommended approach and rationale.
   - Alternatives considered (if meaningful trade-off exists).
   - File-by-file implementation map (exact paths, exact changes).
   - Verification guidance (test commands, manual checks, acceptance criteria mapping).
4. Present a concise summary of the plan to the human. Gate on explicit approval.
5. Create a GitHub child issue labelled `phase:plan`, then attach it as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md). The sequence is: `gh issue create` → resolve both node IDs → `gh api graphql ... addSubIssue`. Link to `05-plan.md`.
6. Update `00-intake.md` frontmatter: `plan_approved: true`, `plan_path: .coding-workflow/work/<slug>/05-plan.md`.

**Outputs**: `05-plan.md`, updated `00-intake.md`, GitHub sub-issue.

**Gate D**: `05-plan.md` must exist and `00-intake.md` must have `plan_approved: true` before Phase 7 begins.

**Parallelism**: none.

---

## Phase 7 — TDD Task Graph

**Objective**: decompose the approved plan into a DAG of TDD vertical slices with explicit sequencing.

**Inputs**: `05-plan.md`.

**Steps**:

1. Identify distinct behaviours to implement. Each behaviour becomes one vertical slice: RED → GREEN → REFACTOR.
2. For each slice, determine: id, name, stage (`red | green | refactor`), depends_on (list of prior slice ids), parallelizable (`true | false`).
3. **Do not write all RED slices before any GREEN slices.** Each vertical slice is independent.
4. Write `06-task-graph.yaml` using the [task-graph template](templates/task-graph.yaml).
5. Create GitHub child issues for each major implementation task (group minor slices if >8 tasks to avoid issue noise), then attach each one as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md). The sequence is: `gh issue create` → resolve both node IDs → `gh api graphql ... addSubIssue`. Label each `phase:implement` plus `parallel` or `sequential` as appropriate.
6. After Gate E is satisfied, stop the current session and hand off a resume command: `coding-task-workflow RESUME=<slug>`. Do not proceed to Phase 8 in the same invocation, even if the user explicitly asks you to continue immediately.

**Outputs**: `06-task-graph.yaml`, GitHub sub-issues for implementation tasks.

**Gate E**: `06-task-graph.yaml` must exist and at least one RED task must be defined before Phase 8 begins.

**Parallelism**: none for authoring the graph; execution in Phase 8 follows the graph's parallelism rules.

---

## Phase 8 — Implementation

**Objective**: execute the task graph using a strict TDD red→green→refactor loop.

**Inputs**: `06-task-graph.yaml`, `05-plan.md`, source files from `files.csv`, fresh session resumed after the Phase 7 hard stop.

**Steps**:

1. Process tasks in dependency order. Run tasks marked `parallelizable: true` concurrently when their dependencies are satisfied.
2. For each sequential task:
   a. **RED**: write a failing test that captures the behaviour. Run it; confirm it fails for the expected reason.
   b. **GREEN**: write the minimal code to make the test pass. Run it; confirm it passes.
   c. **REFACTOR**: clean up if needed; run tests again; confirm still green.
3. For parallel task groups, launch one implementation subagent per task. Each agent follows the same RED→GREEN→REFACTOR loop.
4. After each slice, append an entry to `07-implementation-log.md`: slice id, status, files changed, test result.
5. Never add untested code paths. If a useful branch is not yet covered by a test, do not add it.

**Outputs**: modified source files, tests, `07-implementation-log.md`.

**Gate**: none (the task graph itself is the gate structure).

**Parallelism**: parallelizable task groups run concurrently; sequential tasks run in order.

Strict TDD rules: see [../tdd/SKILL.md](../tdd/SKILL.md).

---

## Phase 9 — Review

**Objective**: catch defects, security issues, and tech debt before the code is committed.

**Inputs**: changed source files and tests, `05-plan.md`, `06-task-graph.yaml`.

**Steps**:

1. Determine the scope of changed files.
2. Partition files into non-overlapping groups by module or directory.
3. Launch three specialised review subagents in parallel (one per review type):

   **Code review agent**:
   - Check: conventions match the codebase, no dead code, no obvious logic errors, clear naming, DRY.
   - Write findings to `08-review/code-review.md`.

   **Security review agent**:
   - Check: OWASP Top 10, injection risks, hardcoded secrets, insecure defaults, over-privileged access, unvalidated input, broken auth.
   - Write findings to `08-review/security-review.md`.

   **Tech-debt review agent**:
   - Check: duplication, high coupling, complex functions (cyclomatic complexity), missing abstraction opportunities, known anti-patterns for the language/framework.
   - Write findings to `08-review/tech-debt.md`.

4. Each finding is classified: `severity: High | Medium | Low | Info`.
5. Consolidate results. Fix all `High` severity findings immediately (re-run Phase 8 slices as needed).
6. Record `Medium` and `Low` findings as labelled follow-up GitHub issues: `tech-debt` or `security`.
7. Create a GitHub child issue labelled `phase:review`, then attach it as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md).

**Outputs**: `08-review/code-review.md`, `08-review/security-review.md`, `08-review/tech-debt.md`.

**Gate**: none — review always runs after implementation.

**Parallelism**: three review agents run concurrently.

---

## Phase 10 — Verification

**Objective**: confirm the implementation satisfies every acceptance criterion and all automated checks pass.

**Inputs**: `00-intake.md` (acceptance criteria), `05-plan.md` (verification guidance), `test-commands.yaml` (if available).

**Steps**:

1. Run the test suite, linter, type-checker, and build commands from `.coding-workflow/overrides/test-commands.yaml`. If the file does not exist, run the commands inferred during bootstrap or from `package.json` / `Makefile`.
2. For each acceptance criterion in `00-intake.md`: record `pass` or `fail` with evidence (command output, screenshot, log excerpt).
3. Verify that no `High` severity issues remain from Phase 9 review.
4. Write `09-verification.md` using the [verification template](templates/verification.md).
5. If any criterion fails: return to Phase 8 to fix the failing behaviour, then re-run verification.
6. Create a GitHub child issue labelled `phase:verify`, then attach it as a true sub-issue of the Phase 1 parent issue using the `addSubIssue` GraphQL mutation described in [issue-hierarchy.md](issue-hierarchy.md).

**Outputs**: `09-verification.md`.

**Gate F**: all acceptance criteria must be `pass` and all automated checks must exit 0 before Phase 11 begins.

**Parallelism**: test suite steps may run in parallel subagents if the test framework supports it.

---

## Phase 11 — Commit / Push / PR

**Objective**: land the verified work into a PR.

**Inputs**: all changed files, `09-verification.md`, parent GitHub issue number.

**Steps**:

1. Stage all changed files.
2. Write a conventional-commits message: `<type>(<scope>): <subject>`. Include a body linking to the work-item slug and parent issue, then append a `Co-authored-by: NAME <EMAIL>` trailer block separated from that body by a blank line using your own known co-author identity. For GitHub Copilot CLI, use `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`. If more than one trailer is present, keep them together in that final trailer block.
3. Push the branch to the remote.
4. Open a pull request:
   - Title: conventional-commits subject.
   - Body: links to parent issue (`Closes #N`), link to `.coding-workflow/work/<slug>/`, summary of changes, open follow-up items.
5. Write `10-pr.md`: PR number, URL, list of follow-up issues created during review.
6. Close completed sub-issues. Leave open items as labelled issues for future sprints.

**Outputs**: `10-pr.md`, PR, closed sub-issues.

**Gate**: none after Gate F.

**Parallelism**: none.
