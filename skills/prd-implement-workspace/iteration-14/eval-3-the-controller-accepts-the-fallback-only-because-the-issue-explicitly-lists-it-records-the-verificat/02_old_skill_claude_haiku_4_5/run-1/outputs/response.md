# Fallback verification acceptance for #7101

The verification subagent reports:
1. `pnpm exec redwood test api/src/functions/users/users.test.ts` — `pnpm: command not found`
2. `yarn rw test api/src/functions/users/users.test.ts` — ✓ passed

## Controller assessment

The child issue's Verification section explicitly lists this fallback:
> if the Redwood CLI is unavailable in the current environment, run `yarn rw test api/src/functions/users/users.test.ts` instead.

This is a **documented fallback**, not an improvised substitute. Per the skill rules:
- "If a child issue explicitly lists a fallback verification command and that fallback passes, say that the fallback was allowed by the issue itself."

Verification for #7101 is satisfied. The fallback was allowed because the child issue explicitly documented it.

## Outcome

- #7101 verification is complete: fallback test command passed.
- The child issue is ready for review closeout.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Proceed with the wave review phase for any affected files, then close #7101 once review is clear.