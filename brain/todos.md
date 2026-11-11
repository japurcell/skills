# Todos

<!-- next-id: 30 -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.


## Investigations


2. [ ] Investigate a pre-commit hook that runs all tests and checks Markdown syntax and local links. Select existing Markdown/link tooling, and assess changed-file scoping and feedback runtime against the original full-test requirement before proposing a narrower alternative.


4. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle), [What it takes to build a software factory](https://youtu.be/x-PK3yx_MJg?si=85-cMsMY9a_LbDXS). Supporting content lives in `brain/plans/software-factory`.


7. [ ] Reproduce scanner capacity/recovery behavior on current code before considering budget changes; historical incomplete-scan incidents are not current defect proof. [codebase/secret-scanner](codebase/secret-scanner.md)



17. [ ] Clean up skills: remove `addy-*` skills and assess minimal bespoke replacements to reduce context usage.

18. [ ] Incorporate relevant brain principles into code review skills.

19. [ ] Pull in the unslop skill from [poteto/noodle](https://github.com/poteto/noodle/tree/main/.agents/skills/unslop).


23. [ ] Investigate Cursor’s formal verification skill: [create-formal-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-formal-verification-skill/SKILL.md).

28. [ ] Strengthen `execplan-implement` `SKILL.md` enforcement: require persistent integration coordinators to run in background mode and verify follow-up messaging; require intermediate acceptance-worker evidence checkpoints and split oversized validation matrices into bounded independent tasks; run full configuration matrices on the final source revision unless configurations or milestone gates require earlier runs, reusing evidence by source/configuration/toolchain identity; mechanically validate commit messages against `references/message.md` for required sections, real newlines, and trailers before committing.

29. [ ] Investigate and fix `execplan-implement` blocking before implementation when router-selected subagent model controls are unavailable under session permissions. Reported blocker: "Required workflow needs router-selected subagent model controls unavailable under this session's permissions. Your requested workflow required model-controlled subagents, but I lacked authorization to select their models." Identify the requirement causing the block and make the workflow honor available permissions without requiring unauthorized model selection. `delegate-to-subagents` does not cause this issue.
