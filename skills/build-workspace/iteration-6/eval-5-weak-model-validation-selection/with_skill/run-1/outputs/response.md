Manager handoff (lean):
- Task: "Run relevant validation for changes touching scripts/addy-install.sh and skills/build/evals/grade_benchmark.py."
- Success criteria: bash syntax + linter pass for the script; grade_benchmark.py imports/runs on a small fixture and targeted tests pass; full test-suite passes; verification commands + outputs recorded; no commits.
- Constraints & hints: only these files; implementer owns repo discovery; run in an isolated env.
- Explicit validation commands to run/record: 
  - bash -n scripts/addy-install.sh
  - shellcheck scripts/addy-install.sh (if available)
  - python3 -m pytest -q (or pytest for tests touching grade_benchmark)
  - python3 skills/build/evals/grade_benchmark.py <fixture> > out.json && diff out.json expected.json
- Return status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED and the raw verification log.

Implementer verification selection (to stop weak models falling back to generic frontend commands):
- Infer stack from file types (shell + Python) then choose stack-specific validators (bash/shellcheck; pytest/run script).  
- If no tests exist, add a tiny unit test that exercises the changed behavior and run only that test.  
- Provide exact commands, sample input(s), and expected output(s) in the verification log so verification is concrete (not "run frontend build").  
- If reasoning seems to require a stronger model, invoke subagent-model-selection and re-dispatch with the selected model.
