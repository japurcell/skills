status: verified
---

# Summary for `llm-wiki.md`

## Core Details
- **Source File**: `.agents/sources/llm-wiki.md`
- **Summary File**: `.agents/memory/sources/llm-wiki-md.summary.md`
- **Stale Reason**: new file

## Executive Summary
- `LLM Wiki` describes a three-layer pattern for persistent knowledge work: immutable raw sources, an LLM-maintained markdown wiki, and a schema/instructions file that tells the model how to ingest, query, and maintain that compiled knowledge base.

## Key Findings
- The pattern's core claim is that an LLM-maintained wiki compounds knowledge over time instead of re-deriving answers from raw documents on every query.
- Raw sources are read-only inputs, the wiki is the editable compiled layer, and the schema file constrains structure, conventions, and maintenance workflows.
- Ingest should update the source summary, index, log, and any related topic pages; query outputs can also be written back into the wiki as durable pages.
- The recommended `index.md` is content-oriented, while `log.md` is chronological and benefits from a consistent `## [YYYY-MM-DD] action | subject` prefix that makes recent activity grep-friendly.
- Periodic lint passes should look for contradictions, stale claims, missing cross-links, and orphan pages before adding more tooling complexity.

## Integration Checklist
- [x] Read the raw source.
- [x] Update the executive summary with verified facts.
- [x] Update the key findings with verified facts.
- [x] Weave durable facts into `.agents/memory/*` or `.agents/instructions/*`.
- [x] Append an integrate record to `.agents/memory/LOG.md` after successful ingestion.
