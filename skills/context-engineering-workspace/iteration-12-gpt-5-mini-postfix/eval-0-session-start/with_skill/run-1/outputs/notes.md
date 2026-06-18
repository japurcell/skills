Rules checked:
- /home/adam/dev/personal/skills/skills/context-engineering/SKILL.md
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/AGENTS.md
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.github/copilot-instructions.md
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.cursorrules
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.cursor
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/.windsurfrules

Rules loaded:
- /home/adam/dev/personal/skills/skills/context-engineering/SKILL.md (local skill under test)

Unavailable paths: none (all checked paths present in repo tree listing)

Files read:
- /home/adam/dev/personal/skills/skills/context-engineering/SKILL.md
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/docs/spec.md
- /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/src/auth_service.py

Notes:
- Spec requires web sessions expire after 15 minutes inactivity.
- src/auth_service.py currently sets SESSION_TIMEOUT_MINUTES = 60.
- Constraint: follow fixture repo instructions (prefer unit test before code change; use Python for edits) when implementing fix.
