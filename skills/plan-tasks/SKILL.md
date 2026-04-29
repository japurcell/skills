---
name: plan-tasks
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
---

# Plan Tasks

## Workflow

1. Invoke the `addy-planning-and-task-breakdown` and `subagent-model-selection` skills.
2. Read the existing spec (SPEC.md or equivalent) and the relevant codebase sections.
3. Enter plan mode — read only, no code changes
4. Identify the dependency graph between components
5. Slice work vertically (one complete path per task, not horizontal layers)
6. Write tasks with acceptance criteria and verification steps
7. Add checkpoints between phases
8. Present the plan for human review

## Output

1. Determine `$OUTPUT_PATH`: if a spec file was provided, use the same directory; otherwise, use `.agents/scratchpad/<feature-name>`.
2. Save the plan to `$OUTPUT_PATH/plan.md` and task list to `$OUTPUT_PATH/todo.md`.

## Subagent Guidance

When using subagents:

- Invoke the `subagent-model-selection` skill.
