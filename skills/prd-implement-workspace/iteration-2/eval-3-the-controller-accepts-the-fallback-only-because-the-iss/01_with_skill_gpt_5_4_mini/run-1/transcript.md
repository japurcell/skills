Controller intake:
- Verified the child issue explicitly allows `yarn rw test api/src/functions/users/users.test.ts` if `pnpm` / Redwood CLI is unavailable.
- Verification subagent reported `pnpm: command not found`, then ran the fallback `yarn rw test api/src/functions/users/users.test.ts` successfully.

Controller checkpoint:
- Accepted the fallback because it was explicitly listed in the issue.
- Closed #7101 / marked it ready to close after verification passed.
- Updated the parent task-graph line for #7101 from `[ ]` to `[x]`.
- Left the parent PRD issue open.
