# Skill sources and installation

- Published sources are `skills/default/` and opt-in `skills/forest-service/`; repository workflows use `.agents/skills/`.
- Forest Service installation supports `--forest-service`/`--fs`, `--no-forest-service`, and `INSTALL_FOREST_SERVICE_SKILLS`.
- Use [create-skill](../../skills/default/create-skill/SKILL.md) for bundle naming, frontmatter, and evaluation guidance.
- `handoff` and `exec-plans` remain independently usable, including separate eval bundles. Neither references or depends on the other; repository notes may link both. Maintain their graders through each workflow's own evaluation README; runtime skill instructions do not load evaluation guidance.
- `exec-plans` owns shared planning rules and never references its `execplan-implement` consumer. Neither ExecPlan skill references `spec-to-tasks` or encodes its manifest schema.
- The task schema owns the full manifest contract; worker intake stays aligned. The Ralph loop stays blind to manifest contents and task selection.

Evidence: installers, checked 2026-10-20. Recheck when installation or packaging changes.
