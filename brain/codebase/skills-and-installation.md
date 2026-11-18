# Skill sources and installation

- Published sources are `skills/default/` and opt-in `skills/forest-service/`. Archived bundles live under `skills/archive/`. Installers exclude them, and active skills, agents, and references must work independently of them. Repository workflows use `.agents/skills/`.
- Scope skill improvement proposals and edits to repository-maintained skills. Exclude every skill imported by [import-skill-repos.sh](../../scripts/import-skill-repos.sh) or [addy-install.sh](../../scripts/addy-install.sh), including renamed destinations under `skills/default/`.
- Use [create-skill](../../skills/default/create-skill/SKILL.md) for bundle naming, frontmatter, and evaluation guidance.
- `handoff` and `exec-plans` remain independently usable, including separate eval bundles. Neither references or depends on the other; repository notes may link both. Maintain their graders through each workflow's own evaluation README; runtime skill instructions do not load evaluation guidance.
- `exec-plans` owns shared planning rules and never references its `execplan-implement` consumer.

Evidence: installers, checked 2026-10-20. Recheck when installation or packaging changes.
