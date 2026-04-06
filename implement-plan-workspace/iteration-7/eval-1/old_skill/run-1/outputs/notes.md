Provenance note

- Controlling workflow: `skills/implement-plan-workspace/iteration-7/skill-snapshot/SKILL.md`
- Eval prompt: missing `tasks.md` while `plan.md` exists for `.agents/scratchpad/feature-export/`
- Response mirrors the skill's required stop behavior during context loading: explicitly report missing `tasks.md`, instruct the user to run `/create-tasks` or regenerate planning artifacts, and state that execution halts before phase execution.
