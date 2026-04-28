PRD execution status for #7000

Completed this run:

1. #7101 Add user retry headers — verification passed with the explicitly allowed fallback. The original `pnpm exec redwood test api/src/functions/users/users.test.ts` could not run because `pnpm` was unavailable, so the verification subagent used `yarn rw test api/src/functions/users/users.test.ts` as explicitly allowed by the child issue and it passed. #7101 is closed and the parent task-graph line was updated from `[ ]` to `[x]`.

Blocked / waiting:

1. none

Next ready work:

- none

Notes:

- The parent PRD issue remains open.
