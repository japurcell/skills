PROJECT CONTEXT:
- Goal: Fix the login timeout in src/auth_service.py so it matches the spec (sessions should expire after 15 minutes of inactivity).
- Stack: Python
- Rules loaded: /home/adam/dev/personal/skills/skills/context-engineering/SKILL.md, /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/AGENTS.md, /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.cursorrules, /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.windsurfrules
- Spec: "Web sessions created by `src/auth_service.py` should expire after 15 minutes of inactivity." (docs/spec.md)
- Constraints: Do not change code; prepare startup context only; follow repo rules (use Python for edits, read targets before editing).
- Files: /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/src/auth_service.py, /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/docs/spec.md
- Pattern: src/auth_service.py defines SESSION_TIMEOUT_MINUTES = 60
- Gotchas: Code sets timeout to 60 minutes (SESSION_TIMEOUT_MINUTES=60) while spec requires 15 minutes; user explicitly forbids changing code, so resolution options include updating configuration, tests, or asking for permission to change code.
