---
name: implement-plan
description: Execute an existing implementation plan end-to-end from a plan file, including checklist gating, prerequisite validation, phase-by-phase task execution, TDD-first delivery, task checkbox updates, code review, and completion validation. Use this whenever the user asks to run or resume implementation from planning artifacts (such as plan.md and tasks.md), explicitly mentions /implement-plan, or wants feature work executed in ordered phases with dependency-aware parallelization and checkpoints. Prefer this skill over generic coding/review flows when the request is to execute an already-generated plan rather than create a new plan or only analyze code.
disable-model-invocation: true
---

# Implement plan

## Inputs

You receive these parameters in your prompt:

- **plan_file** (required): The path to the plan file to implement.

## Context

- Read plan_file into context if it isn't already.
- Derive the feature directory from plan_file and use it as the base for related artifacts.

## Required Output Contract

Use this structure in your user-facing progress and completion updates so execution is auditable:

1. `Checklist Gate`
2. `Implementation Context Loaded`
3. `Phase Execution`
4. `Code Review Findings`
5. `Completion Validation`

Use Markdown section headers for these exact section names so downstream evaluation can verify structure reliably.

For each section, include concise evidence (files read, tasks completed, tests run, blockers).

## Outline

1. **Check checklist status** (if `<feature-dir>/checklists/` exists):
   - Scan all checklist files in that directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 2

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 2

   - **If checklists directory does not exist**:
     - Report that no checklist gate is present
     - Continue to step 2

2. Load and analyze the implementation context:
   - **REQUIRED**: Read `tasks.md` for the complete task list and execution plan
   - **REQUIRED**: Read `plan.md` for tech stack, architecture, and file structure
   - **IF EXISTS**: Read `data-model.md` for entities and relationships
   - **IF EXISTS**: Read `contracts/` for API specifications and test requirements
   - **IF EXISTS**: Read `research.md` for technical decisions and constraints
   - **IF EXISTS**: Read `quickstart.md` for integration scenarios
   - If either `tasks.md` or `plan.md` is missing, stop and instruct the user to run `/create-tasks` or regenerate planning artifacts.

3. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup.
   - Only append missing critical patterns; do not overwrite user-managed ignore files.

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile\* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc\* exists → create/verify .eslintignore
   - Check if eslint.config.\* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc\* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (\*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only.
   **If ignore file missing**: Create with full pattern set for detected technology.

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `*.dll`, `autom4te.cache/`, `config.status`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

4. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

   If no actionable tasks are found, stop and recommend regenerating `tasks.md`.

5. Implement individual phases of the task plan in the correct order using subagents. For each phase:
   - Launch a subagent for each phase with an explicit handoff prompt that includes:
     - Current phase name and ordered task IDs
     - Dependency rules (`[P]` can run in parallel only when files do not overlap)
     - Requirement to apply TDD (tests first, then implementation)
     - Requirement to mark completed tasks as `[X]` in `tasks.md`
     - Expected deliverable: changed files, test results, and unresolved issues
   - The phase subagent must:
     - Respect dependencies by running sequential tasks in order
     - Run `[P]` tasks concurrently only when safe
     - Halt phase execution if a non-parallel task fails
     - Continue remaining independent parallel tasks if one `[P]` task fails
   - After each phase, run a validation checkpoint subagent that confirms:
     - All intended phase tasks were completed or explicitly deferred
     - `tasks.md` status is synchronized with actual completion
     - Required tests for that phase were executed
   - Do not start the next phase until checkpoint passes (or user explicitly approves continuing with known failures).

6. Code review: perform code review using <code_review_instructions>.

7. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan

- Include an explicit `Checkpoint Decision` block using this exact structure:

  ```text
  Checkpoint Decision
  - Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
  - Evidence: <tasks completed, tests run, files changed, blockers/deferments>
  - Next Action: <advance to next phase | resolve blockers | request user approval>
  ```

- Do not advance to the next phase unless the checkpoint decision status permits advancement or the user explicitly approves continuation.
- Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/create-tasks` first to regenerate the task list.

## Implementation Safety Rules

- Never use destructive git or filesystem commands unless the user explicitly asks.
- Do not revert unrelated changes in the working tree.
- If unexpected unrelated changes appear during execution, pause and ask the user how to proceed.
- Keep edits focused on files required by current tasks.

<implementation_execution_rules>

1.  **Setup first**: Initialize project structure, dependencies, configuration
2.  **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
3.  **Core development**: Implement models, services, CLI commands, endpoints
4.  **Integration work**: Database connections, middleware, logging, external services
5.  **Polish and validation**: Unit tests, performance optimization, documentation

</implementation_execution_rules>

<codereview_instructions>

1. Using a subagent, apply the code-simplifier skill to all touched files
   - Exclude .gitignore files
2. Launch 3 code-reviewer agents in parallel that:
   1. Read [agents/code-reviewer.agent.md](agents/code-reviewer.agent.md)
   2. Focus on different aspects: simplicity/DRY/elegance, bugs/functional correctness, project conventions/abstractions for all of the touched files
   3. Excludes .gitignore files
3. Consolidate findings and identify highest severity issues that you recommend fixing

</codereview_instructions>
