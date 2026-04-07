## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/command-injection-export as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- Read and followed the security-review skill instructions before starting the review.
- Inspected the repo's uncommitted diff and confirmed only `app.py` changed in executable code; `README.md` changes were documentation-only.
- Compared the current subprocess call against the prior safe argument-vector form shown in the diff.
- Verified that user-controlled `request.json["target"]` now flows into a shell command string with `shell=True`, creating a concrete command-injection path.
- Recorded one HIGH finding for authenticated arbitrary command execution and wrote the report to `findings.md`.
