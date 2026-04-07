## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the current uncommitted git diff in the target repo
- reviewed the changed request handler in app.py with line numbers for exact references
- checked the README change and found the security-relevant regression in subprocess invocation
