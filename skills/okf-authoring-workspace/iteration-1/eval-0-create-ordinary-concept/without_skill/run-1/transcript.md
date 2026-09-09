User prompt: The coordinator seeds a complete valid fixture and removes the four expected target documents before its baseline snapshot. Create exactly these four files beneath `outputs/repo`: `.agents/memory/telemetry.md` with body `# Telemetry\n\nRecord durable telemetry guidance.\n`; `.agents/memory/INDEX.md` with body `# Index\n\nRoute canonical knowledge.\n`; `.agents/memory/LOG.md` with body `# Log\n\nRecord source ingestion.\n`; and `.agents/memory/adrs/retention.md` with body `# Retention\n\nKeep stable paths.\n`. Save `outputs/outcome.json` using the declared outcome schema. The coordinator applies output to its fixture and independently runs the full linter, which must exit 0.

Action: Created the four requested files with path-derived `type` metadata and non-empty `description` metadata. Preserved all requested bodies byte-for-byte.

Action: Saved the declared structured outcome with `mode: change`, `completion: complete`, profile reference evidence, clean lint status, and the four exact scoped paths.

Result: Complete.
