# Decision

Reuse and refine `create-plan`; do **not** create a new `plan-maker` skill.

## Why

- The brief matches `create-plan` almost exactly: it already starts from a spec file, reads local planning conventions, writes `plan.md` plus supporting planning artifacts, and hands off cleanly to `/create-tasks`.
- The request explicitly says there is no new file layout or novel workflow. That means the gap is not capability, it is trigger clarity and output specificity.
- `create-tasks` is related, but it is the downstream task-breakdown step after planning, not the replacement for the requested workflow.

## Refinement choice

Tighten `create-plan` so it triggers more reliably on requests like "make this spec ready for task breakdown", "write plan.md and research notes", or "read the repo's planning conventions before implementation", and make the output contract more explicit so the skill avoids vague summaries.

## Saved files

- `outputs/create-plan/SKILL.md`
- `outputs/create-plan/evals/evals.json`
- `outputs/create-plan/references/plan-template.md`

## Guardrails satisfied

- Existing skill name preserved: `create-plan`
- Nearby downstream skill acknowledged: `create-tasks`
- No duplicate `plan-maker/SKILL.md` created
