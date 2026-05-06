# Handoff

## Goal
- Finish and harden the authentication service so the test suite remains green: implement remaining functions in src/auth/service.ts (token creation/refresh, password verification, and error handling).

## Current Status
- Done: Tests phase completed; existing tests passed at last run.
- In progress: src/auth/service.ts contains unimplemented TODOs and small edge-case gaps.
- Next up: Implement the remaining logic in src/auth/service.ts and run the unit tests locally.

## Decisions and Constraints
- Follow repository AGENTS.md conventions (no secrets, run tests before committing, ask on ambiguous requirements).
- Keep changes scoped to src/auth/ and related tests; avoid touching unrelated modules.

## Relevant Files
- `src/auth/service.ts` — primary file to modify; contains TODOs and the functions the tests exercise.
- `.agents/scratchpad/feature-auth/plan.md` — active plan and history for this feature; use for context and previous decisions.
- `AGENTS.md` — project-wide rules and conventions to obey.
- `src/auth/*.test.ts` (or nearby test files) — tests to run after changes; they verify expected behavior and will reveal regressions.

## Open Questions or Blockers
- None known. If tests fail after edits, capture the failing test and error output in the next handoff.

## Recommended Next Step
- Edit `src/auth/service.ts` to implement the TODO'd functions (token refresh, password check, error translation). Run `npm test` and fix any failing assertions. Document any new decisions in the feature plan or next handoff.
