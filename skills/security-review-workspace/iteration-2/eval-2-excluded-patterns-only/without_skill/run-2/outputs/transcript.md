## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/excluded-patterns-only as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the current uncommitted diff for README.md, app.py, and tests/test_runner.py
- reviewed surrounding context in app.py to confirm there was no exploitable auth, file access, command execution, or data exposure path
- excluded README.md because documentation findings are out of scope under the snapshot skill
- excluded tests/test_runner.py because test-only code is out of scope under the snapshot skill
- did not report the app.py additions because they map to excluded categories in the snapshot skill, not concrete HIGH or MEDIUM findings
