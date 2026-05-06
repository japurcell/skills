Manager pre-dispatch actions:
- Confirm task clarity and acceptance criteria; ensure validation commands and repo rules are known.
- Invoke addy-context-engineering and subagent-model-selection; pick the next pending task.
- Prepare a lean handoff (do NOT pre-implement).

Handoff contents (lean):
- Task text and explicit success criteria
- Known constraints and validation commands to run
- File hints already named in the plan
- Note: DO NOT commit changes; user will commit

Belongs to implementer:
- Discover relevant files/patterns, write a failing test, implement minimal change, run tests/build, and report status (DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT) with files changed and test results.