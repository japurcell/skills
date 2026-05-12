---
name: implement-plan
description: Execute or resume an existing implementation plan end-to-end. Use this skill whenever the user wants to implement, build, or start coding from an already-created plan — common phrases include "implement the plan", "execute it", "build the thing", "run through the tasks", "pick up where I left off", or "continue implementing from tasks.md". Triggers on references to plan.md or tasks.md combined with action intent, or when the user says they ran create-plan / create-tasks and now want execution. Handles checklist gating, phase-by-phase task execution with dependency-aware parallelization, TDD-first delivery, progress checkboxes, code review orchestration, and completion validation. Do NOT use when the user wants to create or revise a plan (use create-plan), generate task breakdowns (use create-tasks), or do standalone code review, refactoring, or debugging without a plan.
disable-model-invocation: true
---

# Implement plan

Turn planning artifacts into working code through a disciplined pipeline: validate readiness → prepare the project → execute phases → review the result → confirm completion. Each stage gates the next, catching problems before they compound.

The pipeline is **resumable** — if execution was interrupted, already-completed tasks (marked `[X]` in tasks.md) are skipped automatically so you pick up where you left off.

## Inputs

- **plan_file** (required): The path to the plan file to implement.

## Progress reporting

Structure updates around these five sections so the user can quickly orient themselves:

1. `Checklist Gate` — readiness check results
2. `Implementation Context Loaded` — what artifacts were found and read
3. `Phase Execution` — task-by-task progress with checkpoints
4. `Code Review Findings` — issues found and their severity
5. `Completion Validation` — final status and deliverables

Include concise evidence in each: files read, tasks completed, tests run, blockers, and deferments.

## Workflow

### 1. Validate readiness

Load `plan_file` and derive the feature directory from it.

**Checklist gate** — when `<feature-dir>/checklists/` exists:

- Scan each checklist file and count total items (`- [ ]`, `- [X]`, `- [x]`), completed, and incomplete.
- Show a status table:

  ```text
  | Checklist | Total | Completed | Incomplete | Status |
  |-----------|-------|-----------|------------|--------|
  | ux.md     | 12    | 12        | 0          | ✓ PASS |
  | test.md   | 8     | 5         | 3          | ✗ FAIL |
  ```

- If any checklist is incomplete, show the table and ask exactly: `Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)` — then stop until the user replies. `no`/`wait`/`stop` halts; `yes`/`proceed`/`continue` continues.
- If all pass, report that and continue. If no checklists directory exists, note its absence and continue.

**Load implementation context:**

- Required: `tasks.md`, `plan.md`.
- If present: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`.
- If `tasks.md` or `plan.md` is missing, stop and instruct the user to run `/create-tasks` or regenerate planning artifacts.

### 2. Prepare the project

Before writing feature code, make sure housekeeping files are in order. Create or update ignore files only when the project actually uses the relevant tooling — detect this through concrete signals like config files and directory structures, not assumptions.

- Never overwrite user-managed ignore files; only append missing critical patterns.
- Detect what's needed from real signals (e.g., `git rev-parse --git-dir` for .gitignore, `Dockerfile*` for .dockerignore, `.eslintrc*` / `eslint.config.*` for eslint ignores, `.prettierrc*` for .prettierignore, `*.tf` for .terraformignore, Helm charts for .helmignore).
- Read [references/ignore-patterns.md](references/ignore-patterns.md) for technology-specific and tool-specific patterns to add.

### 3. Parse tasks

Parse `tasks.md` into phases (Setup, Tests, Core, Integration, Polish), task IDs, descriptions, file paths, `[P]` parallel markers, and dependency ordering.

If no actionable tasks are found, stop and recommend regenerating `tasks.md`.

**Resumption:** Identify tasks already marked `[X]` and skip them. Report a summary of completed vs remaining tasks so the user knows where execution is picking up.

### 4. Execute phases

Execute phases in order: Setup → Tests → Core → Integration → Polish. Each phase builds on the previous one, so this ordering catches foundation problems before they cascade into later work.

**TDD-first:** Within each phase, run test tasks before their corresponding implementation tasks. Writing tests first clarifies intent and catches regressions immediately. When a test task and its implementation counterpart are both in the same phase, the test runs first regardless of task ID ordering.

**Parallelization:**

- `[P]` tasks may run in parallel only when their touched file paths do not overlap — this prevents conflicting writes.
- Sequential tasks run in declared order. If a non-parallel task fails, halt the phase.
- If one parallel task fails, continue the still-independent parallel work and report the failure.

**Task tracking:** Mark each completed task as `[X]` in `tasks.md` immediately after it succeeds. These checkmarks are the source of truth for resumption — if execution is interrupted, they tell the next run what's already done.

**Error recovery:** When a task fails:

- Report the failure with context (error message, file, what was attempted).
- For non-parallel tasks, halt the phase and suggest concrete next steps (fix the error, skip the task, or ask the user).
- For parallel tasks, continue independent work and collect all failures for a consolidated report at the phase checkpoint.

**Phase checkpoints:** After each phase, verify the work before moving on:

```text
Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Next Action: <advance to next phase | resolve blockers | request user approval>
```

Do not advance unless the checkpoint passes or the user explicitly approves.

### 5. Code review

After implementation, review all changed code. The review catches issues that tests miss — duplication, convention violations, security problems, and unnecessary complexity.

Build the review scope from all uncommitted changed files (staged, unstaged, and untracked via `git status --porcelain`). Exclude deleted files and `.gitignore` files from review but list them under excluded files.

#### Launch code-simplifier subagents

Launch [code-simplifier](../code-simplifier/SKILL.md) subagents to identify refactoring opportunities in the changed code. This is not optional — every implementation run that produces changed files must include code-simplifier review. Scale the agents based on the number of changed files:

- **≤5 files**: 1 code-simplifier agent covering all changed files
- **>5 files**: partition into non-overlapping groups by module, directory, or logical area — each file appears in exactly one agent's scope to prevent conflicting writes

Pass each code-simplifier agent the exact `review_scope_files` list (or its partition). The agents run independently and can be launched in parallel with the code-reviewer agents below.

#### Launch code-reviewer subagents

Launch 3 code-reviewer agents in parallel using code-reviewer, each focusing on a different lens:

1. **Simplicity & DRY** — duplication, unnecessary complexity, dead code
2. **Bugs & correctness** — logic errors, null handling, race conditions, security
3. **Conventions & abstractions** — project patterns, naming, architecture alignment

Pass each reviewer the same `review_scope_files` list. Subagents must not recompute or narrow the scope.

#### Coverage tracking and scope conflicts

Read [references/review-protocol.md](references/review-protocol.md) for the full coverage tracking template (Review Scope Coverage block) and scope conflict resolution rules. Key points:

- Report Total Changed Files, Total Reviewed Files, Missing Files, Excluded Files, and Completion Gate
- If `Missing Files > 0`, review status is INCOMPLETE until gaps are reviewed or the user explicitly defers
- If a reviewer reports a different file list than what it was given, treat it as a scope conflict and reconcile

After review, consolidate findings and call out the highest-severity issues to fix.

### 6. Completion validation

Verify the delivered work is complete and correct:

- All required tasks are marked `[X]` in `tasks.md`
- Delivered features match the specification and technical plan
- Tests pass and coverage expectations are met
- Report final status with completed work, blockers, and any deferred items

## Safety rules

- Never use destructive git or filesystem commands unless the user explicitly asks.
- Do not revert unrelated working-tree changes.
- If unrelated changes appear and conflict with the current phase, pause and ask how to proceed.
- Keep edits focused on the files required by the active tasks.
