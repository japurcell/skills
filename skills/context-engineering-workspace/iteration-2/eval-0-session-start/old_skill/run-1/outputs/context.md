PROJECT CONTEXT:
- Goal: Fix the login timeout in src/auth_service.py so it matches the spec (15 minutes) without changing code.
- Stack: Python
- Rules loaded: /home/adam/dev/personal/skills/skills/context-engineering-workspace/skill-snapshot-old/SKILL.md, /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/docs/spec.md, tests in /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/tests/
- Spec: "Web sessions created by `src/auth_service.py` should expire after 15 minutes of inactivity." (docs/spec.md)
- Constraints: Do not change source files; follow repo tests and spec; surface ambiguities before making code changes.
- Files: /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/src/auth_service.py (target), /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/src/session_service.py (example), /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/tests/test_auth_service.py (test), /home/adam/dev/personal/skills/skills/context-engineering/evals/files/session-start-fixture/docs/spec.md (spec)
- Pattern: src/session_service.py shows DEFAULT_TIMEOUT_MINUTES = 15 and build_session() -> {"timeout_minutes": DEFAULT_TIMEOUT_MINUTES}; follow this precedent.
- Gotchas: src/auth_service.py currently sets SESSION_TIMEOUT_MINUTES = 60; tests expect 15. The user forbids changing code, so fix will likely be a configuration, initialization, or CI/test adjustment; surface options and ask before applying code changes.
