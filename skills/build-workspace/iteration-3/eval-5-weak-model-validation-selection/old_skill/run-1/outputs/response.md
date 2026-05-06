Manager: invoke addy-context-engineering + subagent-model-selection and dispatch an implementer with implementer-prompt.md. Hand over a lean packet: one-line task, explicit machine-checkable acceptance criteria, constraints (no commits, runtime env), exact file hints (scripts/addy-install.sh, skills/build/evals/grade_benchmark.py), a small deterministic fixture, and canonical CLI verification commands.

Examples of verification commands to include (manager supplies fixtures/thresholds):
- bash scripts/addy-install.sh  (expect exit code 0)
- python3 skills/build/evals/grade_benchmark.py <fixture> --output /tmp/out.json (expect exit 0)
- python3 -c "import json;print(json.load(open('/tmp/out.json'))['score']>=0.75)"
- pytest -q (relevant tests)

Implementer: follow implementer-prompt (TDD). Choose the lowest-level, automated checks (exit codes, unit tests, parsing JSON/golden fixtures) and write failing tests first that assert those conditions. That forces deterministic CLI/tests-based verification and prevents weaker models from falling back to vague GUI/frontend steps.
