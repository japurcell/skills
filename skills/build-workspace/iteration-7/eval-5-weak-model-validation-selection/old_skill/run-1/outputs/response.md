**Manager handoff:** Use the implementer prompt with a **lean handoff** and **dispatch immediately** once the task is clear. Hand over only:
1. task text and success criteria,
2. known constraints / validation commands,
3. only already-known file hints: `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`.

Do **not pre-read** more files or **draft the solution**. For this slice, the manager should include the known stack-specific commands: `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`, `python3 -m py_compile skills/build/evals/grade_benchmark.py`, and if grader behavior changes, `python3 skills/build/evals/grade_benchmark.py skills/build-workspace/<iteration-dir>`. Repo discovery, pattern lookup, first-pass design, and verification stay with the implementer. This is bounded shell/Python work, so a fast-tier implementer model is reasonable.

**Implementer verification:** The implementer **owns verification** and should **infer the slice’s surface and stack** from the filenames before choosing checks. `.sh` means shell validation (`bash -n` plus `bash scripts/test-addy-install.sh`); `.py` means Python validation (`python3 -m py_compile`, plus a real `run grade_benchmark` invocation if grader logic changed). Pick the narrowest matching checks for the files actually changed, instead of generic frontend commands.
