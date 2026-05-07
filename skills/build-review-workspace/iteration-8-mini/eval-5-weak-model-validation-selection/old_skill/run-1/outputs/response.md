Manager handoff (give the implementer):

- Task: "Run relevant validation for touches to scripts/addy-install.sh and skills/build-review/evals/grade_benchmark.py."
- Success criteria: addy-install.sh passes syntax/linting and runs non-interactively (exit 0) in CI-like env; grade_benchmark.py runs under python3 (or via pytest) and returns exit 0 / produces expected metric file; all verification commands, logs, and failures recorded; no commits.
- Constraints & hints: only these file paths: scripts/addy-install.sh and skills/build-review/evals/grade_benchmark.py. Do routine discovery yourself.

Required validation commands (manager-provided):
- bash -n scripts/addy-install.sh
- shellcheck scripts/addy-install.sh (if available)
- CI=true bash scripts/addy-install.sh > /tmp/addy-install.log 2>&1; test $? -eq 0
- python3 skills/build-review/evals/grade_benchmark.py --help; then run: python3 skills/build-review/evals/grade_benchmark.py > /tmp/grade.log 2>&1; test $? -eq 0
- If tests exist: pytest -q

How the implementer should choose verification (to avoid weaker-model fallback):
- Infer stack (shell + Python). Prefer the narrowest checks: shell syntax/lint + running the install script in a controlled env; Python-level invocation or pytest for the benchmark script.
- Explicitly forbid frontend/browser tooling: any suggestion to validate via npm, browser automation, or generic "frontend" commands must be rejected.
- If delegating to a subagent, use subagent-model-selection and require a model that can execute shell/Python checks (not a weak frontend-focused model).
- Record exactly which commands were run and attach logs for reviewers.
