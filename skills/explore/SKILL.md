---
name: explore
description: Explores the codebase given a topic, task, issue, or request by spawning fast-tier codebase-exploration subagents in parallel. Use when beginning a new investigation, researching a feature or bug, mapping dependencies, or before editing unfamiliar files, provided the codebase has not already been explored for the same topic in the current session.
---

# Explore Codebase

## Workflow

1. Check prior session context and, if available, `.agents/scratchpad/explore-<topic-slug>.md`. Reuse if relevant and current; refresh only gaps.
2. Define the topic in one sentence and use a short filesystem-safe slug for `<topic-slug>`.
3. Pick 1–3 independent areas to inspect.
4. If subagents exist, run one focused explorer per area in parallel, using `code-explorer` if available; otherwise do bounded search/read directly.
5. For each area, capture: key files, entry points, main flow, dependencies, tests/config, gotchas, unknowns, likely edit targets.
6. Synthesize concise findings before editing. Save to `.agents/scratchpad/explore-<topic-slug>.md`.

## Subagent Prompt

Investigate only `<area>` for `<topic>` in `<paths>`.
Do not leave scope except to identify direct dependencies.
Return concise bullets: key files, entry points, flow, dependencies, tests/config, gotchas/unknowns, likely edit targets.
Avoid raw code dumps.

## Stop Conditions

Do not re-explore valid current findings.
Do not use this for a single known-file change.
