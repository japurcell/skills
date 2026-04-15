## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Inspected the uncommitted diff and confirmed only `app.py` and `README.md` changed.
- Reviewed the full archive handler to trace request input into the subprocess sink.
- Verified the diff introduced `shell=True` and string interpolation for the user-controlled `target` value.
- Excluded the README token example from findings because documentation-only issues are out of scope.
- Reported one HIGH-confidence command injection issue in the request handler.
