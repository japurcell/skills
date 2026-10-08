---
name: spec-to-tasks
description: Use when the user wants to break down a SPEC, PRD, plan, or raw requirements into independent, bounded tasks. Do not use to write the spec or implement tasks.
---

# /spec-to-tasks

Turn a spec into a `tasks.json` manifest with explicit prerequisites, source coverage, worker context, task type, and applicable verification. Keep each assignment small enough to understand while preserving its full behavior and acceptance contract.

## Inputs

Required, one of:

- `spec`: path to a spec, PRD, or plan file
- Spec, PRD, or plan text already in the conversation

Optional:

- `output_directory`

## Output path

Write valid JSON only to the selected file. Do not put Markdown, comments, explanations, or trailing commas in `tasks.json`.

Use this path precedence:

1. `output_directory/tasks.json`, if `output_directory` is provided
2. `tasks.json` beside `spec`, if `spec` is a file path
3. `.agents/scratchpad/tasks.json`

Create directories as needed. Paths in task references and `workingDirectory` are repository-relative. For source material outside the repository or in the conversation, capture the relevant text with the inline reference form in [task-schema.md](references/task-schema.md); never put an absolute path into the manifest.

## Workflow

1. Activate the `delegate-to-subagents` skill so that you delegate tasks to the most suitable subagents for each task type when useful. This skill produces a manifest; it does not schedule execution or add batching fields.
2. Resolve the source and output path. If no spec source is available, ask the user and stop.
3. Read the spec if it is not already in context. For a `/prd`-style PRD, follow [prd-handling.md](references/prd-handling.md).
4. Extract the project and feature, stories, functional requirements, technical decisions, acceptance criteria or Definition of Done, test plan, mandatory sequence, edge cases, negative states, fallback behavior, integration invariants, and out-of-scope items.
5. Activate the `explore` skill if repository context is needed and missing. Use only existing commands, paths, and conventions that you can verify.
6. Resolve conflicts before decomposition. Prefer mandatory order, acceptance criteria, technical decisions, functional requirements, then narrative text. For an unresolved architectural choice that is within the task's authority, create a bounded `decision` task that records the decision and evidence, and make dependent work wait for it. If a choice requires user approval or cannot safely be resolved within the provided authority, ask and stop without writing the manifest.
7. Size the work by behavioral scope, unresolved decisions, coupled state, environment uncertainty, and verification burden. Give each task one central outcome. Split independently deliverable behaviors and unrelated failure families. Keep code and its necessary tests together; keep negative cases with the behavior they constrain. Do not split an indivisible difficult invariant into partial tasks that could be marked complete. Explain remaining reasoning risk and bounded entry points in `description` or `designGuidance`; do not invent numeric difficulty scores or time/token limits.
8. Build an explicit dependency graph. Each `dependsOn` edge must name an outcome or artifact the dependent task needs, or enforce mandatory source order. Reading an existing task definition does not require that task's implementation to pass. A dependent task is eligible only after every listed prerequisite passes. Keep recommended order in priority only. Priority is an ordering hint, not authorization to bypass prerequisites. Reject unknown IDs, self-edges, duplicate edges, and cycles. No dependency edge does not prove that tasks can safely run concurrently.
9. Use implementation tasks for end-to-end behavior. Add `integration` tasks or checks when separate tasks must compose to preserve shared invariants. Make the integration proof explicit, link it to the current source contract, and depend on the contributing work. Passing component tasks alone does not pass the integrated behavior.
10. Populate every task with all existing task fields and the complete enriched contract: `dependsOn`, nonempty `sourceRefs`, `requiredContext`, `taskType`, and `verification`. Use stable source headings or requirement IDs when available. References identify requirements; context entries name what the worker must read and why. The fields are not interchangeable. See [task-schema.md](references/task-schema.md).
11. Define verification before saving. Include at least one required check that directly establishes the task outcome, an explicit typecheck classification for every task, and each other relevant check. Use known repository commands and observable expected results. If a required check is manual, give a concrete procedure and expected evidence. If verification is unresolved because of a host or access blocker, retain any known command; use `command: null` only when no command is known. An unresolved check cannot count as passed and the manifest is not ready. Do not invent commands or reclassify a failing applicable check as inapplicable.
12. Apply [validation.md](references/validation.md), then save `tasks.json`. Complete coverage and manifest reviews whose inputs already exist during authoring; create later review tasks only when their evidence depends on future work. Do not claim readiness if context is missing, the graph is invalid, or a required check remains unresolved.

## Task shape

Keep the top-level fields `project`, `branchName`, `description`, and `tasks`. Every task must use the complete shape in [task-schema.md](references/task-schema.md). New tasks start with `passes: false` and `notes: ""`; when updating existing tasks, preserve their IDs, pass values, notes, and completion evidence.

Implementation tasks remain vertical slices through the layers required for their behavior. Decision, verification, integration, and documentation tasks may have other outcomes, but each must still be independently valuable and verifiable. A task type does not justify a code-only or test-only fragment with no independent value.

For UI-visible behavior, include “activate the `playwright-cli` skill” in the task's browser-verification instructions and describe the concrete scenario. Backend-only tasks must not include UI or browser wording.

## Final response

After saving, report the task count, output path, and readiness. Say `ready` only when references resolve, each task has the context it needs, the dependency graph is valid, and no required verification remains unresolved. If a required check is unresolved, report `needs follow-up` and identify it. If missing source or context or an invalid graph prevents a valid manifest, do not save it; state that it was not saved and what must be resolved.
