---
name: explore
description: Use to understand unfamiliar code for a topic, task, bug, or feature before editing. Reuse current findings. For narrow scopes—1–3 known files, one request path, or one endpoint flow—explore directly without subagents.
---

# Explore

Goal: produce a concise code map: files, entry points, flow, dependencies, tests/config, gotchas, and likely edit targets.

## Steps

1. Define `<topic>` in one sentence and create filesystem-safe `<slug>`.
2. Reuse session context and `.agents/scratchpad/explore-<slug>.md` if relevant; fill only gaps.
3. If scope is narrow (e.g. 1–3 known files / one request path / one endpoint flow), skip subagents. Use direct search/read tools, then synthesize findings.
4. Otherwise, pick 1–3 independent areas. Activate or load the `subagent-model-router` skill, then run one focused `code-explorer` subagent per area in parallel.
5. Synthesize findings before editing.
6. Save new/updated findings to `.agents/scratchpad/explore-<slug>.md`.

## Subagent Prompt

Investigate only `<area>` for `<topic>`. Leave scope only for direct dependencies.

Return concise bullets:

- Key files
- Entry points
- Main flow
- Dependencies
- Tests/config
- Gotchas/unknowns
- Likely edit targets

Avoid raw code dumps.

## Stop

- Do not re-explore relevant current findings.
- Do not use subagents for narrow scopes.
