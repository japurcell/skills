---
name: ingest-source
description: Ingest all blocking source summaries in one run and clear pending manifest entries.
---

# /ingest-source

Process every blocking source in the manifest in one run.

## Use when

- `.agents/memory/sources/source-ingest-manifest.json` contains `needs_summary` or `stale` entries.
- The agent must clear pending source summaries before doing normal work.

## Workflow

1. Read the raw source and its matching summary in `.agents/memory/sources/`.
2. Confirm the source content is readable enough to verify findings.
3. Update the summary executive summary and key findings with only verified facts.
4. Weave durable facts into the appropriate `.agents/memory/*` or scoped `.agents/instructions/*` file.
5. Register the source in `.agents/memory/INDEX.md` under `Ingested Sources`.
6. Append an `integrate` record to `.agents/memory/LOG.md`.
7. Complete the summary checklist.
8. Run `update-agent-docs`.

## Blocked sources

- If the source cannot be read reliably, stop and mark the task blocked.
- Do not fabricate findings.
- Do not change the executive summary or findings.
- Do not check integration boxes.
- Do not append an `integrate` record.

## Guardrails

- Preserve raw source files.
- Do not silently replace an existing summary.
- Process all blocking entries in one run.
