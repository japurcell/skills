---
type: Knowledge Index
description: Index and loading map for all .agents/memory/ knowledge-base files
---

# Memory Index

This is the loading map for the agent knowledge base under `.agents/memory/`. **Read this file first** when starting any task. Load other files **on demand** — and read only the area-scoped **instruction file** for the area you're working in (see below), not all of them. This keeps context small.

## Repo-wide files (load as the task needs)

| File                       | Purpose                                                                 | When to load                                  |
| -------------------------- | ----------------------------------------------------------------------- | --------------------------------------------- |
| **[INDEX.md](INDEX.md)** (this file) | Discovery map for the knowledge base                                    | Always — read first                           |
| **[ARCHITECTURE.md](ARCHITECTURE.md)**      | Top-level repo structure, install flows, and documentation boundaries   | Load when task needs repo structure, install flows, or docs boundaries |
| **[CONVENTIONS.md](CONVENTIONS.md)**       | Repo-wide formatting and agent-workspace boundaries                     | When writing or reviewing code                |
| **[FILE_MAP.md](FILE_MAP.md)**          | Top-level map (one line per area) + layer pointers                      | When deciding which area/layer to work in     |
| **[API_MAP.md](API_MAP.md)**           | Public repository validation and provider-adapter entry points          | When changing OKF lint CLI or hook envelopes  |
| **[LOG.md](LOG.md)**               | Append-only source-ingestion activity log                               | When reviewing ingested source history        |
| **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)**      | Repo-wide / cross-cutting quirks & workarounds                          | Code review or cross-cutting troubleshooting  |
| **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)**  | Test layout, shared authoring conventions & how to run tests            | When writing tests or debugging test failures |

## Layer-specific knowledge

Per-area directory detail, key files/APIs, and working rules live in the
matching **instruction files**. **Known issues**, **testing**, and
**architectural decision records (ADRs)** are broken out into dedicated memory
files so you load only what the task needs. Read the row for the area you're
working in:

| Area | Instruction file (rules + dir detail) | Known issues | Testing | ADRs / Decisions |
| --- | --- | --- | --- | --- |
| `AGENTS.md`, `README.md` | [repo](../instructions/repo.md) | empty | empty | empty |
| General provider hooks | [hooks](../instructions/hooks.md) | [hooks](known-issues/hooks.md) | [hooks](testing/hooks.md) | [hooks](adrs/hooks.md) |
| Hook source auto-ingest | [auto-ingest](../instructions/hooks-auto-ingest.md) | [auto-ingest](known-issues/hooks-auto-ingest.md) | [auto-ingest](testing/hooks-auto-ingest.md) | [hooks](adrs/hooks.md) |
| Hook observability and trace storage | [observability](../instructions/hooks-observability.md) | [observability](known-issues/hooks-observability.md) | [observability](testing/hooks-observability.md) | [hooks](adrs/hooks.md) |
| `skills/` | [skills](../instructions/skills.md) | [skills](known-issues/skills.md) | [skills](testing/skills.md) | empty |
| `agents/` | [agents](../instructions/agents.md) | empty | empty | empty |
| `scripts/` (shell) | [scripts](../instructions/scripts.md) | [scripts](known-issues/scripts.md) | [scripts](testing/scripts.md) | empty |
| `scripts/*.ps1` (PowerShell) | [PowerShell](../instructions/powershell.md) | [PowerShell](known-issues/powershell.md) | [PowerShell](testing/powershell.md) | empty |

The repo-wide memory files above hold only cross-cutting content and point into
these layer files for specifics.

## Ingested Sources

Use this area to register scaffolded source summaries and keep source-specific knowledge discoverable.
Load `.agents/memory/LOG.md` first, then the matching summary in `.agents/memory/sources/`.
When a user asks for exact behavior, an authoritative answer, or work on a topic with a matching raw source, read the raw source after the summary. Summaries route investigation and preserve durable findings, but raw sources are the authority for precise behavior, schemas, command output, and edge cases.
The committed manifest `.agents/memory/sources/source-ingest-manifest.json` tracks source fingerprints plus stale or orphan summary state for auto-ingest hooks and pending-ingest gating.
Raw files under `.agents/sources/` are immutable source inputs; summaries plus the wider `.agents/memory/` and `.agents/instructions/` corpus are the compiled knowledge layer.
Keep chronological integration history grep-friendly by prefixing log entries as `## [YYYY-MM-DD] action | subject`.

| Source summary path | Raw source path | When to load |
| ----------------------------- | ------------------- | ---------------------------------------------------------- |
| `.agents/memory/sources/12-factor-cli-apps-md.summary.md` | `.agents/sources/12-factor-cli-apps.md` | When working on CLI UX guidance, help text, stream discipline, prompts, tables, or XDG path conventions. |
| `.agents/memory/sources/cli-design-guidelines-md.summary.md` | `.agents/sources/cli-design-guidelines.md` | When working on concise CLI UX defaults such as naming, prompts, errors, progress, or expressive flags. |
| `.agents/memory/sources/clig-dev-md.summary.md` | `.agents/sources/clig-dev.md` | When working on broader CLI interaction design, configuration precedence, output conventions, or future-proofing decisions. |
| `.agents/memory/sources/copilot-hooks-ref-md.summary.md` | `.agents/sources/copilot-hooks-ref.md` | When changing Copilot hook events, cross-surface behavior, matcher semantics, or exit-code handling. |
| `.agents/memory/sources/gemini-hooks-best-practices-md.summary.md` | `.agents/sources/gemini-hooks-best-practices.md` | When changing Gemini hook performance, debugging, threat-model, privacy, or hardening guidance. |
| `.agents/memory/sources/gemini-hooks-writing-md.summary.md` | `.agents/sources/gemini-hooks-writing.md` | When changing Gemini hook authoring patterns, tool filtering, or multi-event workflow composition. |
| `.agents/memory/sources/gemini-hooks-md.summary.md` | `.agents/sources/gemini-hooks.md` | When changing Gemini hook event coverage, config precedence, trust behavior, or `/hooks` operations. |
| `.agents/memory/sources/llm-wiki-md.summary.md` | `.agents/sources/llm-wiki.md` | When changing source-ingest workflow, wiki/log/index structure, or compiled-knowledge maintenance patterns. |
| `.agents/memory/sources/vscode-agent-hooks-md.summary.md` | `.agents/sources/vscode-agent-hooks.md` | When changing VS Code hook compatibility, hook locations, or agent-scoped hook behavior. |
| `.agents/memory/sources/source-ingest-manifest.json` | `.agents/sources/*` | When debugging auto-ingest hook state, stale-summary detection, or pending-ingest gating. |
| [LOG.md](LOG.md) | N/A | When reviewing scaffold and integrate history. |

## Related Existing Docs

This repo predates this knowledge base and still keeps companion docs that the
memory files cross-reference:

- [AGENTS.md](../../AGENTS.md) — top-level quickstart and loading contract.
- [README.md](../../README.md) — repo overview and installation entry point.
- [`docs/ideas.md`](../../docs/ideas.md) — lightweight inbox for ideas that are not ready for research or planning.
- [`.agents/instructions/repo.md`](../instructions/repo.md) and its siblings — canonical area-scoped workflow rules and conventions.
- [`.agents/skills/okf-authoring/SKILL.md`](../skills/okf-authoring/SKILL.md) and its siblings — task-specific repository workflows.

## Conventions

- **Treat memory files as authoritative for repo conventions, but cross-check against actual code** — they can drift.
- **Prefer small focused files over large monolithic ones.** Keep layer-specific detail in the matching `.agents/instructions/<area>.md`, not in the repo-wide memory files.
- **New files should have minimal OKF frontmatter** with the path-derived `type` and a routing-oriented `description`; source summaries also follow their manifest-backed provenance and lifecycle rules.

## Maintenance

When you change the knowledge base, keep this index in sync:

- Keep the root `AGENTS.md` scope list aligned with this table.
- **Added, removed, or renamed a memory file?** → Update this index.
- **Significantly changed a file's purpose or scope?** → Update its row in the loading map.
- **Added layer-specific knowledge?** → Known issues go in `known-issues/<area>.md`; test conventions go in `testing/<area>.md`; directory detail, key files/APIs, and coding conventions go in the matching `.agents/instructions/<area>.md`; architectural decision records go in `adrs/<area>.md`. Keep it out of the repo-wide memory files.
