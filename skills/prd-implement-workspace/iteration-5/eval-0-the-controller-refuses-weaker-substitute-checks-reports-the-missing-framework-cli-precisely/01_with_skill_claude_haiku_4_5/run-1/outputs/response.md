## Verification Blocked: Missing Required CLI

**Issue #5101 cannot close.** The required verification command `pnpm exec expo-router verify` cannot run because the `expo-router` CLI is unavailable in this environment.

### Why the substitution is rejected

Your subagent proposed using manual code inspection + `pnpm exec tsc --noEmit` instead. I cannot accept that substitution because:

1. **Strength downgrade**: The required verification command `pnpm exec expo-router verify` is a framework-native verification step. It validates tenant-scoped route guard behavior specific to Expo Router, not just type-checking.
2. **Policy constraint (rule 3, Verification section)**: The skill explicitly forbids replacing framework-native verification with static analysis, code inspection, or generic type-check-only checks unless the child issue itself lists those as acceptable fallbacks.
3. **Acceptance risk**: TSC type-checking and manual inspection cannot validate that the route guard correctly scopes to tenants at runtime or that Expo Router's routing behavior is correct.

### Outcome

- **Child issue #5101**: Remains open. Implementation is complete, review passed, but verification blocked.
- **Parent task-graph line**: Stays `[ ] W2 - #5101 Add tenant-scoped route guard - AFK - blocked by #5099` (unchecked).
- **Next step**: You need either:
  - Install `expo-router` CLI in the current environment, or
  - Update the child issue's Verification section to explicitly list an acceptable fallback, or
  - Move this task to an environment where the required CLI is available

I will not proceed to the next wave or any other new work until this verification blocker is resolved.
