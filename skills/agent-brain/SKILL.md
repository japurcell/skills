---
name: agent-brain
description: Use when a repository task explicitly relies on agent-brain mapped guidance or asks to use its knowledge lifecycle commands.
---

# Agent Brain

Use agent-brain to load the repository's configured guidance as complete artifacts. Treat the output as information for the foreground agent to apply; CLI output alone is not proof that a host delivered or applied it.

## Procedure

1. In this source checkout, run `python3 skills/agent-brain/scripts/agent-brain.py`. Use `--help` and command-specific help to confirm available behavior and inputs.
2. For task grounding, read [the recall procedure](references/recall.md), run `recall`, and apply relevant policy before acting. Preserve the configured order and complete artifact contents.
3. For a requested knowledge update or review, read [learn](references/learn.md) or [dream](references/dream.md) first. The standalone source CLI currently cannot establish registered active context, so these commands return an actionable error before reading input or changing files. Explain that the requested operation is unavailable in this context.
4. Use `status` and `doctor` only as read-only reports. Setup is unavailable from this CLI. Keep semantic decisions with the foreground agent; the CLI never launches a model.
