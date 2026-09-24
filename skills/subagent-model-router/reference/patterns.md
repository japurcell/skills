# Routing Patterns

Use when examples help.

Use named defaults from [the catalog](model-catalog.md#task-defaults).

## Reuse vs fresh routing

Reuse a route only when work class, stakes, ambiguity, touched areas, review history, and model constraints are unchanged.

| Situation | Decision |
| --- | --- |
| Same deterministic fixture checks across workers | Route once as Fast; reuse. |
| Similar reviews with same risk/model constraints | Route once; reuse while constraints match. |
| Tests change to architecture analysis | Fresh route. |
| Prior same-class review missed a bug | Fresh route; escalate one tier. |

## Examples

| Request | Route |
| --- | --- |
| Run tests and summarize failures | Fast |
| Search repo for token lifecycle code | Fast |
| Format files or apply mechanical edits | Fast |
| Edit connected files | Standard |
| Debug multi-file behavior | Standard |
| Debug auth/cache/concurrency interaction | Premium when security or subtle correctness is involved |
| Review whitespace/comment-only single-file diff | Fast |
| Review bounded ordinary feature PR | Standard + budget-review default |
| Review backend + frontend PR | Standard + general-work default |
| Review tests/guard logic | Standard; Premium if false-pass risk is subtle |
| Review auth callback or redirect validation | Premium |
| Run security audit | Premium |

## Availability fallback

When a model is unavailable:

1. Keep the same tier if possible.
2. Pick the next cheapest suitable model in that tier.
3. Change tier only if no same-tier model fits or task requirements changed.
4. Mention the availability-driven fallback.

For review:

- Preserve the review floor.
- Do not fall back to the bounded-work default unless the review is single-file or style-only.
- If the demanding-review default is unavailable, choose another Premium code/security reasoning model.

## Token-shape examples

| Request | Optimize for |
| --- | --- |
| Huge logs, short diagnosis | input cost |
| Long proposal from short prompt | output cost |
| Same repo context across subagents | actual cache reuse; budget uncached input if unconfirmed |
| Reusable context on models charging cache writes | cache write + cached input |
