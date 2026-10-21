# Todos

<!-- next-id: 12 -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.

## Forest Service skills

10. [ ] Create `skills/forest-service/accomplishment-report`, invoked when all work in an ExecPlan is completed. Save the report as `accomplishment-report.md` in the same directory as that plan. Produce a concise executive-level report describing the repository, completed work, and alignment with Forest Service strategic goals and priorities by activating `agency-priorities`. Estimate AI-assisted versus human-only implementation time and cost, including AI spend and human oversight, with explicit assumptions and evidence. Show estimated net savings to support decisions about spending on AI coding assistants.

## Investigations

2. [ ] Investigate a changed-file pre-commit check for Markdown syntax and local links; select an existing checker before adding tooling.
3. [ ] Evaluate correction capture, deduplication, provenance, staleness, and replay for agent memory; distinguish measured improvements from the [source video's proposals](https://youtu.be/mAKUL12h1n8?si=jo_E1lSoFM9btLqY).
4. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle).
5. [ ] Investigate whether nested AGENTS.md maps complement the root brain index for local context; evaluate [harness-engineering](https://github.com/lopopolo/harness-engineering).
6. [ ] Audit skills against compatible [official skill guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), focusing on OpenAI usage, progressive disclosure, reference navigation, and feedback loops.
7. [ ] Reproduce scanner capacity/recovery behavior on current code before considering budget changes; historical incomplete-scan incidents are not current defect proof. [codebase/secret-scanner](codebase/secret-scanner.md)
11. [ ] Research interface options for assigning and monitoring agentic work across multiple repositories before choosing a UI or implementing it. Compare a web app, a CLI, and integration with the existing Codex UI against the workflow of assigning work to a repository, following progress, and identifying work that needs attention. Document supported integration capabilities, constraints, tradeoffs, and supporting sources; recommend an initial interface and a bounded first version. Leave #4 unchanged; its workflow prototype is already in progress in another session.
