# Todos

<!-- next-id: 27 -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.


## Investigations


2. [ ] Investigate a pre-commit hook that runs all tests and checks Markdown syntax and local links. Select existing Markdown/link tooling, and assess changed-file scoping and feedback runtime against the original full-test requirement before proposing a narrower alternative.


2. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle), [What it takes to build a software factory](https://youtu.be/x-PK3yx_MJg?si=85-cMsMY9a_LbDXS). Supporting content lives in `brain/plans/software-factory`.


7. [ ] Reproduce scanner capacity/recovery behavior on current code before considering budget changes; historical incomplete-scan incidents are not current defect proof. [codebase/secret-scanner](codebase/secret-scanner.md)



17. [ ] Clean up skills: remove `addy-*` skills and assess minimal bespoke replacements to reduce context usage.

18. [ ] Incorporate relevant brain principles into code review skills.

19. [ ] Pull in the unslop skill from [poteto/noodle](https://github.com/poteto/noodle/tree/main/.agents/skills/unslop).


21. [ ] Add a rule to the brain skill and a template to brain-install: keep `AGENTS.md` files concise; put topic-specific procedures in focused brain reference docs, with explicit required-read links from the applicable `AGENTS.md`. "## AGENTS.md Guidelines - Keep `AGENTS.md` as the concise repository-specific entrypoint and map. Put detailed examples, formats, procedures, and rationale in focused brain notes, linked here with explicit read conditions. When updating guidance, consolidate or relocate detail rather than duplicating it in `AGENTS.md`. Preserve `## Brain` and `## End of Work Session Defined` as explicit exceptions."

23. [ ] Investigate Cursor’s formal verification skill: [create-formal-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-formal-verification-skill/SKILL.md).

9. [ ] An agent executing the 'execplan-implement' skill didn't enforce a subagent runtime limit. It suggested this improvement to the skill: "Deadlines require parent-side enforcement. Before each background assignment, record its task ID, start time, deadline, extension count, and enforcement handle. Arm a host timeout or parent-owned deadline timer before waiting.
At expiry, request a checkpoint with a bounded response deadline. Allow only one ETA-based extension, update the recorded deadline, and re-arm enforcement. Follow-up messages do not reset the extension count.
At the second expiry, stop the worker and confirm it is quiescent before assigning a replacement. Cancel timers when tasks finish. Recheck active deadlines after user interruptions. Never rely solely on deadlines written in worker prompts or completion notifications."

25. [ ] Add improvements for both `subagent-model-router` and `delegate-to-subagents` skills. For `subagent-model-router/SKILL.md`, add: "Distinguish tool support, permission to set overrides, and verified live availability. A catalog recommendation proves none of these. Report which check blocks dispatch." (Reason: I described supported settings as unavailable without testing them.) For `delegate-to-subagents/SKILL.md`, add: "Before routing, check whether host constraints allow both model and effort overrides. If not, report the specific incompatibility and do not dispatch. Do not treat a router recommendation as an explicit user selection." (Reason: This catches the conflict before routing and prevents a misleading availability claim.)

26. [ ] Improve `delegate-to-subagents/SKILL.md`: if the user explicitly overrides the router, honor their chosen model instead of enforcing the router's tier recommendation. Preserve host restrictions and deadline enforcement. Apply router constraints normally when no override is given. (Reason: Keeps the router advisory when the user explicitly takes responsibility for the choice.)
