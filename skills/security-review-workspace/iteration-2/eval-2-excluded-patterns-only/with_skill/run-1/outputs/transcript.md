## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/excluded-patterns-only as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the pending diff in app.py, README.md, and tests/test_runner.py
- checked whether user-controlled regex compilation, request logging, and shell execution were reachable in production code
- excluded the README secret example, test-only shell invocation, regex injection/ReDoS, and log spoofing per the skill rules
