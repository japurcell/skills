I’ll ground the answer in the exact benchmark skill file and avoid changing or validating anything.

The manager should run the **final reviewed tracking sync** now across all active trackers: `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and the SQL todo state. They should align the same final reviewed status everywhere, including any task that was reopened, fixed, and re-closed, and record any additional verification actually performed during review.

The manager should **not create or publish anything**: no commit, PR, tag, new tracker, or artifact. Leave the changes **uncommitted and local**.
