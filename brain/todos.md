# Todos

<!-- next-id: 9 -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

1. [ ] Replace the legacy agent knowledge system with brain notes and portable maintenance hooks [[plans/01-brain-migration/ExecPlan]]
8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.

## Investigations

1. [ ] Investigate a changed-file pre-commit check for Markdown syntax and local links; select an existing checker before adding tooling.
2. [ ] Evaluate correction capture, deduplication, provenance, staleness, and replay for agent memory; distinguish measured improvements from the [source video's proposals](https://youtu.be/mAKUL12h1n8?si=jo_E1lSoFM9btLqY).
3. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle).
4. [ ] Investigate whether nested AGENTS.md maps complement the root brain index for local context; evaluate [harness-engineering](https://github.com/lopopolo/harness-engineering).
5. [ ] Audit skills against compatible [official skill guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), focusing on OpenAI usage, progressive disclosure, reference navigation, and feedback loops.
6. [ ] Reproduce scanner capacity/recovery behavior on current code before considering budget changes; historical incomplete-scan incidents are not current defect proof. [[codebase/secret-scanner]]
