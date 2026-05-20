PROJECT CONTEXT:
- Goal: Fix the login timeout in src/auth_service.py so it matches the spec (tests expect 15 minutes).
- Stack: Python
- Rules loaded: .github/copilot-instructions.md, .cursorrules, .cursor/rules/quality.md, .windsurfrules, AGENTS.md
- Spec: tests/test_auth_service.py asserts: "assert session_timeout_minutes() == 15"
- Constraints: Do not change code; follow repo rules; prefer unit tests before code changes.
- Files: src/auth_service.py, tests/test_auth_service.py
- Pattern: tests/test_auth_service.py (unit test asserting expected timeout)
- Gotchas: src/auth_service.py currently sets SESSION_TIMEOUT_MINUTES = 60, conflicting with the test/spec; since code must not be changed, determine whether to update config, environment, or tests; run unit tests to verify.
