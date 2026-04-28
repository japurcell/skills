PRD execution status for #7000

Completed this run:

1. #7101 Add user retry headers

Blocked / waiting:

1. none

Next ready work:

- none

Notes:

- The required fallback `yarn rw test api/src/functions/users/users.test.ts` was explicitly allowed by the child issue.
- `pnpm exec redwood test api/src/functions/users/users.test.ts` could not run because `pnpm` was unavailable, so the controller accepted the fallback after it passed.
- #7101 is closed and the parent task-graph line was updated from `[ ]` to `[x]`.
