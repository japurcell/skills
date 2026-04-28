PRD execution status for #5000

Completed this run:

- none

Blocked / waiting:

1. #5101 Add tenant-scoped route guard - required verification command `pnpm exec expo-router verify` could not run because `expo-router` is not installed (`/bin/sh: expo-router: command not found`). I did not replace it with `pnpm exec tsc --noEmit`.

Next ready work:

- none

Notes:

- `pnpm test -- route-guard.test.ts` passed.
