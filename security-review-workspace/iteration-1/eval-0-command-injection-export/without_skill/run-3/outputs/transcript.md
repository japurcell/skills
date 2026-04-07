## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the uncommitted git diff and identified changes in `app.py` and `README.md`
- verified `target` is sourced from request JSON and passed into the subprocess command string
- confirmed `shell=True` makes shell metacharacters in `target` executable by the server shell
- treated the README change as non-security-relevant compared with the code execution issue in `app.py`
