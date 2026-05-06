Manager should hand the implementer the implementer-prompt.md plus a lean handoff containing:
- Task text + explicit success criteria (e.g., syntax-check passes; addy-install.sh dry‑run exits 0/idempotent; grade_benchmark.py runs on a small fixture and its output/schema matches expected; touched tests pass).
- Known constraints (no commits, local/ephemeral env, no broad e2e, network limits).
- Exact validation commands and only the file hints (scripts/addy-install.sh, skills/build/evals/grade_benchmark.py).

Implementer verification approach:
- Infer the slice’s surface & stack from the files.
- Run the narrowest checks: syntax checks (bash -n), targeted unit tests, direct CLI runs on small fixtures, and schema/assertion checks of outputs (exit codes + JSON diffs).
- Record exact commands+results in the report. Avoid generic frontend/e2e commands.
