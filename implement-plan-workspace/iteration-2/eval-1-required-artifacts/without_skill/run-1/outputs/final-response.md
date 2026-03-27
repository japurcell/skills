Loading implementation context for `plan_file=.agents/scratchpad/feature-export/plan.md`:

- Read required artifact: `plan.md` -> found
- Read required artifact: `tasks.md` -> **missing**

`/implement-plan` is blocked because `tasks.md` is a required input for task phases, dependencies, and execution order parsing.

Execution is halted before phase execution (Setup/Tests/Core/Integration/Polish).

Please run `/create-tasks` to regenerate `tasks.md` (planning artifacts), then rerun `/implement-plan`.