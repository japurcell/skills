## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read and followed the security-review skill instructions before starting the review.
- Scoped the review to the current uncommitted diff in the target repository.
- Inspected the changed handler in app.py and confirmed request input flows into subprocess.run.
- Compared the old list-based subprocess invocation to the new shell-based command string.
- Excluded README-only documentation changes from findings per the review rules.
