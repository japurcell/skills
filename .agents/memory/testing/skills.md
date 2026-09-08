---
coverage: Test and validation guidance for skills under `skills/`
---

# Skills - Testing

- Run `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>` after changing a skill definition.
- If packaging behavior changed, run `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`.
- If a skill ships `evals/grade_benchmark.py` and you edited it, run `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`.
- If benchmark grading behavior changed, run `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>`.
- Treat `skills/*-workspace/**/outputs/` as generated artifacts, not maintained source.

## Subagent model router

Run `python3 -m unittest discover -s skills/subagent-model-router/evals -p 'test_*.py'` for grader changes or catalog tier changes. These tests verify accepted/rejected routing decisions, including unknown models, capability floors, fallback availability, and environment failures. They do not establish comparative model quality; default-model quality claims require representative live evaluations.
