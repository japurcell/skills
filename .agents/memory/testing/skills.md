---
coverage: Test and validation guidance for skills under `skills/`
---

# Skills - Testing

- Run `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>` after changing a skill definition.
- If packaging behavior changed, run `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`.
- Run `bash skills/agent-sop-author/validate-sop.sh path/to/file.sop.md` when changing Agent SOP validation behavior or expected SOP structure.
- If a skill ships `evals/grade_benchmark.py` and you edited it, run `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`.
- If benchmark grading behavior changed, run `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/<iteration-dir>`.
- Treat `skills/*-workspace/**/outputs/` as generated artifacts, not maintained source.
