Created exactly the two requested deliverables:

- [hooks.md](/Users/adam/dev/skills/skills/okf-authoring-workspace/iteration-1/eval-1-metadata-only-migration/with_skill/run-1/outputs/repo/.agents/instructions/hooks.md)
- [outcome.json](/Users/adam/dev/skills/skills/okf-authoring-workspace/iteration-1/eval-1-metadata-only-migration/with_skill/run-1/outputs/outcome.json)

Outcome fields:

- `mode`: `change`
- `completion`: `complete`
- `affected`: `.agents/instructions/hooks.md` → `Agent Instruction`
- `references_loaded`: `["profile"]`
- `lint`: `./scripts/lint-okf.py`, exit `0`, `clean`
- `scoped_diff`: `clean`, containing only `.agents/instructions/hooks.md`
- `orchestration`: omitted because composition is not applicable

The 47-byte body matches the supplied body byte-for-byte. Per the fixture constraint, I did not run the linter, grader, or tests; the lint result records the coordinator’s declared verification outcome.