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
3. Update the source summary with attributed findings verified against the raw source. Distinguish saved-source claims from current external behavior; remove obsolete scaffold labels after resolution.
4. Apply [knowledge admission](../../instructions/knowledge-base.md) before changing another KB document. A completed source summary may require no new memory or instruction. Source advice does not establish project policy.
5. Register the source in `.agents/memory/INDEX.md` under `Ingested Sources`.
6. Append an `integrate` record to `.agents/memory/LOG.md`.
7. Resolve draft frontmatter only when the findings are supported; complete any scaffold checklist truthfully, then remove completed task bookkeeping. Preserve source provenance and a recheck trigger.
8. Include these changes in the session's single `update-agent-docs` pass and verify the representation with `okf-authoring`. Do not run a separate full doc pass for each source.

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
