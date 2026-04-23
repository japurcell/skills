---
name: coding-task-workflow
description: Deterministic end-to-end workflow for coding tasks — feature additions, bug fixes, or spec-driven changes. Use this skill whenever the user wants to implement something non-trivial, start from a feature description, bug report, or spec, follow a structured multi-phase approach, or ensure all work is tracked via GitHub issues and PR-backed artifacts. This skill combines deep codebase exploration, parallel online research, clarification, TDD-based implementation, multi-role review, and a bootstrap phase that can generate repo-local override files for any target repository.
---

# Coding Task Workflow

A portable, deterministic workflow for coding tasks. Covers everything from intake to merged PR, with an optional repo-bootstrap phase that synthesises repo-local override files from existing documentation and signals.

See [README.md](README.md) for installation, usage examples, and an overview of all generated artifacts.

---

## Quick Reference — Phases

| #   | Phase                      | Parallelism           | Human gate |
| --- | -------------------------- | --------------------- | ---------- |
| 0   | **Bootstrap** _(optional)_ | parallel              | –          |
| 1   | **Intake**                 | –                     | –          |
| 2   | **Worktree setup**         | –                     | –          |
| 3   | **Codebase exploration**   | parallel              | Gate A     |
| 4   | **Online research**        | parallel              | Gate B     |
| 5   | **Clarification**          | –                     | Gate C     |
| 6   | **Plan**                   | –                     | Gate D     |
| 7   | **TDD task graph**         | –                     | Gate E     |
| 8   | **Implementation**         | sequential + parallel | –          |
| 9   | **Review**                 | parallel              | –          |
| 10  | **Verification**           | –                     | Gate F     |
| 11  | **Commit / Push / PR**     | –                     | –          |

Read [references/workflow.md](references/workflow.md) for full phase specifications.
Read [references/stop-gates.md](references/stop-gates.md) for gate definitions and exit criteria.

---

## Invocation

```
coding-task-workflow

Arguments (all optional — gather interactively if not provided):
  WORK_ITEM   Feature description, bug report, spec text, or path to a spec file
  ISSUE       GitHub issue number to track this work item (created if absent)
  WORKTREE    Worktree path (defaults to ../worktrees/<slug>)
  BRANCH      Branch name (defaults to feat/<slug> or fix/<slug>)
  BOOTSTRAP   Set to "only" to run only the repo bootstrap phase
  RESUME      Work-item ID to resume from last recorded phase
```

The skill determines the correct starting phase automatically.

---

## Phase 0 — Bootstrap _(optional)_

Run this phase alone on a new or poorly-documented repository, or automatically if override files are missing or stale.

```
coding-task-workflow BOOTSTRAP=only
```

What it does:

1. Inspects `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `.github/`, manifests, lockfiles, and CI workflow files.
2. Infers tech stack, tooling, test/lint/typecheck commands, architecture notes, and repo policies.
3. Writes or updates repo-local override files only where necessary (never duplicates existing canonical docs).
4. Records provenance, confidence, and evidence in each generated file.

Generated override files (stored in `.coding-workflow/` in the **target** repo):

| File                    | Purpose                                                |
| ----------------------- | ------------------------------------------------------ |
| `repo-inventory.yaml`   | Tech stack, languages, frameworks, key paths           |
| `doc-sources.md`        | Links to existing docs rather than duplicating content |
| `test-commands.yaml`    | Test, lint, typecheck, and build commands              |
| `repo-policy.md`        | Contribution rules, branch naming, PR process          |
| `architecture-notes.md` | High-level architecture, key modules, patterns         |
| `agent-hints.md`        | Gotchas, known traps, agent-specific guidance          |

See [references/bootstrap.md](references/bootstrap.md) for full bootstrap specification.

---

## Phase 1 — Intake

Capture the work item in a structured artifact before any code is touched.

1. Collect `WORK_ITEM` (ask if not provided — one prompt only).
2. Classify: `feature | bug | refactor | spec | chore`.
3. Assign a deterministic slug: `YYYY-MM-DD-<kebab-title>`.
4. Create artifact directory: `.coding-workflow/work/<slug>/`.
5. Write `00-intake.md` from the [intake template](references/templates/intake.md).
6. Create GitHub parent issue if `ISSUE` is not provided. Apply labels per [references/issue-hierarchy.md](references/issue-hierarchy.md).

---

## Phase 2 — Worktree Setup

Isolate the work before any files are modified.

1. Create a git worktree: `git worktree add <WORKTREE> -b <BRANCH>`.
2. Write `01-worktree.md` recording the worktree path, branch, and base commit.
3. Link worktree artifact to the parent GitHub issue.

---

## Phase 3 — Codebase Exploration

Understand the relevant parts of the codebase using parallel subagents.

1. Launch 2–3 code-explorer subagents in parallel, each covering a different angle (e.g., similar features, architecture, test patterns, extension points).
2. Read all key files surfaced by agents.
3. Write `02-exploration/summary.md`, `files.csv`, and `open-questions.md`.
4. **Gate A**: exploration artifact must exist before proceeding.

See [references/delegation-rules.md](references/delegation-rules.md) for explorer agent instructions.

---

## Phase 4 — Online Research

Fill remaining gaps using parallel research subagents.

1. Identify open questions from Phase 3.
2. Launch 1–3 research subagents in parallel, each targeting a distinct question or topic.
3. Write `03-research/findings.md` and `sources.md` — one row per source: question, URL, date, finding, confidence, applicability, decision.
4. **Gate B**: research artifact must exist before proceeding.

---

## Phase 5 — Clarification

Resolve any questions that remain after exploration and research.

1. Review `open-questions.md`. Mark each as `resolved` or `blocking`.
2. If no `blocking: true` questions remain, proceed automatically.
3. If blocking questions remain, present them to the human (minimum viable set only — ≤3 per prompt).
4. Record answers in `04-clarifications.md`.
5. **Gate C**: no unresolved blocking questions may remain before Phase 6.

---

## Phase 6 — Plan

Design the implementation with full context in hand.

1. Read all artifacts from Phases 3–5 plus relevant source files.
2. Write `05-plan.md` — goal, non-goals, approach, file-by-file map, verification guidance.
3. Present plan summary to human; gate on explicit approval.
4. Create GitHub sub-issue for the plan. Link to parent.
5. **Gate D**: plan must be approved before Phase 7.

See [references/templates/plan.md](references/templates/plan.md) for the plan template.

---

## Phase 7 — TDD Task Graph

Break the plan into TDD phases with explicit sequencing.

1. Decompose into vertical slices, each: `red → green → refactor`.
2. Mark each task `sequential` or `parallelizable`.
3. Write `06-task-graph.yaml` — id, name, stage (red/green/refactor), depends_on, parallelizable.
4. Create GitHub sub-issues for major implementation tasks.
5. **Gate E**: task graph must exist and all RED tasks must be defined before implementation starts.

See [references/templates/task-graph.yaml](references/templates/task-graph.yaml) for the schema.

---

## Phase 8 — Implementation

Execute the task graph using the tdd skill.

1. Process tasks in dependency order; run parallelizable groups concurrently.
2. For each slice: write failing test → confirm failure → write minimal code → confirm green → refactor.
3. Update `07-implementation-log.md` after each slice.
4. Never implement code for a test that has not yet been written.

Follow the [tdd skill](../tdd/SKILL.md) for the full red-green-refactor protocol.

---

## Phase 9 — Review

Run specialised review subagents in parallel.

1. Launch three review subagents concurrently:
   - **Code review**: conventions, correctness, clarity.
   - **Security review**: OWASP Top 10, injection, secrets, auth.
   - **Tech-debt review**: duplication, coupling, complexity.
2. Write `08-review/code-review.md`, `security-review.md`, `tech-debt.md`.
3. Fix all High-severity findings before Phase 10; record Low/Medium as follow-up issues.

See [references/delegation-rules.md](references/delegation-rules.md) for reviewer agent prompts.

---

## Phase 10 — Verification

Confirm the implementation is correct and complete.

1. Run the test suite, linter, type-checker, and build commands from `test-commands.yaml`.
2. Verify each acceptance criterion in `05-plan.md`.
3. Write `09-verification.md` — pass/fail per criterion plus commands run.
4. **Gate F**: all verification checks must pass before Phase 11.

---

## Phase 11 — Commit / Push / PR

Land the work.

1. Stage changed files; write a conventional-commits message referencing the work item.
2. Push the branch to the remote.
3. Open a pull request; link to the parent GitHub issue and the artifact directory.
4. Write `10-pr.md` recording PR number, URL, and open follow-up items.
5. Close completed sub-issues; leave open items as labelled issues.

---

## artifact Directory Layout

All artifacts for a work item live in the **target repo** at:

```
.coding-workflow/
  work/<slug>/
    00-intake.md
    01-worktree.md
    02-exploration/
      summary.md
      files.csv
      open-questions.md
    03-research/
      findings.md
      sources.md
    04-clarifications.md
    05-plan.md
    06-task-graph.yaml
    07-implementation-log.md
    08-review/
      code-review.md
      security-review.md
      tech-debt.md
    09-verification.md
    10-pr.md
  overrides/
    repo-inventory.yaml
    doc-sources.md
    test-commands.yaml
    repo-policy.md
    architecture-notes.md
    agent-hints.md
```

artifact frontmatter schema: see [references/artifact-schema.md](references/artifact-schema.md).
Full template set: see [references/templates/](references/templates/).
