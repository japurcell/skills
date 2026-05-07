Hand the implementer only the lean build-wave packet:
- task text: update `scripts/addy-install.sh` and `skills/build/evals/grade_benchmark.py`
- success criteria: implement the plan’s requested behavior with minimal changes, leave the tree dirty, and report files changed plus exact validation run
- known constraints: no commits; do not expand scope; use only already-known file hints and relevant validation

For verification, the implementer should infer the surface first. Because this is shell + Python, choose narrow shell/Python validation (targeted script checks, unit/eval tests, and the smallest relevant repo test command) rather than generic frontend commands. Only use frontend-style commands if the task is actually frontend work.
