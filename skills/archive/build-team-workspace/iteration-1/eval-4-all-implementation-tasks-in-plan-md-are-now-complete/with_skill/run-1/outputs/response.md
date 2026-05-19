I’ll read the specified local skill snapshot and answer from that source only.

● skill(addy-using-agent-skills)

● Read SKILL.md
  │ skills/build-team-workspace/skill-snapshot-current/SKILL.md
  └ 128 lines read

Post-implementation build-team does **not** stop when implementation tasks are complete. It builds `$review_scope_files`, then runs exactly one simplification phase and one review phase before handoff.

**Review scope:** include `src/api/issues.ts`, `src/api/issues.test.ts`, and `src/api/router.ts`. Exclude `src/old.ts` because deleted paths are filtered out. Deduplicate and keep paths repo-relative.

Then:

1. Add a **Code Simplification** task to `plan.md` with that full scope, dispatch a code-simplifier over the files, mark complete only after `DONE`, save, and re-read `plan.md`.
2. Add a **Code Review** task to `plan.md` with the same scope, dispatch a code-reviewer, and handle status.
3. If review reports `DONE_WITH_FINDINGS` for `src/api/router.ts`, do **not** patch inline and do **not** mark Code Review complete. Re-open the affected `plan.md` task, send the finding plus `src/api/router.ts` and original task context to a fresh implementer, add any newly changed files to `$review_scope_files`, return to simplification for the affected files, then repeat code review.
4. Leave all repository changes uncommitted, and invoke `self-improve` only if there are durable reusable lessons.

