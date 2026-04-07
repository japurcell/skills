## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read /home/adam/.agents/skills/security-review/SKILL.md and scoped the review to the uncommitted diff.
- Inspected git status and the diff for the repo under review; only `app.py` and `README.md` were modified.
- Compared the new `subprocess.run(..., shell=True)` call in `app.py` against the base version that used an argv list.
- Checked the endpoint context, including the token gate and the attacker-controlled `request.json["target"]` flow into the shell command.
- Excluded README-only concerns from findings because the review guidance says not to report documentation-only issues.
