## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Inspected the uncommitted git diff for the review repo.
- Read the full `/archive` handler in `app.py` to confirm request reachability and data flow.
- Verified that `request.json["target"]` now flows into a shell command with `shell=True`.
- Checked the README change and found the material security issue is the subprocess change in `app.py`.
