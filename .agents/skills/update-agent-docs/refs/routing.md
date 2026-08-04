# Routing

Update only `.agents/instructions/` and `.agents/memory/`.

Do not edit `.agents/skills/` or `.agents/sources/`.

## Choose the Doc Type

Use `.agents/instructions/` for what agents must do:

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

If a topic needs both rules and background, split it.

Example:

- `.agents/instructions/hooks.md`
- `.agents/memory/known-issues/hooks.md`

## Common Routes

| Change                                                      | Update                                                       |
| ----------------------------------------------------------- | ------------------------------------------------------------ |
| File added, moved, renamed, or layout changed               | `.agents/memory/FILE_MAP.md` if agents need the map          |
| Compiler error, IDE diagnostic, or code action changed      | Matching instruction or memory doc for that area             |
| Required repo-wide convention changed                       | Matching `.agents/instructions/` doc                         |
| Descriptive repo-wide pattern changed                       | `.agents/memory/CONVENTIONS.md` or focused memory doc        |
| Area-specific pattern changed                               | Matching focused instruction or memory doc                   |
| Repo-wide gotcha changed                                    | `.agents/memory/KNOWN_ISSUES.md`                             |
| Area-specific gotcha changed                                | `.agents/memory/known-issues/<area>.md`                      |
| Repo-wide test command/layout changed                       | `.agents/memory/TESTING_STRATEGY.md` or test instruction doc |
| Area test fixture/base/convention changed                   | `.agents/memory/testing/<area>.md` or test instruction doc   |
| Memory doc added, removed, renamed, or purpose changed      | `.agents/memory/INDEX.md` and affected links                 |
| Instruction doc added, removed, renamed, or purpose changed | Matching instruction index, if one exists                    |
| Ordinary project docs changed only                          | No agent-doc update unless links/indexes/frontmatter changed |
