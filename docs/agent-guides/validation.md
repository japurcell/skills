# Validation commands

There is no single repo-wide test command. Run the narrowest command that exercises the area you changed.

## Skill validation and packaging

- `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`: validate a skill definition
- `PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist`: package a skill into a `.skill` archive

## Other targeted checks

- `bash scripts/test-addy-install.sh`: exercise the addy importer’s skill-selection and dependency-copying behavior
- `bash skills/agent-sop-author/validate-sop.sh path/to/file.sop.md`: validate an Agent SOP file
- `python3 skills/security-review/evals/grade_reports.py <run-dir>`: grade a `security-review` eval run

## Workflow

- If you change a helper script, run the most specific command that covers that script instead of looking for a nonexistent monorepo test runner.
