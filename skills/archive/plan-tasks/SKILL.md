---
name: plan-tasks
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
argument-hint: <skip_design_phase:true|false>
---

# Plan Tasks

## Inputs

- `$skip_design_phase` (optional, default: `false`): Whether to skip the design phase.

## Workflow

1. Invoke the `addy-planning-and-task-breakdown` skill.
2. Read the existing spec (SPEC.md or equivalent) and the relevant codebase sections.
3. Enter plan mode — read only, no code changes
4. Unless `$skip_design_phase=true`, [Design the architecture and implementation approach](#architecture-design)
5. Identify the dependency graph between components
6. Slice work vertically (one complete path per task, not horizontal layers)
7. Write tasks with acceptance criteria and verification steps
8. Present the plan for human review

## Architecture Design

**Goal**: Design implementation approaches with different trade-offs.

1. Invoke the `addy-source-driven-development` skill to ensure that every implementation decision is grounded in up-to-date, official documentation.
2. Launch N parallel `code-architect` subagents where N is determined by the complexity and scope of the feature.
3. Each agent should design a different implementation approach with a clear rationale, citations, trade-offs, and potential risks. For example:
   - Minimal changes: the smallest possible change to implement the feature
   - Clean architecture: the most maintainable and extensible design, even if it requires more upfront work
   - Pragmatic balance: a middle ground that balances maintainability with development speed
4. Present a recommendation; include multiple options only when the choice is meaningful.
5. Ask the user to choose only when there is a real product or architectural fork; otherwise recommend the best path and proceed.

## Output

1. Determine `$OUTPUT_PATH`: if a spec file was provided, use the same directory; otherwise, use `.agents/scratchpad/<feature-name>`.
2. Save the plan to `$OUTPUT_PATH/plan.md`.
