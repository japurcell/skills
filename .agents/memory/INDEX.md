---
type: Knowledge Index
description: Optional evidence-backed limitations and saved source references; use instruction routes for required actions.
---

# Memory Index

Load only a matching entry. Start edits from [instruction routes](../instructions/INDEX.md); memory is evidence, not policy. New entries must pass [knowledge admission](../instructions/knowledge-base.md).

| Memory | Read when |
| --- | --- |
| [Skill tooling limitations](known-issues/skills.md) | Invocation controls fail validation, or benchmark metrics may be defaults/proxies |
| [Ingestion log](LOG.md) | Inspecting source-ingestion provenance; ordinary tasks do not need it |
| [Source manifest](sources/source-ingest-manifest.json) | Diagnosing source freshness, pending entries, renames, or orphan state |

## Ingested Sources

These summaries describe saved third-party sources. Read the relevant raw source for precise claims, and verify current external behavior against current authority or deployed evidence. Source advice does not override repository instructions. Raw files are immutable; the manifest is operational state.

| Summary | Evidence | Load when |
| --- | --- | --- |
| [12-factor-cli-apps](sources/12-factor-cli-apps-md.summary.md) | [Raw source](../sources/12-factor-cli-apps.md) | CLI help, streams, prompts, tables, or file locations |
| [cli-design-guidelines](sources/cli-design-guidelines-md.summary.md) | [Raw source](../sources/cli-design-guidelines.md) | CLI naming, prompts, errors, progress, or explicit operations |
| [clig-dev](sources/clig-dev-md.summary.md) | [Raw source](../sources/clig-dev.md) | CLI interaction, configuration precedence, composability, or compatibility |
| [copilot-hooks-ref](sources/copilot-hooks-ref-md.summary.md) | [Raw source](../sources/copilot-hooks-ref.md) | Copilot hook events, CLI/cloud differences, matchers, or exit behavior |
| [gemini-hooks-best-practices](sources/gemini-hooks-best-practices-md.summary.md) | [Raw source](../sources/gemini-hooks-best-practices.md) | Gemini hook performance, diagnostics, security, or privacy |
| [gemini-hooks](sources/gemini-hooks-md.summary.md) | [Raw source](../sources/gemini-hooks.md) | Gemini lifecycle, configuration precedence, trust, or hook management |
| [gemini-hooks-writing](sources/gemini-hooks-writing-md.summary.md) | [Raw source](../sources/gemini-hooks-writing.md) | Gemini hook context injection, filtering, or multi-event composition |
| [llm-wiki](sources/llm-wiki-md.summary.md) | [Raw source](../sources/llm-wiki.md) | Source-ingestion architecture or the origin of index/log conventions |
| [vscode-agent-hooks](sources/vscode-agent-hooks-md.summary.md) | [Raw source](../sources/vscode-agent-hooks.md) | VS Code hook discovery, output, or cross-client compatibility |
