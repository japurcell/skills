# PRD #5000 Verification Blocker: Missing Required Framework CLI

**Status:** Verification blocked; child issue #5101 remains open.

## Issue

The verification subagent reports that `pnpm exec expo-router verify` cannot run because the `expo-router` CLI is not available in the current environment. This is a required verification command listed in child issue #5101's `Verification` section.

The subagent proposes substituting manual code inspection plus `pnpm exec tsc --noEmit` instead. **This proposal is rejected.**

## Why the substitution is not acceptable

Per the prd-implement skill rules (rule 223):

> Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient.

- `pnpm exec expo-router verify` is explicitly required for this issue.
- Manual code inspection is not a substitute for framework-native verification.
- `tsc --noEmit` is a static type check, not the required `expo-router` router configuration verification.
- These proxies are weaker and do not validate the same contract.

## Blocker

**Missing dependency:** The `expo-router` CLI is unavailable. This must be resolved before verification can proceed.

**Required to proceed:**
1. Either install or enable `expo-router` in the verification environment.
2. Or, if `expo-router verify` cannot be made available, escalate to the user for decision on how to proceed.

## Current state

- Child issue #5101 **remains open**
- Parent PRD task-graph line for #5101 **remains `[ ]` unchecked**
- Wave W2 is **blocked** on this verification blocker
- Review is complete; the implementation code is ready; only the verification dependency gap is in the way

## Next step

Stop here. User action is required to either resolve the missing `expo-router` CLI availability or provide an explicit alternative verification path in the child issue's `Verification` section if a substitute is acceptable. Do not proceed to the next wave or close any other issues while this blocker stands.
