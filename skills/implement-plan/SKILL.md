---
name: implement-plan
description: Execute or resume an existing implementation plan end-to-end. Use this skill whenever the user wants to implement, build, or start coding from an already-created plan — common phrases include "implement the plan", "execute it", "build the thing", "run through the tasks", "pick up where I left off", or "continue implementing from tasks.md". Triggers on references to plan.md or tasks.md combined with action intent, or when the user says they ran create-plan / create-tasks and now want execution. Handles checklist gating, phase-by-phase task execution with dependency-aware parallelization, TDD-first delivery, progress checkboxes, code review orchestration, and completion validation. Do NOT use when the user wants to create or revise a plan (use create-plan), generate task breakdowns (use create-tasks), or do standalone code review, refactoring, or debugging without a plan.
argument-hint: "plan_file: .agents/scratchpad/<feature>/plan.md"
disable-model-invocation: true
---

# Implement plan

Turn planning artifacts into working code through a disciplined pipeline: validate readiness → prepare the project → execute phases → review the result → confirm completion. Each stage gates the next, catching problems before they compound.

The pipeline is **resumable** — if execution was interrupted, already-completed tasks (marked `[X]` in tasks.md) are skipped automatically so you pick up where you left off.

## Inputs

- **plan_file** (optional): The path to the plan file to implement.

### Inferring plan_file

When `plan_file` is not explicitly provided, resolve it from context before proceeding:

1. **Conversation context**: Check whether a plan file was recently created or mentioned in the current session (e.g., output from `create-plan` or `create-tasks`). Use that path if found.
2. **Ask the user**: If no candidate is found after the steps above, ask which plan file to use.

If the resolved file is unreadable or does not contain actionable planning content, stop and return a blocking error.

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

**Controller/subagent split:**

- The main agent is the controller. It decides which phase is next, gathers the relevant planning context, and launches a dedicated implementation subagent for that phase. Do not execute phase work inline in the controller.
- Use at least one implementation subagent per phase. Do not collapse multiple phases into one long-running implementation subagent.
- The controller prompt must include the phase name, ordered task list, dependency rules, touched file paths, resumption state, relevant planning artifacts, and the verification expectations for that phase.
- The phase subagent must load the `tdd` skill before it starts implementing. Treat that as the first implementation step for the phase so every behavioral change follows an explicit red-green-refactor loop rather than ad hoc coding.
- The phase subagent must return a concrete execution report: tasks attempted, RED/GREEN/REFACTOR progress where applicable, files changed, validations run, failures, deferments, and which tasks are ready to be marked `[X]`.
- The controller owns `tasks.md` checkmark updates and the checkpoint decision. Only mark a task `[X]` after the subagent provides verification evidence that satisfies the rules below.

**TDD-first inside the phase subagent:** Within each phase, run test tasks before their corresponding implementation tasks. Writing tests first clarifies intent and catches regressions immediately. When a test task and its implementation counterpart are both in the same phase, the test runs first regardless of task ID ordering.

**Parallelization inside the phase subagent:**

- `[P]` tasks may run in parallel only when their touched file paths do not overlap — this prevents conflicting writes.
- Sequential tasks run in declared order. If a non-parallel task fails, halt the phase.
- If one parallel task fails, continue the still-independent parallel work and report the failure.

**Task tracking — verify then mark:**

A `[X]` checkmark in `tasks.md` is a permanent promise that the task's work is done and verified. Since checkmarks are the source of truth for resumption, a premature `[X]` on a broken task means the next run will skip it and build on a broken foundation. This makes verification before marking essential — not optional, not deferrable.

Before marking any task `[X]`, run a concrete verification step that matches the task type:

| Task type                       | Verification                                                 | What counts as success                                                                                                                                                                                                                                                                                 |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Code implementation**         | Build/compile/lint the changed files, then run related tests | No errors from build/lint, and any pre-existing tests for the touched code pass                                                                                                                                                                                                                        |
| **TDD test writing** (RED step) | Run the new tests                                            | Tests fail for the intended reason — a clean RED result. In TDD-first (Tests phase before Core), module-not-found errors are expected and count as clean RED because the implementation doesn't exist yet. A test that errors out due to syntax problems _in the test file itself_ is not a clean RED. |
| **Bug-fix / regression tests**  | Run the tests after the fix is applied                       | Tests pass                                                                                                                                                                                                                                                                                             |
| **Config / infra / schema**     | Validate the artifact parses and applies                     | Config loads without errors, schema is valid, service starts                                                                                                                                                                                                                                           |
| **Docs / non-code**             | Confirm the file exists and is non-empty                     | File is present with substantive content                                                                                                                                                                                                                                                               |
| **Refactor**                    | Run the existing test suite for the affected area            | All previously-passing tests still pass                                                                                                                                                                                                                                                                |

If none of these categories fit, use the **fallback rule**: find the nearest concrete validation command or artifact check for the task. If no validation exists at all, do NOT mark `[X]` — instead leave the task `[ ]`, report it as "completed but unverified" in the phase checkpoint, and let the user decide.

**Never mark speculative completion.** If a task hit errors that you worked around, partially completed, or deferred for later — it stays `[ ]`. Only clean, verified outcomes earn the checkmark. When in doubt, leave it unchecked; a false `[ ]` is cheap to fix on the next run, but a false `[X]` silently corrupts the resumption state.

**Error recovery:** When a task fails verification or encounters errors during execution:

- Report the failure with context (error message, file, what was attempted).
- Leave the task as `[ ]` in `tasks.md` — do not mark it `[X]`.
- For non-parallel tasks, halt the phase and suggest concrete next steps (fix the error, skip the task, or ask the user).
- For parallel tasks, continue independent work and collect all failures for a consolidated report at the phase checkpoint. Mark a parallel task `[X]` only after its own task-local verification passes. If verification depends on a shared test suite that other parallel tasks also affect, defer marking until the shared validation passes at the phase checkpoint.

**Phase checkpoints:** After each phase, verify the work before moving on. This is a backstop that catches any tasks that were incorrectly marked:

```text
Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Integrity check: <any [X] tasks whose expected outputs are missing or whose tests now fail>
- Next Action: <advance to next phase | resolve blockers | request user approval>
```

Run the full test suite for the phase's scope. If any task marked `[X]` has failing tests or missing expected outputs, flag it as a checkpoint integrity error — revert its `[X]` back to `[ ]` and report the discrepancy before proceeding.

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
- Cross-check: for each `[X]` task, confirm its expected output files exist and its associated tests pass. If any `[X]` task fails this cross-check, revert it to `[ ]` and report the discrepancy.
- Delivered features match the specification and technical plan
- Tests pass and coverage expectations are met
- Report final status with completed work, blockers, and any deferred items

## Safety rules

- Never use destructive git or filesystem commands unless the user explicitly asks.
- Do not revert unrelated working-tree changes.
- If unrelated changes appear and conflict with the current phase, pause and ask how to proceed.
- Keep edits focused on the files required by the active tasks.
