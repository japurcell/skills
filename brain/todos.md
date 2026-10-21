# Todos

<!-- next-id: 10 -->
<!-- completed todos live in archive/todos.md -->
<!-- completed plans live in archive/plans/ -->

## Repository maintenance

1. [ ] Replace the legacy agent knowledge system with brain notes and portable maintenance hooks [[plans/01-brain-migration/ExecPlan]]
8. [ ] Set an acceptable maximum feedback runtime for `.github/workflows/hooks-posix.yml`, then refactor the workflow to meet it while preserving required coverage; some runs currently take nearly 30 minutes.
9. [ ] Convert all `[[<filename>]]` wikilinks to standard Markdown links with valid relative file destinations; update link-generation code and authoring guidance so files remain compatible with standard Markdown tools.

## Investigations

2. [ ] Investigate a changed-file pre-commit check for Markdown syntax and local links; select an existing checker before adding tooling.
3. [ ] Evaluate correction capture, deduplication, provenance, staleness, and replay for agent memory; distinguish measured improvements from the [source video's proposals](https://youtu.be/mAKUL12h1n8?si=jo_E1lSoFM9btLqY).
4. [ ] Define one bounded prototype for configurable agent workflows, multi-harness routing, live/history inspection, and evidence-based self-improvement. References: [Shopify process](https://youtu.be/bBMp5tLxShQ?si=qgFTxY2TBbCXjlvd), [validation pipeline](https://github.com/kunchenguid/no-mistakes), [software factory UI](https://github.com/disler/super-simple-software-factory), [Noodle](https://github.com/poteto/noodle).
5. [ ] Investigate whether nested AGENTS.md maps complement the root brain index for local context; evaluate [harness-engineering](https://github.com/lopopolo/harness-engineering).
6. [ ] Audit skills against compatible [official skill guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), focusing on OpenAI usage, progressive disclosure, reference navigation, and feedback loops.
7. [ ] Reproduce scanner capacity/recovery behavior on current code before considering budget changes; historical incomplete-scan incidents are not current defect proof. [[codebase/secret-scanner]]
