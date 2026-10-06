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

For activated, supported agent-brain source ingestion, use the current foreground [learn procedure](../../../skills/agent-brain/references/learn.md) and its integration-issued invocation. Load this skill once for all blocking entries in the work package. Read every original and summary, verify readability, and author complete proposed summary, knowledge, index and integration-log bytes outside canonical paths. Preserve Source Summary description, resource provenance and checklist, stable knowledge identities, qualifications and compact source/revision/verification notes. Include required index/log updates within explicitly owned knowledge paths; unavailable writable ownership keeps their obligation incomplete.

Submit the exact change set and current source/summary/knowledge evidence to learn prepare before any semantic write, then publish only prepared bytes and complete through current artifact checks. The canonical scanner alone owns manifest/scaffold reconciliation and checked mechanical settlement. Raw sources remain immutable. Review renamed/removed-source orphans separately. Pre-pass qualified artifacts that already establish current source claims may receive an evidenced no-change review without invented guidance. Direct edits followed by recover cannot replace reversible publication. Source drift requires current redelivery and a fresh checked outcome. An update-agent-docs call joins this same learn obligation without recursive ingestion or another semantic pass.

For unactivated or unsupported integrations, preserve this complete legacy workflow and all mandatory documentation obligations:

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
