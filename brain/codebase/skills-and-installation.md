# Skill sources and installation

- Published sources are `skills/default/` and opt-in `skills/forest-service/`; repository workflows use `.agents/skills/`.
- Keep each bundle's `SKILL.md` name/frontmatter consistent with its directory and supported host conventions.
- Never remove `disable-model-invocation: true` merely to satisfy a validator that does not recognize it.
- Benchmark artifacts belong in sibling `<skill>-workspace/` directories, outside published skill bundles.
- Forest Service installation supports `--forest-service`/`--fs`, `--no-forest-service`, and `INSTALL_FOREST_SERVICE_SKILLS`.
- Skill authoring mechanics belong in the maintained create-skill workflow; brain notes hold repository-specific constraints.
- `handoff` and `exec-plans` remain independently usable, including separate eval bundles. Neither references or depends on the other; repository notes may link both. Maintain their graders through each workflow's own evaluation README; runtime skill instructions do not load evaluation guidance.
- `exec-plans` owns shared planning rules and never references its `execplan-implement` consumer. Neither ExecPlan skill references `spec-to-tasks` or encodes its manifest schema.
- The task schema owns the full manifest contract; worker intake stays aligned. The Ralph loop stays blind to manifest contents and task selection.

Evidence: [create-skill](../../skills/default/create-skill/SKILL.md), installers, checked 2026-10-20. Recheck supported metadata and packaging changes. See [skill-evaluation](skill-evaluation.md).
