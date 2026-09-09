# Source Summaries

Load this branch only for `.agents/memory/sources/**/*.summary.md`.

Every summary uses `type: Source Summary`, a routing-oriented non-empty `description`, and exactly one `sources` entry with a `resource` that file-relatively resolves to its immutable raw source in `.agents/sources/`.

An unresolved scaffold is a real draft: retain `status: draft` with its pending description and source resource. A completed summary removes `draft` and omits `status`, using the stable default. It does not carry the legacy `status: verified` claim. Do not alter raw sources, source-ingest manifest freshness/orphan state, or summary body prose unless the authorized task requires it.

```yaml
---
type: Source Summary
description: Pending routing guidance for the raw source
sources:
  - resource: ../../sources/example.md
status: draft
---
```

When adding this metadata above an existing or supplied summary body, do not insert an additional blank line after the closing delimiter. Preserve any existing leading blank line only when it is already part of the body.
