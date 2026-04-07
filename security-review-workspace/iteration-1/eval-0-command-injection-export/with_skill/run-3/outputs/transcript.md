## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read /home/adam/.agents/skills/security-review/SKILL.md and followed its HIGH/MEDIUM-only review criteria.
- Inspected the pending git diff and confirmed the only code change in app.py switches subprocess execution from an argument list to a shell command.
- Read the full request handler to verify `request.json["target"]` is user-controlled input that flows into `subprocess.run(..., shell=True)` without validation.
- Reviewed the README change and did not report it because documentation findings are explicitly excluded by the review rules.
