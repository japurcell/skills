---
name: agent-brain
description: Use when a repository task explicitly relies on agent-brain mapped guidance or asks to use its knowledge lifecycle commands.
---

# Agent Brain

Use agent-brain to load the repository's configured guidance before relying on repository knowledge. Treat the output as information for the foreground agent to apply; CLI output alone is not proof that a host delivered or applied it.

## Procedure

1. In this source checkout, run `python3 skills/agent-brain/scripts/agent-brain.py`. Use `--help` and command-specific help to confirm available behavior and inputs.
2. For task grounding, read [the recall procedure](references/recall.md). With no task scope, `recall` returns required startup guidance and universal policy only. Once the task is known, add relevant `--path`, `--concept`, `--action`, `--dependency`, `--provider`, `--runtime`, or `--query` scope, then apply established policy before acting. Use `--all-guidance` only for deliberate library browsing. Preserve startup order, required references, and complete whole-artifact contents.
3. For a requested knowledge update or review, read [learn](references/learn.md) or [dream](references/dream.md) first. The standalone source CLI currently cannot establish registered active context, so these commands return an actionable error before reading input or changing files. Explain that the requested operation is unavailable in this context.
4. Use `status` and `doctor` only as read-only reports. Setup is unavailable from this CLI. Keep semantic decisions with the foreground agent; the CLI never launches a model.

## Metadata and delivery

Guidance can use the namespaced JSON comments described in [the authoring example](examples/metadata-authoring-v1.md) and [metadata schema](schemas/metadata-v1.schema.json). Stable UUIDs survive moves; defaults provide inherited fields but never an identity. Protected documents can be indexed through read-only selectors in configuration.

Treat candidate units as investigation material only. They never satisfy established policy or a mandatory startup/reference read. Check `complete`, `gaps`, and `scope_status`; an uncertain selector broadens recall and leaves an explicit scope gap. Default evidence output contains availability and source references. `--show-evidence` requests details. A whole-artifact read preserves exact source text, including metadata comments that may contain detail, and says so in its result.
