---
name: agent-brain
description: Use when a repository task explicitly relies on agent-brain mapped guidance or asks to use its knowledge lifecycle commands.
---

# Agent Brain

Use agent-brain to load the repository's configured guidance before relying on repository knowledge. Treat the output as information for the foreground agent to apply; CLI output alone is not proof that a host delivered or applied it.

## Procedure

1. In this source checkout, run `python3 skills/agent-brain/scripts/agent-brain.py`. Use `--help` and command-specific help to confirm available behavior and inputs.
2. For task grounding, read [the recall procedure](references/recall.md). With no task scope, `recall` returns required startup guidance and universal policy only. Once the task is known, add relevant `--path`, `--concept`, `--action`, `--dependency`, `--provider`, `--runtime`, or `--query` scope, then apply established policy before acting. Use `--all-guidance` only for deliberate library browsing. Preserve startup order, required references, and complete whole-artifact contents.
3. Follow automatic integration checkpoints for the same objective across clarification turns. Classify a checkpoint as active, awaiting_user, or ready_to_complete. Missing classification requests a compact checkpoint. For a registered learn obligation, read [learn](references/learn.md): start supplies the work package, prepare checks evidence, publish applies the exact prepared set with inverse history, and complete verifies actual results. A checked no-change skips publication. Review [the lifecycle protocol](references/lifecycle.md) for binding, child assignments, recovery, or changed inputs/context.
4. Follow [dream](references/dream.md) when a due cycle assigns a routine batch. Complete its exact reviewed dispositions and checks before session completion. Unassigned cycle coverage remains due for a later session; changed targets require current review. Unconfigured providers stay disabled; protocol fixtures prove common behavior only in disposable repositories. No native provider path is certified.
5. Use `status` and `doctor` as read-only reports of configuration, local pending work, and observed SQLite capability. Missing/corrupt expected state is unavailable and incomplete. Setup is unavailable from this CLI. Keep semantic decisions with the foreground agent; the CLI never launches a model.

## Metadata and delivery

Guidance can use the namespaced JSON comments described in [the authoring example](examples/metadata-authoring-v1.md) and [metadata schema](schemas/metadata-v1.schema.json). Stable UUIDs survive moves; defaults provide inherited fields but never an identity. Protected documents can be indexed through read-only selectors in configuration.

Treat candidate units as investigation material only. They never satisfy established policy or a mandatory startup/reference read. Check `complete`, `gaps`, and `scope_status`; an uncertain selector broadens recall and leaves an explicit scope gap. Default evidence output contains availability and source references. `--show-evidence` requests details. A whole-artifact read preserves exact source text, including metadata comments that may contain detail, and says so in its result.
