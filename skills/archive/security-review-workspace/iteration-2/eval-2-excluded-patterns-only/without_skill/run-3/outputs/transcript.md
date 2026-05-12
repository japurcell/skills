## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/excluded-patterns-only as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the pending changes in app.py for concrete exploitable input-handling issues
- confirmed the added logging and user-supplied regex usage fall under excluded log spoofing and regex-related patterns
- checked tests/test_runner.py and excluded the shell invocation because the file is only used for tests
- checked README.md and excluded the token example because it is documentation-only
