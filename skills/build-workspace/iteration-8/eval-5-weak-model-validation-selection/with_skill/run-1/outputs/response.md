**Manager handoff:** dispatch immediately with a **lean handoff**; **do not pre-read** more files and **do not draft the solution**. Hand the implementer only:
1. **Task + success criteria:** make the planned change touching `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`, then report exact commands run, results, and files changed.
2. **Known constraints / validation commands:** `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`; `python3 -m py_compile skills/build/evals/grade_benchmark.py`; if grader behavior changes, `python3 skills/build/evals/grade_benchmark.py skills/build-workspace/<iteration-dir>`.
3. **Already-known file hints:** `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`.

**Implementer verification selection:** the **implementer owns verification**. They should **infer the slice/stack** from the file types first—this slice is Bash installer work plus a Python grader—then run the narrowest matching shell/Python checks, adding the `grade_benchmark.py` run only if the grading behavior changed. That keeps a weaker model anchored to stack-specific validation instead of drifting into generic frontend checks.
