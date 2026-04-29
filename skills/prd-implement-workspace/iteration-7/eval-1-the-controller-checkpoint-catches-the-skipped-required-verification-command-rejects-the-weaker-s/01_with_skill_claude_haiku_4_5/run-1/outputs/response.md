# Controller Checkpoint: Verification Command Substitution Blocked

**Issue:** #5104 remains open.

The implementation subagent completed a clean RED → GREEN → REFACTOR cycle for "Add admin settings form" and passed the targeted test (`npm test -- settings-form.test.tsx`). However, the subagent encountered an unavailable required verification command and substituted it with weaker alternatives rather than surfacing the blocker.

## Checkpoint Finding

**Skipped Required Command:** `pnpm exec next typegen` — the subagent reported this command could not run because the `next` binary is unavailable in this checkout.

**Substitution Made:** The subagent read the generated types file manually and ran `pnpm exec eslint app/settings/form.tsx` instead.

**Problem:** The child issue #5104 specifies `pnpm exec next typegen` as a required verification step. Reading a generated file and running eslint—while useful checks—do not fulfill the contract. Static analysis and source inspection do not replace the required framework CLI validator.

## Decision

Per the skill rules on verification strength: "If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker. Report the command, the missing dependency/tool, and the stderr or setup gap. Do not mark the issue ready to close."

This checkpoint stops before review. The issue remains open and cannot advance to closure until one of the following:

1. The `next` binary becomes available and `pnpm exec next typegen` runs and passes, **or**
2. The child issue #5104 is explicitly updated to list the alternative verification steps as acceptable, **or**
3. A human decision approves the substitution after confirming the gaps pose no acceptance risk.

**No review subagents will launch.** The implementation output is held pending verification resolution.
