# Place guidance by scope and task

Use while designing new guidance or reorganizing existing files.

## Choose one owner

| Guidance | Owner |
| --- | --- |
| Rules needed across the repository | Root AGENTS.md |
| Rules needed throughout one package or directory scope | That scope's nested AGENTS.md |
| Conditional procedure, domain concept, or detailed examples | Existing authoritative doc, or a focused reference with a task-triggered link |
| Fact readily obtained from a manifest or directory listing | Keep in its existing source unless a short pointer prevents a known mistake |
| Enforceable invariant | Existing test, lint, type, or configuration; document how to use it instead of copying its implementation |

A shared API contract may belong at a common ancestor or in a shared reference even if its implementation lives in one package. Scope is determined by the consumers who need the rule. Moving a cross-package constraint into just one package would hide it from the others.

## Build explicit routes

For a repository with a web app and a service, an appropriate layout might be:

```text
AGENTS.md
apps/web/AGENTS.md
services/api/AGENTS.md
docs/api-contract.md
docs/database-changes.md
```

Example root pointer:

```markdown
For changes to the public API or its consumers, read [API contract](docs/api-contract.md) before editing.
```

Example service pointer:

```markdown
For schema or migration changes, read [Database changes](../../docs/database-changes.md) before editing.
```

Each nested file contains only its scoped additions and intentional exceptions. The root can point to relevant nested files with path conditions, making them discoverable even when the host does not automatically load descendants. Never tell every task to load every nested guide.

Use target-owned names and paths. The example is not a mandatory layout. Reuse a suitable existing doc instead of introducing a competing `docs/agents/` tree. Prefer a direct link to the needed section or document; verify heading anchors after edits. Existing external docs may supplement local guidance, but required project policy must remain discoverable without reconstructing it from an external article.

## Preserve the effective contract

Root rules normally apply to descendants; a more specific rule may intentionally vary within its scope. Do not flatten scoped exceptions into universal rules or assume an entire parent file becomes irrelevant because one child rule differs. Respect the active host's actual instruction hierarchy and explicit user directions. Where host behavior is unknown, make routes explicit and report that automatic loading is unverified.

A tiny project may need only one short root file. A mixed-language project with separate build and validation paths normally needs nested guides. A cross-cutting conditional procedure may need a reference without any new nested guide. Choose the smallest layout that exposes every required rule at the point it matters.
