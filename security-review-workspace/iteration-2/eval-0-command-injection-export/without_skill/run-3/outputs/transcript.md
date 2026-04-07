## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the pending git diff and confirmed only `README.md` and `app.py` changed
- read the full archive handler to trace `request.json["target"]` into `subprocess.run(...)`
- confirmed the change introduced `shell=True` with direct string interpolation, creating a concrete command injection path
- excluded the README change from findings because documentation files are out of scope for reporting
