## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read the snapshotted skill instructions before reviewing the diff.
- Inspected the current uncommitted git diff and confirmed the only code change is in `app.py`.
- Verified the changed subprocess call now interpolates request data into a shell command with `shell=True`.
- Ignored `README.md` because documentation-only changes are excluded from reporting.
