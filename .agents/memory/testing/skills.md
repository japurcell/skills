---
type: Testing Guidance
description: Test and validation guidance for skills under `skills/`
---

# Skills - Testing

- Run `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>` after changing a skill definition, except for the explicitly scoped `dotnet-upgrade` document review below.
- If packaging behavior changed, run `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`.
- If a skill ships `evals/grade_benchmark.py` and you edited it, run `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`.
- If benchmark grading behavior changed, run `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>`.
- Treat `skills/*-workspace/**/outputs/` as generated artifacts, not maintained source.

## dotnet-upgrade document review

The approved acceptance scope is document review and non-mutating JSON/whitespace checks. Review the provenance ledger, bundled navigation, evidence scope, exact invocation controls and six paper scenarios. Parse `references/provenance/source-map.json` and `evals/evals.json` with `python3 -m json.tool`; check scoped diffs with `git diff --check`. Run `./scripts/lint-okf.py` for canonical agent-document changes.

Do not run `quick_validate.py`, archive packaging, live models, benchmarks, trial upgrades, application commands or installers as acceptance gates. The requested frontmatter incompatibility is retained, not waived as a passing result. The integrated document-only acceptance record is [references/document-review.md](../../../skills/dotnet-upgrade/references/document-review.md); it covers ledger, navigation and paper scenarios, not migration behavior, refreshed vendor facts or live client enforcement.
