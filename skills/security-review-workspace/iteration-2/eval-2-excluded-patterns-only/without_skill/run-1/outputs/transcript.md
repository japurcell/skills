## Eval Prompt

Review the pending changes in /home/adam/.agents/skills/security-review/evals/files/excluded-patterns-only as a security engineer. Write markdown findings to findings.md. If there are no HIGH or MEDIUM findings, write exactly 'No HIGH or MEDIUM findings.'

## Notes

- inspected the uncommitted diff in README.md, app.py, and tests/test_runner.py
- checked the Flask handler for reportable input-validation or code-execution issues under the snapshot skill rules
- excluded README.md because documentation findings are out of scope
- excluded the shell command change because it is confined to a unit-test file, which the snapshot skill excludes
- excluded the user-controlled regex and log line because regex injection, regex DoS, and log spoofing are explicitly excluded
