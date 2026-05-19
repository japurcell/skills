I’ll read the specified local skill file, then answer the eval prompt without modifying or running anything.

● skill(addy-using-agent-skills)

● Read SKILL.md
  │ skills/build-team-workspace/skill-snapshot-current/SKILL.md
  └ 128 lines read

I would run the **build-team orchestration workflow** from the existing `plan.md` without implementing inline.

1. Read `plan.md` and identify **T014: add pagination to `GET /api/issues`** as the next ready pending task.
2. Invoke `subagent-model-selection` to choose the least powerful capable implementer model/agent for T014.
3. Dispatch a **fresh implementer subagent** with:
   - the exact T014 task text
   - the relevant `plan.md` excerpt
   - the local `implementer-prompt.md` template
4. Wait for the implementer result:
   - `DONE`: update T014 as complete in `plan.md`, save it, then re-read `plan.md` and verify T014 is visibly complete.
   - `DONE_WITH_CONCERNS`: resolve the concerns before marking complete.
   - `NEEDS_CONTEXT`: provide context and re-dispatch.
   - `BLOCKED`: try better context, smaller scope, or stronger model; escalate only if still blocked.
5. Because T014 is the final pending implementation task, build `$review_scope_files` from files changed by implementers plus filtered uncommitted files, excluding deleted, ignored, and `.gitignore` paths.
6. Add and run a **Code Simplification** task in `plan.md`, dispatching code-simplifier subagents over `$review_scope_files`; wait for `DONE`, update `plan.md`, save, and re-read to verify.
7. Add and run a **Code Review** task in `plan.md`, dispatching code-reviewer subagents over `$review_scope_files`; wait for `DONE`, update `plan.md`, save, and re-read to verify.
8. If review returns `DONE_WITH_FINDINGS`, re-open the affected `plan.md` task and route the fix to a fresh implementer, then repeat simplification and review for affected files.
9. Before stopping, invoke `self-improve` only if the session produced durable reusable lessons.
10. Leave all repository changes uncommitted.

