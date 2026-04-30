---
name: implement-plan
description: Execute or resume an existing implementation plan end-to-end. Use this skill whenever the user wants to implement or continue work from an already-created plan or task breakdown — for example "implement the plan", "execute it", "build the thing", "pick up where I left off", or "continue from plan.md/tasks.md" after create-plan or create-tasks. Handles checklist gating, controller-owned phase execution with explicit parallel waves for eligible `[P]` tasks, TDD-first delivery, code review orchestration, and completion validation. Do NOT use it to create or revise a plan, generate tasks, or do standalone review, refactoring, or debugging without a plan.
argument-hint: "plan_file: .agents/scratchpad/<feature>/plan.md"
disable-model-invocation: true
---

# Implement plan

Turn planning artifacts into working code through a resumable pipeline: validate readiness → prepare the project → execute phases → review the result → confirm completion. Skip tasks already marked `[X]` in `tasks.md`. The controller owns scheduling: it turns eligible `[P]` work into explicit parallel waves instead of asking one phase-wide subagent to improvise the parallelism.

## Inputs

- **plan_file** (optional): The path to the plan file to implement.

### Resolving plan_file

If `plan_file` is omitted, first reuse a recent plan path mentioned or created in the current session (for example by `create-plan` or `create-tasks`). Otherwise ask the user which plan to use. If the resolved file is unreadable or does not contain actionable planning content, stop with a blocking error.

## Progress reporting

Always structure updates with these five sections:

1. `Checklist Gate` — readiness check results
2. `Implementation Context Loaded` — what artifacts were found and read
3. `Phase Execution` — task-by-task progress with checkpoints
4. `Code Review Findings` — issues found and their severity
5. `Completion Validation` — final status and deliverables

Include concise evidence in each: files read, tasks completed, tests run, blockers, and deferments.
Even when the user asks for only one section or a concise handoff, still include all five headings. Use brief placeholders such as `Not started yet` or `Pending this phase` for sections that do not have active work yet.

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

- Required: `tasks.md` and `plan.md`.
- If present: `data-model.md`, `contracts/`, `research.md`, and `quickstart.md`.
- If `tasks.md` or `plan.md` is missing, stop and instruct the user to run `/create-tasks` or regenerate planning artifacts.

### 2. Prepare the project

- Create or update ignore files only when the project actually uses the relevant tooling.
- Never overwrite user-managed ignore files; only append missing critical patterns detected from real signals such as a git repo, Dockerfiles, lint/format configs, Terraform files, or Helm charts.
- Read [references/ignore-patterns.md](references/ignore-patterns.md) for technology-specific and tool-specific patterns to add.

### 3. Parse tasks

- Parse `tasks.md` into phases (Setup, Tests, Core, Integration, Polish), task IDs, descriptions, file paths, `[P]` markers, and dependency ordering.
- If no actionable tasks are found, stop and recommend regenerating `tasks.md`.
- On resume, identify tasks already marked `[X]`, skip them, and report completed vs remaining work before execution continues.

### 4. Execute phases

Execute phases in order: Setup → Tests → Core → Integration → Polish.

**Controller-owned scheduling and dispatch:**

- The main agent is the controller: choose the next phase, gather planning context, materialize a `phase_execution_plan`, and launch implementation subagents. Do not execute phase work inline.
- Do not hand an entire phase to one subagent and tell it to decide what can run in parallel. The controller decides the schedule first, then dispatches only the assigned task set for each subagent.
- Before dispatch, reorder ready tasks so TDD test-writing tasks run before their corresponding implementation tasks, even when task IDs would otherwise suggest the reverse.
- `phase_execution_plan` contains ordered waves:
  - **Parallel wave**: two or more `[P]` tasks whose dependencies are satisfied, whose TDD ordering is valid, and whose touched file paths are pairwise disjoint.
  - **Sequential slot**: a single task, or tightly coupled bundle, that must stay serialized because it is not `[P]`, depends on unfinished work, or overlaps on files with another ready task.
- `[P]` is permission, not an override. A `[P]` task still runs sequentially when it shares touched file paths with another task, depends on unfinished work, needs another task's output first, or would break TDD-first ordering.
- When a parallel wave is eligible, launch its implementation subagents in the same turn using the `task` tool in `background` mode. Default to one task per subagent so file ownership, verification, and task-status decisions stay unambiguous.
- Use at least one implementation subagent per phase. If a phase contains an eligible parallel wave, use multiple implementation subagents for that wave instead of collapsing the work into one executor.
- Every implementation subagent must load the `tdd` skill first and receive only its assigned task IDs, phase name, wave ID, allowed file paths, prerequisite context, relevant planning artifacts, resumption state, and verification expectations. Forbid it from broadening scope or editing files assigned to another in-flight wave member. It must return tasks attempted, RED/GREEN/REFACTOR progress, files changed, validations run, failures, deferments, and tasks ready to be marked `[X]`.
- The controller alone updates `tasks.md`, manages wave transitions, and makes checkpoint decisions. Only mark `[X]` after the assigned subagent provides verification evidence that satisfies the rules below.

**When presenting a phase schedule to the user, make the wave mechanics explicit:**

- Name each wave (`W1`, `W2`, etc.) and each member (`W1-A`, `W1-B`, etc.) when there is parallel work.
- Use an explicit launch sentence for the wave, for example: `Launch W1-A (T003), W1-B (T004), and W1-C (T005) in parallel as separate implementation subagents.`
- For any blocked or deferred `[P]` task, say the reason in a full sentence using direct language such as: `T010 and T011 cannot run in parallel because both touch src/search/service.ts, so keep T011 for W2.` Avoid implying the rule only indirectly.
- After every wave, include an explicit wait boundary such as: `Wait for W1 results before launching W2.` If the next wave depends on one member of the prior wave, say that directly.
- When tests run before implementation, say explicitly that this follows **TDD-first** or **test-first** ordering so the rationale is visible in the handoff.
- For handoff-style responses, include a `Checkpoint Decision` block under `Phase Execution` using that exact heading and explicit `PASS | PASS WITH DEFERRED ITEMS | FAIL` criteria before advancing.
- When reporting a clean TDD RED outcome, use the exact phrase `clean RED` and say explicitly that it is **not a broken test**. Name the broken-test examples directly: syntax errors in the test file, import crashes caused by the test itself, or invalid test setup do **not** count as `clean RED`.
- When a clean RED outcome counts as success, say explicitly that this is the expected result in **TDD-first / RED-GREEN** workflow.
- When reporting a failed parallel wave, say explicitly: `The controller does not launch another wave until the failure has been reported to the user and resolved.` Do not soften this to an implication about waiting or collecting results.

**Task tracking — verify then mark:** `[X]` means done and verified. Never mark speculative completion.

- `[P]` tasks may share a wave only when their touched file paths do not overlap — this prevents conflicting writes.
- Sequential tasks run in declared or TDD-adjusted order. If a sequential slot fails, halt the phase immediately.
- If one task in a parallel wave fails, let the already-launched independent tasks finish, collect their results, and do not launch another wave until the controller reports the failure and decides whether to continue.
- If a parallel task needs a shared validation step before it can be marked done, report it as ready for controller checkpoint validation rather than marking it `[X]` prematurely.

Before marking any task `[X]`, run a concrete verification step that matches the task type:

| Task type                       | Verification                                                 | What counts as success                                                                                                                                                                                                                                                                                 |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Code implementation**         | Build/compile/lint the changed files, then run related tests | No errors from build/lint, and any pre-existing tests for the touched code pass                                                                                                                                                                                                                        |
| **TDD test writing** (RED step) | Run the new tests                                            | Tests fail for the intended reason — a clean RED result. In TDD-first (Tests phase before Core), module-not-found errors are expected and count as clean RED because the implementation doesn't exist yet. A test that errors out due to syntax problems _in the test file itself_ is not a clean RED. |
| **Bug-fix / regression tests**  | Run the tests after the fix is applied                       | Tests pass                                                                                                                                                                                                                                                                                             |
| **Config / infra / schema**     | Validate the artifact parses and applies                     | Config loads without errors, schema is valid, service starts                                                                                                                                                                                                                                           |
| **Docs / non-code**             | Confirm the file exists and is non-empty                     | File is present with substantive content                                                                                                                                                                                                                                                               |
| **Refactor**                    | Run the existing test suite for the affected area            | All previously-passing tests still pass                                                                                                                                                                                                                                                                |

If none of these categories fit, use the **fallback rule**: choose the nearest concrete validation command or artifact check. If no validation exists, do NOT mark `[X]` — leave the task `[ ]`, report it as "completed but unverified" in the phase checkpoint, and let the user decide.

**Error recovery:** When a task fails verification or encounters errors during execution:

- Report the failure with context (error message, file, what was attempted).
- Leave the task as `[ ]` in `tasks.md` — do not mark it `[X]`.
- For non-parallel tasks, halt the phase and suggest concrete next steps (fix the error, skip the task, or ask the user).
- For parallel tasks, continue independent work and collect failures for the phase checkpoint. Mark a parallel task `[X]` only after its own task-local verification passes. If verification depends on shared validation, defer marking until the phase checkpoint.
- In user-facing status updates for a failed parallel wave, state both parts of the rule: allow already-launched independent work to finish, **and** say verbatim that `the controller does not launch another wave until the failure has been reported to the user and resolved`.

**Phase checkpoints:** After each phase, verify the work before moving on:

```text
Checkpoint Decision
- Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
- Evidence: <tasks completed, tests run, files changed, blockers/deferments>
- Integrity check: <any [X] tasks whose expected outputs are missing or whose tests now fail>
- Next Action: <advance to next phase | resolve blockers | request user approval>
```

Run the full test suite for the phase's scope. If any task marked `[X]` has failing tests or missing expected outputs, flag it as a checkpoint integrity error, revert its `[X]` back to `[ ]`, and report the discrepancy before proceeding.

Do not advance unless the checkpoint passes or the user explicitly approves.

### 5. Code review

After implementation, review all changed code.

Build the review scope from all uncommitted changed files (staged, unstaged, and untracked via `git status --porcelain`). Exclude deleted files and `.gitignore` files from review but list them under excluded files.

- Launch code-simplifier subagents to identify refactoring opportunities. This is not optional for runs that produce changed files:
  - **≤5 files**: 1 code-simplifier agent covering all changed files
  - **>5 files**: partition files into non-overlapping groups by module, directory, or logical area so each file appears in exactly one agent's scope
- Launch 3 code-reviewer agents in parallel using code-reviewer, each focusing on a different lens:

1. **Simplicity & DRY** — duplication, unnecessary complexity, dead code
2. **Bugs & correctness** — logic errors, null handling, race conditions, security
3. **Conventions & abstractions** — project patterns, naming, architecture alignment

- Pass every review agent the controller-authored `review_scope_files` list (or its partition for code-simplifier). Say explicitly that subagents **must not recompute or narrow scope independently**.
- Read [references/review-protocol.md](references/review-protocol.md) for the full coverage template and scope-conflict rules. Report Total Changed Files, Total Reviewed Files, Missing Files, Missing File List, Excluded Files, and Completion Gate. If `Missing Files > 0`, review status is INCOMPLETE until gaps are reviewed or explicitly deferred. If a reviewer reports a different file list than what it was given, treat it as a scope conflict and reconcile.
- After review, consolidate findings and call out the highest-severity issues to fix.

### 6. Completion validation

Verify the delivered work is complete and correct:

- All required tasks are marked `[X]` in `tasks.md`
- Cross-check: for each `[X]` task, confirm its expected output files exist and its associated tests pass. If any `[X]` task fails this cross-check, revert it to `[ ]` and report the discrepancy.
- Confirm the delivered features match the specification and technical plan, and that tests plus coverage expectations are met.
- Report final status with completed work, blockers, and any deferred items.

## Safety rules

- Never use destructive git or filesystem commands unless the user explicitly asks.
- Do not revert unrelated working-tree changes.
- If unrelated changes appear and conflict with the current phase, pause and ask how to proceed.
- Keep edits focused on the files required by the active tasks.
