# Routing Patterns

Use when examples help.

## Reuse vs fresh routing

Reuse a route only when work class, stakes, ambiguity, agent type, touched areas, review history, and model constraints are unchanged.

| Situation | Decision |
|---|---|
| Same deterministic fixture checks across workers | Route once as `task` + Fast; reuse. |
| Similar reviews with same risk/model constraints | Route once; reuse while constraints match. |
| Tests change to architecture analysis | Fresh route. |
| Normal review changes to security audit | Fresh route; Premium. |
| Prior same-class review missed a bug | Fresh route; escalate one tier. |

## Examples

| Request | Route |
|---|---|
| Run tests and summarize failures | `task` + Fast |
| Search repo for token lifecycle code | `explore` + Fast |
| Format files or apply mechanical edits | `task` or `editor` + Fast |
| Edit connected files | `editor` + Standard |
| Debug multi-file behavior | `debugger` + Standard |
| Debug auth/cache/concurrency interaction | Standard or Premium, depending on stakes |
| Review whitespace/comment-only single-file diff | `code-reviewer` + Fast + `gpt-5-mini` |
| Review ordinary feature PR | `code-reviewer` + Standard + `gpt-5.4-mini` |
| Review backend + frontend PR | `code-reviewer` + Standard + `gpt-5.4-mini` |
| Review tests/guard logic | Standard; Premium if false-pass risk is subtle |
| Review auth callback or redirect validation | `code-reviewer` or `security-review` + Premium |
| Run security audit | `security-review` + Premium |

## Availability fallback

When a model is unavailable:

1. Keep the same tier if possible.
2. Pick the next cheapest suitable model in that tier.
3. Change tier only if no same-tier model fits or task requirements changed.
4. Mention the availability-driven fallback.

For review:

- Preserve the review floor.
- Do not fall back to `gpt-5-mini` unless the review is truly tiny, single-file, and style-only.
- If `gpt-5.3-codex` is unavailable, choose another Premium code/security reasoning model.

## Token-shape examples

| Request | Optimize for |
|---|---|
| Huge logs, short diagnosis | input cost |
| Long proposal from short prompt | output cost |
| Same repo context across subagents | cached-input cost |
| Anthropic reusable context | cache write + cached input |
