The orchestrator must pass the following to `self-improve`:
- The aggregated reusable learnings extracted from the progress file.
- Instructions to update the nearby `AGENTS.md` (or nearby auth docs, as noted by the reviewer) with these findings.

The orchestrator must mine the following progress-file sections:
- The `**Learnings for future iterations:**` blocks from all subagent and orchestrator entries (including `Patterns discovered`, `Gotchas encountered`, and `Useful context`).
- The `## Codebase Patterns` section at the top of the file.

The orchestrator must preserve the following kinds of reusable learnings:
- Module conventions.
- Non-obvious gotchas.
- Important file relationships.
- Testing expectations.
- Config or environment requirements.
(Story-specific notes must be excluded.)
