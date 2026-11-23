# Todos

<!-- next-id: 42 -->
<!-- Merge collision: origin/main keeps IDs 33/34; topic IDs 33/34 from c7a6261a are now 36/37. -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.

40. [ ] Update `delegate-to-subagents` and `execplan-implement` to skip `subagent-model-router` when the user specifies a model for an assignment. Dispatch with that model directly. Keep routing assignments for which the user specifies only a tier or leaves model selection open.

41. [ ] Example self-updating AGENTS.md file: "## Maintaining this file

- Keep durable project requirements and reusable lessons here; active status and next authorization belong in `handoff.md`.
- Rewrite or prune rather than append duplicates. Link authoritative files or commands instead of copying their facts; keep entries concise and useful across sessions."

## Investigations

2. [ ] Investigate a pre-commit hook that runs all tests and checks Markdown syntax and local links. Select existing Markdown/link tooling, and assess changed-file scoping and feedback runtime against the original full-test requirement before proposing a narrower alternative.


4. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle), [What it takes to build a software factory](https://youtu.be/x-PK3yx_MJg?si=85-cMsMY9a_LbDXS). Supporting content lives in `brain/plans/software-factory`.

17. [ ] Clean up skills: remove `addy-*` skills and assess minimal bespoke replacements to reduce context usage.

19. [ ] Pull in the unslop skill from [poteto/noodle](https://github.com/poteto/noodle/tree/main/.agents/skills/unslop).


23. [ ] Investigate Cursor’s formal verification skill: [create-formal-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-formal-verification-skill/SKILL.md).

28. [ ] agent self-reported inefficient orchestration and provided these skill improvement suggestions. Strengthen `execplan-implement` `SKILL.md` enforcement: require persistent integration coordinators to run in background mode and verify follow-up messaging; require intermediate acceptance-worker evidence checkpoints and split oversized validation matrices into bounded independent tasks; run full configuration matrices on the final source revision unless configurations or milestone gates require earlier runs, reusing evidence by source/configuration/toolchain identity; mechanically validate commit messages against `references/message.md` for required sections, real newlines, and trailers before committing.

30. [ ] Create a council skill. References: [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/council/SKILL.md), [t3dotgg/tstack](https://github.com/t3dotgg/tstack/blob/main/skills/council/SKILL.md).

32. [ ] Update the published `commit` skill to require the committing LLM's model name and reasoning effort in commit messages. Verify with actual Codex and Copilot CLI evaluation runs covering commits made through each role's own commit workflow: Codex main agent, Codex subagent, Copilot main agent, and Copilot subagent. In each scenario, establish the agent's contribution, have that same agent perform a normal commit without prompting it to add model or effort metadata, and inspect the resulting Git commit message. Confirm it includes the actual observed model name and reasoning effort for the committing agent. Record CLI versions, selected models, selected reasoning efforts, transcripts, and actual committed messages. Do not infer metadata from host defaults; use observed session metadata. Before implementation, decide and document the message representation, how to handle unavailable model or reasoning-effort metadata, and how attribution applies when multiple agents contribute. Preserve existing commit-skill behavior and evaluate against its published source.

41. [ ] Add Microsoft Work IQ integration to the `accomplishment-report` skill. Reference: [microsoft/work-iq](https://github.com/microsoft/work-iq).
