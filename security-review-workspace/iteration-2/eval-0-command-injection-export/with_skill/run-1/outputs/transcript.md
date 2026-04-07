## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Inspected the uncommitted diff and confirmed only `app.py` introduces executable behavior changes.
- Read the full archive handler to trace `request.json["target"]` into `subprocess.run()`.
- Verified the diff switched from argument-list execution to a shell string with `shell=True`, creating a direct command-injection path.
- Ignored the README-only change for findings because it does not introduce executable code.
