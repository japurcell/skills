## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read and followed the security-review skill instructions before inspecting the repo.
- Reviewed the current uncommitted git diff and confirmed the only code change in `app.py` switches `subprocess.run` from argv execution to shell execution.
- Read the full archive handler to verify `target` is sourced directly from request JSON and is reachable by authenticated callers.
- Checked the README diff but did not report it because documentation changes are excluded and did not change the code-level risk.
