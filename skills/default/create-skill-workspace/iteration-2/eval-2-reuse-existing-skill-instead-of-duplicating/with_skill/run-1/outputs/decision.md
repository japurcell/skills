# Decision

Refine **`create-plan`**; do **not** create a new `plan-maker` skill.

## Why

- The request matches `create-plan` almost exactly: it already starts from a spec file, reads local planning conventions, writes `plan.md` plus supporting planning artifacts, and hands off cleanly to `/create-tasks`.
- The brief explicitly says there is no new file layout or novel workflow. That means the gap is trigger clarity and output specificity, not missing capability.
- Nearby skills such as `create-tasks`, `plan-tasks`, and `addy-planning-and-task-breakdown` cover downstream task slicing or generic planning guidance, not the requested spec-to-artifacts workflow.

## Refinement choice

Tighten `create-plan` so it triggers more reliably on requests like:

- "write `plan.md` and research notes"
- "read the repo's planning conventions before implementation"
- "make this spec ready for task breakdown"

Also make the skill's output contract and validation guidance more explicit so it avoids vague planning summaries.

## Saved files

- `outputs/create-plan/SKILL.md`
- `outputs/create-plan/evals/evals.json`

## Guardrails satisfied

- Existing skill name preserved: `create-plan`
- Downstream task-breakdown skill acknowledged: `create-tasks`
- No duplicate `plan-maker/` skill created
