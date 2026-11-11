# Todos

<!-- next-id: 33 -->
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

28. [ ] agent self-reported inefficient orchestration and provided these skill improvement suggestions. Strengthen `execplan-implement` `SKILL.md` enforcement: require persistent integration coordinators to run in background mode and verify follow-up messaging; require intermediate acceptance-worker evidence checkpoints and split oversized validation matrices into bounded independent tasks; run full configuration matrices on the final source revision unless configurations or milestone gates require earlier runs, reusing evidence by source/configuration/toolchain identity; mechanically validate commit messages against `references/message.md` for required sections, real newlines, and trailers before committing.

29. [ ] Investigate and fix `execplan-implement` blocking before implementation when router-selected subagent model controls are unavailable under session permissions. Reported blocker: "Required workflow needs router-selected subagent model controls unavailable under this session's permissions. Your requested workflow required model-controlled subagents, but I lacked authorization to select their models." Identify the requirement causing the block and make the workflow honor available permissions without requiring unauthorized model selection. `delegate-to-subagents` does not cause this issue. Reported by copilot cli agent.

30. [ ] Create a council skill. References: [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/council/SKILL.md), [t3dotgg/tstack](https://github.com/t3dotgg/tstack/blob/main/skills/council/SKILL.md).

31. [ ] Make coding-agent attribution automatic in the published `commit` skill when the agent contributed to the changes.

    **Problem and intended result:** A Codex-assisted commit omitted attribution because the user supplied no `co_author` input. Missing input must not mean opting out. A trailer is a final commit-message line in the form `Co-authored-by: Name <email>`; it does not replace Git's author name or email. After this change, a normal request to commit work that Codex or Copilot helped produce should include exactly one verified trailer for the contributing agent without asking the user to identify that agent.

    **Behavior to implement:** Treat changes produced or edited by the current agent in the session as evidence of contribution. Merely running Git for somebody else's changes is not contribution. Explicit user instructions, including an attribution opt-out or an explicit `co_author` identity, take precedence. Otherwise, apply documented repository attribution rules; if neither supplies a different rule, use the contributing agent's verified default identity. Preserve other established contributors and deduplicate identical trailers. Never substitute Copilot's identity for Codex or assume every supported agent is Codex.

    **Step 1 - establish the identities:** Verify Codex's attribution name and email using official OpenAI documentation, official Codex source, or attribution metadata supplied by the host. Verify Copilot's attribution name and email using official GitHub documentation, official Copilot source, or host-supplied attribution metadata. Keep both exact identities and their sources ready to document in step 3. Do not invent an email from the product name. If no identity can be verified, report that prerequisite explicitly; do not present the default-attribution implementation as complete. This verification is part of the task, not knowledge the implementer is expected to bring.

    **Step 2 - reproduce and write failing checks:** Before editing the skill or validator, save an immutable snapshot of the current bundle and reproduce the missing-trailer behavior in a disposable repository. Update `skills/default/commit/evals/test_validate_message.py` for required, missing, duplicate, unlisted, and absent-by-design trailers. Add behavioral scenarios to `skills/default/commit/evals/evals.json` and extend `skills/default/commit/evals/grade_benchmark.py`, its fixtures, and `skills/default/commit/evals/test_grade_benchmark.py` as needed. Add separate Codex and Copilot scenarios. Each must establish that the corresponding agent contributed, then ask only for a normal commit: do not tell the evaluated agent to add a trailer or supply `co_author`, because discovering that default is what the test must measure. Run the Copilot scenario using the actual Copilot CLI and the candidate skill snapshot in a disposable repository; retain its transcript, validator invocation, and resulting commit message as evidence. Inspect the actual Git commit message and validator invocation. Also cover an explicit identity override, explicit opt-out, repository policy, no agent contribution, and an already-present matching trailer. Keep unrelated existing checks intact. Work one behavior at a time through steps 2-4: observe its failing check before implementing the change, then make that check pass.

    **Step 3 - update the instructions:** Edit `skills/default/commit/SKILL.md` under Inputs and step 7, and `skills/default/commit/references/message.md` under trailer rules, including the verified default identities and supporting sources from step 1. Replace the unconditional statement that attribution is optional with the behavior above. State how the agent resolves the identity before writing the message, how user and repository overrides apply, and which identity is passed to the validator. Preserve all unrelated scope, staging, issue-closing, message-format, commit-count, and push rules. Do not change Git author configuration, installed skill copies, or existing commits.

    **Step 4 - enforce the resolved identity:** In `skills/default/commit/scripts/validate_message.py`, make each identity supplied through the existing repeatable `--co-author 'Name <email>'` option both allowed and required exactly once. A missing expected trailer, duplicate trailer, or unlisted identity must fail validation. With no `--co-author` options, a message without attribution remains valid for opt-out, repository-policy, or no-contribution cases. The skill resolves the current agent and policy; the Python validator must not guess them from its environment or require Codex on every invocation.

    **Step 5 - verify:** From the repository root, run `rtk proxy python3 skills/default/commit/evals/test_validate_message.py`, `rtk proxy python3 skills/default/commit/evals/test_grade_benchmark.py`, and `rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/commit`. Follow `skills/default/commit/evals/README.md` for disposable repositories and observed evaluation evidence. Compare the new attribution scenarios against an immutable pre-change skill snapshot in a fresh `skills/default/commit-workspace/iteration-N/`; retain original failed runs. Run both the candidate and baseline Copilot cases through Copilot, recording the Copilot version, selected model, and actual results. If Copilot cannot run, report the blocker and leave Copilot acceptance unmet. Update the evaluation README if setup or evidence requirements change. Never use the working repository for evaluation commits or push fixture commits.

    **Done when:** A normal Codex-assisted commit with omitted `co_author` produces exactly one verified Codex trailer; a normal Copilot-assisted commit with omitted `co_author` produces exactly one verified Copilot trailer, demonstrated by an evaluation run using Copilot; explicit user and repository overrides work; commits without agent contribution gain no invented attribution; missing expected trailers fail validation; Git author identity is unchanged; the focused checks pass; and the behavioral comparison records actual committed messages, observed results, and any remaining limitations.

32. [ ] Update the published `commit` skill to require the committing LLM's model name and reasoning effort in commit messages. Verify with actual Codex and Copilot CLI evaluation runs covering commits made through each role's own commit workflow: Codex main agent, Codex subagent, Copilot main agent, and Copilot subagent. In each scenario, establish the agent's contribution, have that same agent perform a normal commit without prompting it to add model or effort metadata, and inspect the resulting Git commit message. Confirm it includes the actual observed model name and reasoning effort for the committing agent. Record CLI versions, selected models, selected reasoning efforts, transcripts, and actual committed messages. Do not infer metadata from host defaults; use observed session metadata. Before implementation, decide and document the message representation, how to handle unavailable model or reasoning-effort metadata, and how attribution applies when multiple agents contribute. Preserve existing commit-skill behavior and evaluate against its published source.
