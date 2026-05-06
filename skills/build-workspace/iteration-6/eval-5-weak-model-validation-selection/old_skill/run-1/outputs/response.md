Manager (lean handoff):
- Invoke addy-context-engineering and subagent-model-selection, then dispatch with implementer-prompt.
- Provide: task text ("Run relevant validation for changes touching scripts/addy-install.sh and skills/build/evals/grade_benchmark.py"), success criteria (exact commands run, outputs, grading.json produced if applicable, plan/todo updated, status DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT), constraints (no commits, no manager-side pre-solving, run in isolated env), and only the two file hints.

Concrete validation to hand:
- bash -n scripts/addy-install.sh
- shellcheck scripts/addy-install.sh (if available)
- python3 -m py_compile skills/build/evals/grade_benchmark.py
- python3 skills/build/evals/grade_benchmark.py <run-dir> (per docs/benchmarking.md)

Implementer verification strategy to avoid fallback:
- Infer the slice’s surface/stack from filenames and code (shell → shell checks; .py → Python checks).
- Run narrow, stack-matching checks (static syntax/lint, then minimal dry-run in a temp/isolated env, then run grade_benchmark on canonical eval dir).
- Record exact commands and outputs in the report.
- Keep verification ownership with the implementer; only re-dispatch to a stronger model if BLOCKED.
