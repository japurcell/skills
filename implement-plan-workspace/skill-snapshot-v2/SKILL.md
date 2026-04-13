---
name: implement-plan
description: Execute an existing implementation plan end-to-end from a plan file, including checklist gating, prerequisite validation, phase-by-phase task execution, TDD-first delivery, task checkbox updates, code review, and completion validation. Use this whenever the user asks to run or resume implementation from planning artifacts (such as plan.md and tasks.md), explicitly mentions /implement-plan, or wants feature work executed in ordered phases with dependency-aware parallelization and checkpoints. Prefer this skill over generic coding/review flows when the request is to execute an already-generated plan rather than create a new plan or only analyze code.
disable-model-invocation: true
---

# Implement plan

## Inputs

- **plan_file** (required): The path to the plan file to implement.

## Required Output Contract

Use these exact Markdown section headers in progress and completion updates:

1. `Checklist Gate`
2. `Implementation Context Loaded`
3. `Phase Execution`
4. `Code Review Findings`
5. `Completion Validation`

Each section should include concise evidence: files read, tasks completed, tests run, blockers, and deferments.

## Workflow

1. Load `plan_file` and derive the feature directory from it.

2. Run the checklist gate when `<feature-dir>/checklists/` exists:
   - Scan each checklist file.
   - Count total items (`- [ ]`, `- [X]`, `- [x]`), completed items (`- [X]`, `- [x]`), and incomplete items (`- [ ]`).
   - Show a status table with these exact columns:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     ```

   - If any checklist is incomplete, show the table, ask exactly `Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)`, and stop until the user replies. `no`, `wait`, or `stop` means halt; `yes`, `proceed`, or `continue` means continue.
   - If all checklists pass, report that and continue automatically.
   - If there is no checklists directory, report that no checklist gate is present and continue.

3. Load implementation context:
   - Required: `tasks.md`, `plan.md`.
   - If present: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`.
   - If `tasks.md` or `plan.md` is missing, stop and instruct the user to run `/create-tasks` or regenerate planning artifacts.

4. Verify setup artifacts before implementation:
   - Create or update ignore files only when the project setup calls for them.
   - Never overwrite user-managed ignore files; only append missing critical patterns.
   - Detect repo and tooling with concrete signals:
     - `git rev-parse --git-dir 2>/dev/null` for `.gitignore`
     - `Dockerfile*` or Docker mentioned in `plan.md` for `.dockerignore`
     - `.eslintrc*` for `.eslintignore`
     - `eslint.config.*` for config-level `ignores`
     - `.prettierrc*` for `.prettierignore`
     - `.npmrc` or `package.json` for `.npmignore` when publishing
     - `*.tf` for `.terraformignore`
     - Helm charts for `.helmignore`
   - Read [references/ignore-patterns.md](references/ignore-patterns.md) when choosing the technology-specific and tool-specific patterns to add.

5. Parse `tasks.md` into:
   - phases: Setup, Tests, Core, Integration, Polish
   - task IDs, descriptions, file paths, `[P]` markers
   - dependency and execution order rules
   - If no actionable tasks are found, stop and recommend regenerating `tasks.md`.

6. Execute phases in order: Setup, Tests, Core, Integration, Polish.
   - For each phase, hand off the ordered task IDs, dependency rules, touched file paths, TDD requirement, and the requirement to mark completed tasks as `[X]` in `tasks.md`.
   - `[P]` tasks may run in parallel only when their touched file paths do not overlap.
   - Sequential tasks must run in order. If a non-parallel task fails, halt the phase. If one parallel task fails, continue only the still-independent parallel work.
   - After each phase, run a checkpoint that verifies completed or deferred tasks, `tasks.md` sync, and the tests required for that phase.
   - Include this exact block before moving on:

     ```text
     Checkpoint Decision
     - Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
     - Evidence: <tasks completed, tests run, files changed, blockers/deferments>
     - Next Action: <advance to next phase | resolve blockers | request user approval>
     ```

   - Do not advance unless the checkpoint status permits it or the user explicitly approves continuation.

7. Run code review after implementation:
   - Build review scope from all uncommitted changed implementation files: staged, unstaged, and untracked.
   - Prefer git-based discovery such as `git status --porcelain` when available.
   - Exclude deleted files and every `.gitignore` file from review and simplification, but list them under excluded files.
   - Materialize a deterministic, stable-sorted `review_scope_files` list and pass that exact list to every review subagent.
   - Review subagents must not recompute or narrow scope. If a reviewer reports a different file list, explicitly call it a `scope conflict` or `reviewer file-list mismatch`, then reconcile missing files and extra files against the controller list and keep status INCOMPLETE until the conflict is resolved or explicitly deferred.
   - **Always** launch independent subagents to apply the [code-simplifier](../code-simplifier/SKILL.md) skill to the files in `review_scope_files`. Scale based on the number of changed files:
     - **≤5 files**: launch 1 agent covering all changed files
     - **>5 files**: partition files into non-overlapping groups (by module, directory, or logical area) and launch one agent per group in parallel. Each file must appear in exactly one agent's scope — overlapping scopes cause conflicting writes.
   - **Always** launch 3 review agents in parallel using [agents/code-reviewer.agent.md](agents/code-reviewer.agent.md), covering simplicity/DRY, bugs/correctness, and project conventions/abstractions.
   - Inside `Code Review Findings`, use this exact coverage block:

     ```text
     Review Scope Coverage
     - Total Changed (Uncommitted) Files: <count>
     - Total Reviewed Files: <count>
     - Missing Files: <count>
     - Missing File List: <paths or none>
     - Excluded Files: <paths including .gitignore and deleted files, or none>
     - Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval)
     ```

   - If `Missing Files > 0`, code review is incomplete until the gap is reviewed or explicitly deferred.
   - Consolidate findings and call out the highest-severity issues to fix.

8. Finish with completion validation:
   - verify all required tasks are complete
   - confirm the delivered work matches the specification and technical plan
   - confirm tests pass and coverage expectations are met
   - report final status with completed work, blockers, and any deferred items

## Safety Rules

- Never use destructive git or filesystem commands unless the user explicitly asks.
- Do not revert unrelated working-tree changes.
- If unrelated changes appear and conflict with the current phase, pause and ask how to proceed.
- Keep edits focused on the files required by the active tasks.
