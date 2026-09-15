# Routing

## Choose the Doc Type

Use `.agents/instructions/` for required actions:

- Required workflow
- Coding rule
- Testing rule
- Tool usage rule

Use `.agents/memory/` for durable repo knowledge:

- Architecture fact
- File/layout map
- Public entry point map
- Historical reason
- Known gotcha
- Cross-file relationship
- Non-obvious behavior

If a topic needs both rules and background, use separate instruction and memory docs.

Example:

- `.agents/instructions/hooks.md`
- `.agents/memory/known-issues/hooks.md`

## Common Routes

| Change | Destination |
| --- | --- |
| Required repo-wide rule | Focused `.agents/instructions/` doc |
| Area-specific rule | Instruction doc for that area |
| Architecture, layout, or entry point | Focused memory doc; update `FILE_MAP.md` if useful |
| Repo-wide descriptive convention | `CONVENTIONS.md` or a focused memory doc |
| Repo-wide known issue | `KNOWN_ISSUES.md` |
| Area-specific known issue | `known-issues/<area>.md` |
| Required test command or process | Test instruction doc |
| Test layout, fixture, or behavior | `TESTING_STRATEGY.md` or `testing/<area>.md` |
| Compiler, analyzer, or IDE behavior | Instruction for required handling; memory for explanation |
| Memory doc added, moved, removed, or repurposed | Memory `INDEX.md` and affected links |
| Instruction doc added, moved, removed, or repurposed | Matching instruction index, if present |
| Ordinary project documentation only | No update unless agent-doc routing, links, or metadata changed |
