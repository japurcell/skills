---
coverage: Index and loading map for all .agents/memory/ knowledge-base files
---

# Memory Index

This is the loading map for the agent knowledge base under `.agents/memory/`. **Read this file first** when starting any task. Load other files **on demand** — and read only the area-scoped **instruction file** for the area you're working in (see below), not all of them. This keeps context small.

## Repo-wide files (load as the task needs)

| File                       | Purpose                                                                 | When to load                                  |
| -------------------------- | ----------------------------------------------------------------------- | --------------------------------------------- |
| **`INDEX.md`** (this file) | Discovery map for the knowledge base                                    | Always — read first                           |
| **`ARCHITECTURE.md`**      | Top-level repo structure, install flows, and documentation boundaries   | Always for non-trivial tasks                  |
| **`CONVENTIONS.md`**       | Repo-wide code style, naming, immutability, resource & public-API rules | When writing or reviewing code                |
| **`FILE_MAP.md`**          | Top-level map (one line per area) + layer pointers                      | When deciding which area/layer to work in     |
| **`LOG.md`**               | Append-only source-ingestion activity log                               | When reviewing ingested source history        |
| **`KNOWN_ISSUES.md`**      | Repo-wide / cross-cutting quirks & workarounds                          | Code review or cross-cutting troubleshooting  |
| **`TESTING_STRATEGY.md`**  | Test layout, shared authoring conventions & how to run tests            | When writing tests or debugging test failures |

## Layer-specific knowledge

Per-area directory detail, key files/APIs, and working rules live in the
matching **instruction files**. **Known issues**, **testing**, and
**architectural decision records (ADRs)** are broken out into dedicated memory
files so you load only what the task needs. Read the row for the area you're
working in:

| Area | Instruction file (rules + dir detail) | Known issues | Testing | ADRs / Decisions |
| --- | --- | --- | --- | --- |
| `AGENTS.md`, `README.md` | `.agents/instructions/repo.md` | empty | empty | empty |
| `.copilot/hooks`, `.gemini/hooks` | `.agents/instructions/hooks.md` | `known-issues/hooks.md` | `testing/hooks.md` | `adrs/hooks.md` |
| `skills/` | `.agents/instructions/skills.md` | `known-issues/skills.md` | `testing/skills.md` | empty |
| `agents/` | `.agents/instructions/agents.md` | empty | empty | empty |
| `scripts/` | `.agents/instructions/scripts.md` | empty | `testing/scripts.md` | empty |

The repo-wide memory files above hold only cross-cutting content and point into
these layer files for specifics.

## Ingested Sources

Use this area to register scaffolded source summaries and keep source-specific knowledge discoverable.
Load `.agents/memory/LOG.md` first, then the matching summary in `.agents/memory/sources/`.

| Source summary path | Raw source path | When to load |
| ----------------------------- | ------------------- | ---------------------------------------------------------- |
| `.agents/memory/sources/*.md` | `.agents/sources/*` | When working on a specific ingested source or its summary. |
| `.agents/memory/LOG.md` | N/A | When reviewing scaffold and integrate history. |

## Related Existing Docs

This repo predates this knowledge base and still keeps companion docs that the
memory files cross-reference:

- `AGENTS.md` — top-level quickstart and loading contract.
- `README.md` — repo overview and installation entry point.
- `.agents/instructions/<area>.md` — canonical area-scoped workflow rules and conventions.
- `.agents/skills/*/SKILL.md` — task-specific skills (update-agent-docs, etc.).

## Conventions

- **Treat memory files as authoritative for repo conventions, but cross-check against actual code** — they can drift.
- **Prefer small focused files over large monolithic ones.** Keep layer-specific detail in the matching `.agents/instructions/<area>.md`, not in the repo-wide memory files.
- **New files should have minimal frontmatter** with a `coverage:` field describing what the file covers.

## Maintenance

When you change the knowledge base, keep this index in sync:

- Keep the root `AGENTS.md` scope list aligned with this table.
- **Added, removed, or renamed a memory file?** → Update this index.
- **Significantly changed a file's purpose or scope?** → Update its row in the loading map.
- **Added layer-specific knowledge?** → Known issues go in `known-issues/<area>.md`; test conventions go in `testing/<area>.md`; directory detail, key files/APIs, and coding conventions go in the matching `.agents/instructions/<area>.md`; architectural decision records go in `adrs/<area>.md`. Keep it out of the repo-wide memory files.
