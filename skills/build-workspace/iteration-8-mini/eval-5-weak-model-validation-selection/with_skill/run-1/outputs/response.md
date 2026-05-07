Manager handoff (lean, per Build skill)
- Task text + clear success criteria (what “done” looks like).
- Known constraints + explicit validation commands to run.
- Only already-known file hints (e.g., scripts/addy-install.sh, skills/build/evals/grade_benchmark.py).
- Invoke addy-context-engineering & subagent-model-selection, then dispatch implementer (no repo pre-reading or drafted fixes).

Implementer verification strategy (to avoid weak-model fallback)
- Infer the slice/stack from file types (shell → shell checks; .py → Python checks).
- Prefer narrow stack checks, e.g.:
  - Shell: bash -n scripts/addy-install.sh; ./scripts/addy-install.sh --help (smoke run).
  - Python: python3 -m py_compile skills/build/evals/grade_benchmark.py; run the repo’s pytest or a small harness that calls grade(eval_name, response_text).
- Explicitly avoid generic frontend commands (no npm run test/build unless files indicate frontend).
- Record exactly which commands were run and their outputs in the verification context the manager will forward to reviewers.

Short checklist to hand the implementer
- Task + success criteria
- Concrete validation commands (copy the two examples above)
- File hints: scripts/addy-install.sh, skills/build/evals/grade_benchmark.py
- Note: implementer owns discovery, chooses matching validators, and must record verification results.
