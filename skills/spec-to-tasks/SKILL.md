---
name: spec-to-tasks
description: Use when the user wants to break down a SPEC, PRD, plan, or raw requirements into independent, vertical-slice tasks. Do not use to write the spec or implement tasks.
---

# /spec-to-tasks

Break a spec into independently-grabbable issues using **vertical slices** (tracer bullets).

## Inputs

Required, one of:

- `spec`: path to a spec/PRD/plan file
- Spec/PRD/plan text already in conversation

Optional:

- `output_directory`

## Output path

Write valid JSON only: no markdown, comments, explanations, or trailing commas.

Path precedence:

1. `output_directory/tasks.json`, if `output_directory` is provided
2. `tasks.json` beside `spec`, if `spec` is a file path
3. `.agents/scratchpad/tasks.json`

Create directories as needed.

## Workflow

1. Activate or load the `subagent-model-router` skill and delegate tasks to the most suitable subagents whenever useful.
2. Resolve the spec source and output path. If no spec source is available, ask the user and stop.
3. Read the spec if not already in context.
4. If the input is a `/prd`-style PRD, follow `references/prd-handling.md`.
5. Extract project/feature, user stories, functional requirements, technical decisions, acceptance criteria / Definition of Done, testing plan, rollout order, edge cases, and out-of-scope items.
6. If repo context is needed and missing, activate or load the `explore` skill to inspect relevant files.
7. Resolve conflicts before splitting work:
   - Prefer, in order: mandatory order, acceptance criteria/Definition of Done, technical decisions, functional requirements, narrative text.
   - Document safe resolutions in task descriptions or `designGuidance`.
   - If unsafe to resolve, ask the user and stop without writing.
8. Identify any small, necessary prefactoring that would reduce risk or simplify later vertical slices.
9. Break the spec into **tracer bullet** tasks. Each task is a thin **vertical slice** that cuts through the necessary layers end-to-end, not a horizontal slice of one layer.
10. Apply `references/task-schema.md`.
11. Validate with `references/validation.md`.
12. Save `tasks.json`.

## Vertical slice rules

Each task must:

- Deliver a narrow, complete, end-to-end behavior through all needed layers.
- Be independently implementable by one agent.
- Be independently demoable or verifiable.
- Include tests or verification when inferable.
- Map explicit requirements, edge cases, and negative states to acceptance criteria.
- Avoid schema/API/UI/test-only horizontal slices unless independently valuable.

Required prefactoring may precede dependent feature slices if it meets the same verification standard.

## Acceptance criteria rules

Each task must include:

- Concrete behavior-focused validation.
- `Typecheck passes`.

When inferable, include exact commands from the spec or repo. For example:

- `npm test`
- `pnpm typecheck`
- `pytest path/to/test.py`
- `./scripts/verify-hooks.test.sh`

Do not invent commands, files, paths, or conventions.

If commands are unknown, say so in the task description.

UI-visible changes must include:

- `Verify in browser using playwright-cli skill`

Backend-only tasks must avoid UI/browser wording such as page, click, card, button, modal, or browser.

## File inference

In `filesLikelyTouched`, include confidently inferable files the task will create or edit, including source, tests, configs, migrations, fixtures, scripts, and command targets.

If paths cannot be inferred confidently, use `[]` and mention uncertainty in the task description when useful.

## Final response

After saving, respond only with:

- task count
- output path
- whether the file is ready for `/prd-ralph`
